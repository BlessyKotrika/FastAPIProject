from fastapi import APIRouter, HTTPException
from app.models.request_models import ChatRequest
from app.models.response_models import ChatResponse
from app.services.rag_service import rag_service

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = rag_service.answer_question(
            question=request.question,
            language=request.language,
            crop=request.crop,
            location=request.location
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
