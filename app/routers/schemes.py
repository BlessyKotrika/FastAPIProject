from fastapi import APIRouter, HTTPException
from app.models.request_models import SchemeRequest
from app.models.response_models import SchemeResponse
from app.services.rag_service import rag_service

router = APIRouter()

@router.post("/", response_model=SchemeResponse)
async def get_schemes(request: SchemeRequest):
    try:
        # Use RAG to find schemes based on criteria
        query = f"Schemes for {request.category} farmers in {request.state} for {request.crop} with {request.land_size} hectares."
        response = rag_service.answer_question(
            question=query,
            language=request.language,
            crop=request.crop
        )
        
        # In production, LLM should return structured eligibility details.
        # Here we extract from RAG response or use mock for structure.
        return SchemeResponse(
            eligible_schemes=response.get("eligible_schemes", ["PM-KISAN"]),
            documents_required=response.get("documents_required", ["Aadhaar", "Land Records"]),
            application_links=response.get("application_links", ["https://pmkisan.gov.in/"])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
