from fastapi import APIRouter, Depends, HTTPException

from app.models.request_models import ChatRequest
from app.models.response_models import ChatResponse
from app.services.chat_history_service import ChatHistoryService
from app.services.mandi_service import MandiService
from app.services.rag_service import RAGService
from app.dependencies import get_chat_history_service, get_mandi_service, get_rag_service
from app.routers.auth import get_current_user

router = APIRouter()

MANDI_KEYWORDS = {
    "mandi", "market", "price", "rates", "rate", "bhav", "भाव", "भाव क्या", "sell", "selling"
}

CROP_KEYWORDS = {
    "wheat": {"wheat", "gehun", "गेहूं", "गेहूँ"},
    "paddy": {"paddy", "rice", "dhan", "धान"},
    "maize": {"maize", "corn", "makka", "मक्का"},
    "cotton": {"cotton", "kapas", "कपास"},
    "turmeric": {"turmeric", "haldi", "हल्दी"},
    "onion": {"onion", "pyaj", "pyaaz", "प्याज"},
    "potato": {"potato", "aloo", "आलू"},
    "chillies": {"chilli", "chillies", "mirchi", "मिर्ची"},
}


def _is_mandi_query(question: str) -> bool:
    q = (question or "").lower()
    return any(k.lower() in q for k in MANDI_KEYWORDS)


def _extract_crop_from_query(question: str, fallback_crop: str = "") -> str:
    q = (question or "").lower()
    for canonical, tokens in CROP_KEYWORDS.items():
        if any(tok.lower() in q for tok in tokens):
            return canonical
    return (fallback_crop or "").strip().lower()


def _is_ambiguous_paddy_query(question: str) -> bool:
    q = (question or "").lower()
    mentions_dhan = any(x in q for x in {"dhan", "धान", "paddy", "rice"})
    mentions_variety = any(
        x in q for x in {"basmati", "1121", "1509", "swarna", "non basmati", "non-basmati"}
    )
    return mentions_dhan and not mentions_variety


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
    mandi_service: MandiService = Depends(get_mandi_service),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("user_id") or current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user context")

    account_language = str(current_user.get("language") or request.language or "hi")

    if request.conversation_id:
        conversation = chat_history_service.require_conversation(
            conversation_id=request.conversation_id,
            user_id=user_id,
        )
        chat_history_service.upsert_conversation_metadata(
            conversation_id=request.conversation_id,
            user_id=user_id,
            language=account_language,
            crop=request.crop,
            location=request.location,
        )
        conversation_id = request.conversation_id
    else:
        conversation = chat_history_service.create_conversation(
            user_id=user_id,
            language=account_language,
            crop=request.crop,
            location=request.location,
        )
        conversation_id = conversation["id"]

    history = chat_history_service.get_recent_messages(
        conversation_id=conversation_id,
        user_id=user_id,
        limit=8,
    )

    user_message_payload = {
        "question": request.question,
        "language": account_language,
        "crop": request.crop,
        "location": request.location,
    }
    chat_history_service.add_message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=user_message_payload,
        message_id=request.client_message_id,
    )

    question = request.question or ""
    profile_crops = current_user.get("crops") or []
    profile_crop = request.crop or current_user.get("crop") or (profile_crops[0] if profile_crops else "")
    profile_location = current_user.get("location") or current_user.get("district")
    state = current_user.get("state")
    effective_location = request.location or profile_location
    effective_crop = _extract_crop_from_query(question, fallback_crop=profile_crop or "")

    if _is_mandi_query(question):
        if _is_ambiguous_paddy_query(question):
            rag_response = {
                "message_type": "fallback",
                "answer": "Please specify which type of dhan you mean (for example: basmati, non-basmati, 1121).",
                "confidence_score": 0.35,
                "citations": [],
                "checklist": [],
                "do": [],
                "dont": [],
                "schemes": [],
                "eligible_schemes": [],
                "documents_required": [],
                "application_links": [],
            }
        elif not effective_crop:
            rag_response = {
                "message_type": "fallback",
                "answer": "Please tell me which crop you want mandi prices for.",
                "confidence_score": 0.35,
                "citations": [],
                "checklist": [],
                "do": [],
                "dont": [],
                "schemes": [],
                "eligible_schemes": [],
                "documents_required": [],
                "application_links": [],
            }
        elif not effective_location:
            rag_response = {
                "message_type": "fallback",
                "answer": "Please share your district/location so I can fetch nearby mandi prices.",
                "confidence_score": 0.35,
                "citations": [],
                "checklist": [],
                "do": [],
                "dont": [],
                "schemes": [],
                "eligible_schemes": [],
                "documents_required": [],
                "application_links": [],
            }
        else:
            mandi_data = await mandi_service.get_mandi_data(
                crop=effective_crop,
                location=effective_location,
                state=state,
            )
            if not mandi_data:
                rag_response = {
                    "message_type": "fallback",
                    "answer": f"Data not available for {effective_crop} in {effective_location}.",
                    "confidence_score": 0.35,
                    "citations": [],
                    "checklist": [],
                    "do": [],
                    "dont": [],
                    "schemes": [],
                    "eligible_schemes": [],
                    "documents_required": [],
                    "application_links": [],
                }
            else:
                best_market, best_price = mandi_service.get_best_mandi(
                    mandi_data, effective_location, account_language
                )
                top = sorted(
                    mandi_data,
                    key=lambda x: float(x.get("Modal_Price", 0) or 0),
                    reverse=True,
                )[:3]
                top_lines = [
                    (
                        f'{i + 1}. {r.get("Market", "Unknown")} '
                        f'({r.get("District", "Unknown")}): INR {r.get("Modal_Price", "N/A")}/quintal'
                    )
                    for i, r in enumerate(top)
                ]
                rag_response = {
                    "message_type": "advice",
                    "answer": (
                        f"Top mandi for {effective_crop} near {effective_location}: "
                        f"{best_market} at INR {int(best_price) if best_price else 0}/quintal.\n"
                        + "\n".join(top_lines)
                    ),
                    "confidence_score": 0.82,
                    "citations": [],
                    "checklist": [],
                    "do": [],
                    "dont": [],
                    "schemes": [],
                    "eligible_schemes": [],
                    "documents_required": [],
                    "application_links": [],
                }
    else:
        rag_response = rag_service.answer_question(
            question=request.question,
            language=account_language,
            crop=request.crop or profile_crop,
            location=request.location or profile_location,
            history=history,
            conversation_summary=conversation.get("summary_text", ""),
            advisory_mode=request.advisory_mode or "llm",
        )

    normalized = {
        "message_type": rag_response.get("message_type", "advice"),
        "answer": rag_response.get("answer", "Not confident."),
        "confidence_score": rag_response.get("confidence_score", 0.5),
        "citations": rag_response.get("citations", []),
        "checklist": rag_response.get("checklist", []),
        "do": rag_response.get("do", []),
        "dont": rag_response.get("dont", []),
        "schemes": rag_response.get("schemes", []),
        "eligible_schemes": rag_response.get("eligible_schemes", []),
        "documents_required": rag_response.get("documents_required", []),
        "application_links": rag_response.get("application_links", []),
    }

    assistant_message_id = chat_history_service.add_message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
        content=normalized,
    )

    return {
        "conversation_id": conversation_id,
        "message_id": assistant_message_id,
        **normalized,
    }
