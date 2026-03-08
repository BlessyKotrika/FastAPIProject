from fastapi import APIRouter, Depends, HTTPException
from app.models.request_models import ChatRequest
from app.models.response_models import ChatResponse
from app.services.rag_service import RAGService
from app.services.chat_history_service import ChatHistoryService
from app.dependencies import get_rag_service, get_chat_history_service
from app.routers.auth import get_current_user
from app.utils.exceptions import KhetiPulseException

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    account_language = str(current_user.get("language") or request.language or "hi")

        # 1) Resolve or create conversation
        if request.conversation_id:
            conversation = chat_history_service.require_conversation(
                conversation_id=request.conversation_id,
                user_id=user_id
            )
            # Keep conversation metadata fresh
            chat_history_service.upsert_conversation_metadata(
                conversation_id=request.conversation_id,
                user_id=user_id,
                language=str(request.language) if request.language else None,
                crop=request.crop,
                location=request.location
            )
            conversation_id = request.conversation_id
        else:
            conversation = chat_history_service.create_conversation(
                user_id=user_id,
                language=str(request.language),
                crop=request.crop,
                location=request.location
            )
            conversation_id = conversation["id"]

        # 2) Fetch prior history BEFORE adding current user turn
        history = chat_history_service.get_recent_messages(
            conversation_id=conversation_id,
            user_id=user_id,
            language=account_language,
            crop=request.crop,
            location=request.location
        )

        # 3) Persist user message
        user_message_payload = {
            "question": request.question,
            "language": str(request.language),
            "crop": request.crop,
            "location": request.location
        }
        chat_history_service.add_message(
            conversation_id=conversation_id,
            user_id=user_id,
            language=account_language,
            crop=request.crop,
            location=request.location,
            history=history,
            conversation_summary=conversation.get("summary_text", ""),
            advisory_mode=request.advisory_mode or "llm"
        )
        conversation_id = conversation["id"]

    # 2) Fetch prior history BEFORE adding current user turn
    history = chat_history_service.get_recent_messages(
        conversation_id=conversation_id,
        user_id=user_id,
        limit=8
    )

    # 3) Persist user message
    user_message_payload = {
        "question": request.question,
        "language": account_language,
        "crop": request.crop,
        "location": request.location
    }
    chat_history_service.add_message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=user_message_payload,
        message_id=request.client_message_id  # optional idempotency key
    )

    # 4) Generate response from RAG with history + summary
    rag_response = rag_service.answer_question(
        question=request.question,
        language=account_language,
        crop=request.crop,
        location=request.location,
        history=history,
        conversation_summary=conversation.get("summary_text", ""),
        advisory_mode=request.advisory_mode or "llm"
    )

        # 6) Persist assistant message
        assistant_message_id = chat_history_service.add_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="assistant",
            content=normalized
        )

    # 7) Return API response
    return {
        "conversation_id": conversation_id,
        "message_id": assistant_message_id,
        **normalized
    }
