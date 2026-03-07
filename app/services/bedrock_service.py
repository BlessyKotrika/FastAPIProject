import json
import logging
import re
from typing import Dict, Any, List, Optional

import boto3

from app.config import settings

logger = logging.getLogger(__name__)


class BedrockService:
    def __init__(self):
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=settings.AWS_REGION
        )
        self.kb_client = boto3.client(
            service_name="bedrock-agent-runtime",
            region_name=settings.AWS_REGION
        )

    # ------------------------
    # LLM Invocation
    # ------------------------
    def _invoke_raw_text(self, prompt: str, system_prompt: str = "") -> str:
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 700,
            "temperature": 0.2,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ]
        })

        response = self.client.invoke_model(
            modelId=settings.CLAUDE_MODEL_ID,
            body=body
        )

        raw_body = response.get("body").read()
        response_body = json.loads(raw_body)
        return self._extract_text_content(response_body)

    def invoke_claude(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """
        Invokes Claude and returns parsed JSON (best effort).
        Raises on hard invoke errors. Attempts JSON repair if needed.
        """
        try:
            text_content = self._invoke_raw_text(prompt=prompt, system_prompt=system_prompt)
        except Exception as e:
            logger.error("Bedrock invoke failed", exc_info=True)
            raise RuntimeError(f"Bedrock invoke failed: {str(e)}") from e

        if not text_content:
            raise RuntimeError("No text content returned by Bedrock model")

        # 1) strict parse
        parsed = self._try_parse_json(text_content)
        if parsed is not None:
            return parsed

        # 2) extract JSON block from markdown / surrounding text
        extracted = self._extract_json_block(text_content)
        if extracted is not None:
            return extracted

        # 3) repair pass with model
        repaired = self._repair_json_with_model(text_content)
        if repaired is not None:
            return repaired

        # 4) final fallback
        logger.warning("Model did not return valid JSON even after repair. Returning text fallback.")
        return {"text": text_content.strip()}

    def _repair_json_with_model(self, bad_text: str) -> Optional[Dict[str, Any]]:
        repair_system = (
            "You are a strict JSON formatter. "
            "Return ONLY a valid JSON object. No markdown, no explanation."
        )
        repair_prompt = f"""
Convert the following content into a valid JSON object.
If fields are missing, include empty defaults.

Required keys:
message_type, answer, confidence_score, checklist, do, dont, schemes,
eligible_schemes, documents_required, application_links

Content:
{bad_text}
"""
        try:
            repaired_text = self._invoke_raw_text(prompt=repair_prompt, system_prompt=repair_system)
            parsed = self._try_parse_json(repaired_text)
            if parsed is not None:
                return parsed

            extracted = self._extract_json_block(repaired_text)
            if extracted is not None:
                return extracted

            return None
        except Exception:
            logger.warning("JSON repair pass failed", exc_info=True)
            return None

    def _extract_text_content(self, response_body: Dict[str, Any]) -> str:
        content = response_body.get("content", [])
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    txt = item.get("text")
                    if isinstance(txt, str):
                        parts.append(txt)
            return "\n".join(parts).strip()
        return ""

    def _try_parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return data
            return None
        except json.JSONDecodeError:
            return None

    def _extract_json_block(self, text: str) -> Optional[Dict[str, Any]]:
        # ```json {...}```
        fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
        if fenced:
            parsed = self._try_parse_json(fenced.group(1))
            if parsed is not None:
                return parsed

        # ``` {...} ```
        generic_fenced = re.search(r"```\s*(\{.*?\})\s*```", text, re.DOTALL)
        if generic_fenced:
            parsed = self._try_parse_json(generic_fenced.group(1))
            if parsed is not None:
                return parsed

        # text ... { ... }
        loose_obj = re.search(r"(\{.*\})", text, re.DOTALL)
        if loose_obj:
            parsed = self._try_parse_json(loose_obj.group(1))
            if parsed is not None:
                return parsed

        return None

    # ------------------------
    # Knowledge Base Retrieval
    # ------------------------
    def retrieve_from_kb(
        self,
        query: str,
        kb_id: str = settings.BEDROCK_KB_ID,
        metadata_filter: Optional[Dict[str, Any]] = None,
        number_of_results: int = 6
    ) -> List[Dict[str, Any]]:
        if not kb_id:
            logger.warning("BEDROCK_KB_ID missing; returning empty retrieval results.")
            return []

        vector_search_cfg: Dict[str, Any] = {
            "numberOfResults": number_of_results,
            "overrideSearchType": "HYBRID"
        }

        if metadata_filter:
            vector_search_cfg["filter"] = metadata_filter

        try:
            response = self.kb_client.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={"text": query},
                retrievalConfiguration={"vectorSearchConfiguration": vector_search_cfg}
            )
            results = response.get("retrievalResults", [])
            if not isinstance(results, list):
                logger.warning("Unexpected retrievalResults format: %s", type(results))
                return []
            return results
        except Exception as e:
            logger.error("Error retrieving from KB", exc_info=True)
            raise RuntimeError(f"KB retrieve failed: {str(e)}") from e


bedrock_service = BedrockService()