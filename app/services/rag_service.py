from typing import List, Dict, Any, Optional
import json
import re
from app.services.bedrock_service import BedrockService
from app.utils.confidence import calculate_confidence
from app.utils.safety import (
    is_query_safe,
    get_safety_refusal,
    is_high_risk_agri_query,
    get_agri_safety_disclaimer,
)
from app.utils.exceptions import ExternalServiceError


class RAGService:
    def __init__(self, bedrock_service: BedrockService):
        self.bedrock_service = bedrock_service

    # -------------------------
    # Generic utilities
    # -------------------------
    def _as_list(self, value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(v).strip() for v in value if v is not None and str(v).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []

    def _safe_float(self, value: Any, default: float = 0.5) -> float:
        try:
            v = float(value)
            return round(max(0.0, min(1.0, v)), 2)
        except Exception:
            return default

    def _truncate_words(self, text: str, max_words: int = 120) -> str:
        words = (text or "").split()
        if len(words) <= max_words:
            return text.strip()
        return " ".join(words[:max_words]).strip() + "..."

    def _limit_list(self, items: List[str], max_items: int = 5) -> List[str]:
        return items[:max_items]

    def _format_history(self, history: Optional[List[Dict[str, Any]]]) -> str:
        if not history:
            return "No previous conversation."
        lines = []
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", {})
            if role == "user":
                text = content.get("question") or content.get("text") or ""
                if text:
                    lines.append(f"Farmer: {text}")
            else:
                text = content.get("answer") or content.get("text") or ""
                if text:
                    lines.append(f"Advisor: {text}")
        return "\n".join(lines) if lines else "No previous conversation."

    def _try_parse_inline_json_text(self, text: str) -> Optional[Dict[str, Any]]:
        if not text or not isinstance(text, str):
            return None
        s = text.strip()

        # direct JSON
        try:
            obj = json.loads(s)
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass

        # first {...} block
        m = re.search(r"(\{.*\})", s, re.DOTALL)
        if m:
            try:
                obj = json.loads(m.group(1))
                if isinstance(obj, dict):
                    return obj
            except Exception:
                return None
        return None

    def _is_low_information_turn(self, q: str) -> bool:
        q = (q or "").strip().lower()
        if not q:
            return True

        clean = re.sub(r"[^a-z0-9\s?]", "", q)
        words = clean.split()

        # very short social/greeting/ack style turns
        if len(words) <= 2:
            return True

        return False

    # -------------------------
    # Dynamic router (used in schemes mode)
    # -------------------------
    def _route_turn(
        self,
        question: str,
        history_text: str,
        crop: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        router_system = """
You are a strict dialog router for a farmer assistant.
Return ONLY valid JSON with exactly these keys:
speech_act, intent, needs_clarification, missing_slots, response_mode, confidence, extracted_slots

Allowed values:
- speech_act: question | greeting | acknowledgement | clarification | other
- intent: agronomy | scheme | market | safety | unknown
- response_mode: answer | ask_clarification | acknowledge
- missing_slots: array containing any of: crop, stage, location
- extracted_slots: object with keys crop, stage, location (string or "")
- confidence: 0..1

Policy:
1) greetings/thanks -> acknowledge
2) If user asks a meaningful agronomy question, prefer response_mode=answer.
3) If only 1 slot is missing (especially location), still answer with assumptions.
4) ask_clarification only when question is too ambiguous to answer.
"""
        router_prompt = f"""
User message:
{question}

Known profile:
- crop: {crop or "unknown"}
- location: {location or "unknown"}

Recent conversation:
{history_text}
"""

        try:
            routed = self.bedrock_service.invoke_claude(router_prompt, router_system)
            if not isinstance(routed, dict):
                routed = {}
        except Exception:
            routed = {}

        missing = routed.get("missing_slots")
        if not isinstance(missing, list):
            missing = []

        extracted = routed.get("extracted_slots")
        if not isinstance(extracted, dict):
            extracted = {}

        crop_from_q = str(extracted.get("crop", "")).strip()
        stage_from_q = str(extracted.get("stage", "")).strip()
        location_from_q = str(extracted.get("location", "")).strip()

        speech_act = str(routed.get("speech_act", "question")).lower().strip()
        intent = str(routed.get("intent", "agronomy")).lower().strip()
        response_mode = str(routed.get("response_mode", "answer")).lower().strip()
        needs_clarification = bool(routed.get("needs_clarification", False))
        confidence = self._safe_float(routed.get("confidence"), 0.6)

        allowed_speech = {"question", "greeting", "acknowledgement", "clarification", "other"}
        allowed_intent = {"agronomy", "scheme", "market", "safety", "unknown"}
        allowed_mode = {"answer", "ask_clarification", "acknowledge"}

        if speech_act not in allowed_speech:
            speech_act = "question"
        if intent not in allowed_intent:
            intent = "agronomy"
        if response_mode not in allowed_mode:
            response_mode = "answer"

        # Effective slots from profile + extraction
        effective_crop = (crop or "").strip() or crop_from_q
        effective_location = (location or "").strip() or location_from_q
        effective_stage = stage_from_q  # profile currently doesn't store stage

        computed_missing = []
        if not effective_crop:
            computed_missing.append("crop")
        if not effective_stage:
            computed_missing.append("stage")
        if not effective_location:
            computed_missing.append("location")

        # If only one slot missing and agronomy, answer anyway
        if len(computed_missing) <= 1 and intent in {"agronomy", "unknown"}:
            response_mode = "answer"
            needs_clarification = False
            missing = computed_missing
        else:
            missing = [m for m in missing if m in {"crop", "stage", "location"}] or computed_missing

        # If short + low confidence, clarify only for unclear question turns
        if confidence < 0.35 and len((question or "").split()) < 4 and speech_act in {"question", "other"}:
            response_mode = "ask_clarification"

        return {
            "speech_act": speech_act,
            "intent": intent if intent != "unknown" else "agronomy",
            "needs_clarification": needs_clarification,
            "missing_slots": missing,
            "response_mode": response_mode,
            "confidence": confidence,
        }

    # -------------------------
    # KB filter
    # -------------------------
    def _build_kb_filter(self, intent: str, language: str, location: Optional[str]) -> Optional[Dict[str, Any]]:
        clauses: List[Dict[str, Any]] = []
        if intent == "scheme":
            clauses.append({"equals": {"key": "doc_type", "value": "scheme"}})
        elif intent == "market":
            clauses.append({"equals": {"key": "doc_type", "value": "market"}})

        if language:
            clauses.append({"equals": {"key": "language", "value": language}})
        if location:
            clauses.append({"equals": {"key": "location", "value": location}})

        if not clauses:
            return None
        if len(clauses) == 1:
            return clauses[0]
        return {"andAll": clauses}

    # -------------------------
    # Output normalization
    # -------------------------
    def _normalize_output(
        self,
        response_json: Dict[str, Any],
        default_message_type: str,
        default_confidence: float,
        citations: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        if isinstance(response_json, dict) and isinstance(response_json.get("text"), str):
            repaired = self._try_parse_inline_json_text(response_json.get("text"))
            if repaired:
                response_json = repaired

        answer = response_json.get("answer") or response_json.get("text") or "Not confident."
        if isinstance(answer, str):
            a = answer.strip()
            if a.startswith("{") and '"message_type"' in a:
                repaired = self._try_parse_inline_json_text(a)
                if repaired:
                    response_json = repaired
                    answer = response_json.get("answer") or "I understood your question. Please ask once again."
                else:
                    answer = "I understood your question, but had a formatting issue. Please ask once again."

        message_type = str(response_json.get("message_type", default_message_type)).strip().lower()
        if message_type not in {"advice", "schemes", "refusal", "fallback"}:
            message_type = default_message_type

        confidence = self._safe_float(response_json.get("confidence_score"), default_confidence)
        if message_type == "refusal":
            confidence = 0.0
        elif message_type == "fallback":
            confidence = min(confidence, 0.35)

        checklist = self._limit_list(self._as_list(response_json.get("checklist")), 5)
        do_list = self._limit_list(self._as_list(response_json.get("do")), 5)
        dont_list = self._limit_list(self._as_list(response_json.get("dont")), 5)

        raw_schemes = response_json.get("schemes") if isinstance(response_json.get("schemes"), list) else []
        schemes = []
        for s in raw_schemes[:3]:
            if isinstance(s, dict):
                schemes.append({
                    "name": str(s.get("name", "")).strip(),
                    "description": self._truncate_words(str(s.get("description", "")).strip(), 40),
                    "documents": self._limit_list(self._as_list(s.get("documents")), 6),
                    "link": str(s.get("link", "")).strip(),
                })

        return {
            "message_type": message_type,
            "answer": self._truncate_words(str(answer).strip(), 120),
            "confidence_score": confidence,
            "citations": citations or [],
            "checklist": checklist,
            "do": do_list,
            "dont": dont_list,
            "schemes": schemes,
            "eligible_schemes": self._limit_list(self._as_list(response_json.get("eligible_schemes")), 6),
            "documents_required": self._limit_list(self._as_list(response_json.get("documents_required")), 8),
            "application_links": self._limit_list(self._as_list(response_json.get("application_links")), 6),
        }

    # -------------------------
    # Main
    # -------------------------
    def answer_question(
        self,
        question: str,
        language: str,
        crop: str = None,
        location: str = None,
        history: Optional[List[Dict[str, Any]]] = None,
        conversation_summary: str = "",
        advisory_mode: str = "llm"
    ) -> Dict[str, Any]:
        # 1) Safety
        if not is_query_safe(question):
            return {
                "message_type": "refusal",
                "answer": get_safety_refusal(),
                "confidence_score": 0.0,
                "citations": [],
                "checklist": [],
                "do": [],
                "dont": [],
                "schemes": [],
                "eligible_schemes": [],
                "documents_required": [],
                "application_links": []
            }

        # Normalize mode
        advisory_mode = (advisory_mode or "llm").strip().lower()
        if advisory_mode not in {"llm", "schemes"}:
            advisory_mode = "llm"

        use_rag = advisory_mode == "schemes"
        history_text = self._format_history(history)

        # ------------------------------------------------------
        # B) Direct LLM path (default / LLM mode)
        # ------------------------------------------------------
        if not use_rag:
            # Handle greeting/thanks/very short social turns gracefully
            if self._is_low_information_turn(question):
                return {
                    "message_type": "advice",
                    "answer": "Namaste! I can help with crop care, pests, irrigation, fertilizer, yield, mandi prices, and schemes. What do you need help with today?",
                    "confidence_score": 0.9,
                    "citations": [],
                    "checklist": [],
                    "do": [],
                    "dont": [],
                    "schemes": [],
                    "eligible_schemes": [],
                    "documents_required": [],
                    "application_links": []
                }

            high_risk_agri = is_high_risk_agri_query(question)

            system_prompt = f"""
You are KhetiPulse AI, a practical advisor for Indian farmers.
Language: {language}
This is direct advisory mode (no retrieved context).

Return ONLY valid JSON with keys:
message_type, answer, confidence_score, checklist, do, dont

Rules:
- message_type must be "advice" or "fallback"
- answer max 110 words
- checklist/do/dont max 5 items each
- adapt to Indian farming context (KVK, monsoon variability, common crops)
- if sowing date is unknown, use relative timeline (week 1-2, week 3-6), not fixed months
- for pesticide/chemical questions, include caution and label-following advice
- if user message is greeting/thanks/acknowledgement/short social text, respond warmly in one sentence and ask what farm help is needed; do not return fallback
"""

            direct_prompt = f"""
Farmer profile:
- crop: {crop or "unknown"}
- location: {location or "unknown"}

Conversation summary:
{conversation_summary or "No summary available."}

Recent conversation:
{history_text}

Current question:
{question}
"""

            try:
                response_json = self.bedrock_service.invoke_claude(prompt=direct_prompt, system_prompt=system_prompt)
            except Exception as e:
                raise ExternalServiceError("Bedrock LLM", detail=str(e))

            if not isinstance(response_json, dict):
                response_json = {"text": str(response_json)}

            out = self._normalize_output(
                response_json=response_json,
                default_message_type="advice",
                default_confidence=0.55,
                citations=[]
            )

            if out["message_type"] == "advice":
                out["confidence_score"] = min(out["confidence_score"], 0.65)

            # No schemes/citations in LLM-only mode
            out["schemes"] = []
            out["eligible_schemes"] = []
            out["documents_required"] = []
            out["application_links"] = []
            out["citations"] = []

            if high_risk_agri and out["message_type"] in {"advice", "fallback"}:
                disclaimer = get_agri_safety_disclaimer()
                if disclaimer not in out["answer"]:
                    out["answer"] = f'{out["answer"]}\n\n{disclaimer}'

            return out

        # ------------------------------------------------------
        # A) RAG path (Schemes mode only)
        # ------------------------------------------------------
        route = self._route_turn(
            question=question,
            history_text=history_text,
            crop=crop,
            location=location
        )

        if route["response_mode"] == "acknowledge":
            return {
                "message_type": "advice",
                "answer": "Namaste! Schemes & Policies mode is enabled. Ask about eligibility, documents, and application links.",
                "confidence_score": 0.9,
                "citations": [],
                "checklist": [],
                "do": [],
                "dont": [],
                "schemes": [],
                "eligible_schemes": [],
                "documents_required": [],
                "application_links": []
            }

        missing = route.get("missing_slots", [])
        if (route["response_mode"] == "ask_clarification" or route["needs_clarification"]) and len(missing) >= 2:
            ask = ", ".join(missing) if missing else "state, crop and category details"
            return {
                "message_type": "fallback",
                "answer": f"Please share more details for scheme guidance: {ask}.",
                "confidence_score": 0.3,
                "citations": [],
                "checklist": [],
                "do": [],
                "dont": [],
                "schemes": [],
                "eligible_schemes": [],
                "documents_required": [],
                "application_links": []
            }

        intent = route["intent"]
        if intent not in {"scheme", "market"}:
            return {
                "message_type": "fallback",
                "answer": "Schemes & Policies mode is enabled. Please ask about eligibility, required documents, benefits, or application links.",
                "confidence_score": 0.4,
                "citations": [],
                "checklist": [],
                "do": [],
                "dont": [],
                "schemes": [],
                "eligible_schemes": [],
                "documents_required": [],
                "application_links": []
            }

        query_context = question
        if crop:
            query_context = f"Crop: {crop}, {query_context}"
        if location:
            query_context = f"Location: {location}, {query_context}"

        metadata_filter = self._build_kb_filter(intent=intent, language=language, location=location)

        try:
            retrieved_results = self.bedrock_service.retrieve_from_kb(
                query=query_context,
                metadata_filter=metadata_filter,
                number_of_results=6
            )
            if not retrieved_results:
                retrieved_results = self.bedrock_service.retrieve_from_kb(
                    query=query_context,
                    metadata_filter=None,
                    number_of_results=6
                )
        except Exception as e:
            raise ExternalServiceError("Bedrock Knowledge Base", detail=str(e))

        if not retrieved_results:
            return {
                "message_type": "fallback",
                "answer": "Not confident. I couldn't find reliable information for this query in the knowledge base.",
                "confidence_score": 0.3,
                "citations": [],
                "checklist": [],
                "do": [],
                "dont": [],
                "schemes": [],
                "eligible_schemes": [],
                "documents_required": [],
                "application_links": []
            }

        context_chunks = []
        citations = []
        scores = []

        for r in retrieved_results:
            text = ((r.get("content") or {}).get("text") or "").strip()
            if text:
                context_chunks.append(text)

            uri = (((r.get("location") or {}).get("s3Location") or {}).get("uri"))
            if uri:
                citations.append(uri)

            score = r.get("score")
            if isinstance(score, (int, float)):
                scores.append(float(score))

        if not context_chunks:
            return {
                "message_type": "fallback",
                "answer": "Not confident. I could not extract reliable context.",
                "confidence_score": 0.3,
                "citations": [],
                "checklist": [],
                "do": [],
                "dont": [],
                "schemes": [],
                "eligible_schemes": [],
                "documents_required": [],
                "application_links": []
            }

        context_text = "\n\n".join(context_chunks)
        unique_citations = list(set(citations))
        retrieval_score = sum(scores) / len(scores) if scores else 0.5
        kb_confidence = calculate_confidence(retrieval_score=retrieval_score)

        if intent == "scheme":
            system_prompt = f"""
You are KhetiPulse AI.
Language: {language}
Use ONLY provided context.
Return ONLY valid JSON (no markdown).

For scheme queries return ONLY keys:
message_type, answer, confidence_score, schemes

Rules:
- message_type = "schemes"
- max 3 schemes
- schemes item format:
  {{"name":"","description":"","documents":[],"link":""}}
- answer max 100 words
"""
            default_type = "schemes"
        else:
            system_prompt = f"""
You are KhetiPulse AI.
Language: {language}
Use ONLY provided context.
Return ONLY valid JSON (no markdown).

For market queries return ONLY keys:
message_type, answer, confidence_score, checklist, do, dont

Rules:
- message_type = "advice"
- mention rates can change; verify latest in Sell Smart
- answer max 100 words
- max 4 items each list
"""
            default_type = "advice"

        prompt = f"""
Conversation summary:
{conversation_summary or "No summary available."}

Recent conversation:
{history_text}

Retrieved context:
{context_text}

Farmer question:
{question}
"""

        try:
            response_json = self.bedrock_service.invoke_claude(prompt=prompt, system_prompt=system_prompt)
        except Exception as e:
            raise ExternalServiceError("Bedrock LLM", detail=str(e))

        if not isinstance(response_json, dict):
            response_json = {"text": str(response_json)}

        out = self._normalize_output(
            response_json=response_json,
            default_message_type=default_type,
            default_confidence=kb_confidence,
            citations=unique_citations
        )

        if intent == "scheme":
            out["confidence_score"] = min(out["confidence_score"], 0.85)
        elif intent == "market":
            out["confidence_score"] = min(out["confidence_score"], 0.8)
            out["schemes"] = []
            out["eligible_schemes"] = []
            out["documents_required"] = []
            out["application_links"] = []

        return out