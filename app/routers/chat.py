from fastapi import APIRouter, HTTPException, Depends
from app.models.request_models import ChatRequest
from app.models.response_models import ChatResponse
from app.services.rag_service import RAGService
from app.dependencies import get_rag_service

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, rag_service: RAGService = Depends(get_rag_service)):
    try:
        response = rag_service.answer_question(
            question=request.question,
            language=request.language,
            crop=request.crop,
            location=request.location
        )
        return response
    except Exception as e:
        # Our global exception handler will catch specialized exceptions,
        # but for others we can still let them bubble up or raise here.
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
