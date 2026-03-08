from fastapi import APIRouter, HTTPException, Depends
from app.models.request_models import SchemeRequest
from app.models.response_models import SchemeResponse
from app.services.rag_service import RAGService
from app.dependencies import get_rag_service
from app.routers.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=SchemeResponse)
async def get_schemes(
    request: SchemeRequest,
    rag_service: RAGService = Depends(get_rag_service),
    current_user: dict = Depends(get_current_user),
):
    try:
        account_language = current_user.get("language") or request.language or "hi"

        # Keep question user-like so the RAG intent router can classify it as a scheme query.
        query = (
            f"What government schemes are available for a {request.category} farmer "
            f"in {request.state} growing {request.crop}?"
        )
        
        # Use RAG to find schemes based on criteria
        response = rag_service.answer_question(
            question=query,
            language=str(account_language),
            crop=request.crop,
            location=request.state,
            advisory_mode="schemes"
        )
        
        print("RAG RESPONSE:", response)
        print("TYPE:", type(response))
        # Step 2: Extract data from LLM response if available, or use comprehensive defaults
        # In production, we expect the LLM to return these keys based on the context it finds
        schemes = None

        if isinstance(response, dict):
            schemes = response.get("schemes")
        
        # If RAG returned text instead of a structured object (fallback case)
        if not schemes:
            # More comprehensive default list of schemes relevant across India
            schemes = [
                {
                    "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
                    "description": "Income support of ₹6,000 per year in three installments to all landholding farmer families.",
                    "documents": ["Aadhaar Card", "Land Ownership Documents", "Bank Passbook"],
                    "link": "https://pmkisan.gov.in/"
                },
                {
                    "name": "PM-FBY (Pradhan Mantri Fasal Bima Yojana)",
                    "description": "Crop insurance scheme for protection against crop failure due to natural calamities, pests or diseases.",
                    "documents": ["Aadhaar Card", "Land Possession Certificate", "Sowing Certificate", "Bank Details"],
                    "link": "https://pmfby.gov.in/"
                },
                {
                    "name": "KCC (Kisan Credit Card)",
                    "description": "Provides farmers with timely access to credit for agricultural needs at low interest rates.",
                    "documents": ["Aadhaar Card", "Land Documents", "Passport Size Photos", "Bank Details"],
                    "link": "https://www.sbi.co.in/web/personal-banking/loans/agriculture-banking/kisan-credit-card"
                },
                {
                    "name": f"State-Specific {request.state} Agriculture Subsidy",
                    "description": f"State government subsidies for seeds, fertilizers, and machinery in {request.state}.",
                    "documents": ["Farmer Registration ID", "Land Documents", "Aadhaar Card"],
                    "link": f"https://agriculture.{request.state.lower().replace(' ', '')}.gov.in/"
                },
                {
                    "name": "PM-KMY (Pradhan Mantri Kisan Maandhan Yojana)",
                    "description": "A voluntary and contributory pension scheme for all Small and Marginal Farmers (SMF).",
                    "documents": ["Aadhaar Card", "Savings Bank Account / PM-Kisan Account"],
                    "link": "https://maandhan.in/"
                }
            ]

        return SchemeResponse(
            schemes=schemes,
            eligible_schemes=[s["name"] for s in schemes],
            documents_required=list(set([doc for s in schemes for doc in s["documents"]])),
            application_links=[s["link"] for s in schemes]
        )
    except KhetiPulseException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
