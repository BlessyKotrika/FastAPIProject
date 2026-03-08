from fastapi import APIRouter, HTTPException, Depends
from app.models.request_models import SellSmartRequest
from app.models.response_models import SellSmartResponse
from app.services.mandi_service import MandiService
from app.dependencies import get_mandi_service
from app.utils.confidence import calculate_confidence

router = APIRouter()

@router.post("/", response_model=SellSmartResponse)
async def sell_smart(request: SellSmartRequest, mandi_service: MandiService = Depends(get_mandi_service)):
    try:
        # Step 1: Load Mandi Data
        data = await mandi_service.get_mandi_data(request.crop, request.location, request.state)

        if not data:
            return SellSmartResponse(
                best_mandi="Data not available for the selected crop.",
                net_price=0,
                trend_7d="N/A",
                forecast_band="N/A",
                confidence_score=calculate_confidence(data_freshness=0.2),
                all_markets=[]
            )
        
        # Step 2: Compute Best Mandi with language support
        best_market, price = mandi_service.get_best_mandi(data, request.location, request.language)
        
        # Step 3: Compute Trends
        trend_7d, _ = mandi_service.compute_trends(data)
        
        return SellSmartResponse(
            best_mandi=best_market,
            net_price=price,
            trend_7d=trend_7d,
            forecast_band=f"₹{price-50} - ₹{price+50}",
            confidence_score=calculate_confidence(data_freshness=0.95),
            all_markets=data
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
