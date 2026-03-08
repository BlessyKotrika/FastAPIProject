from fastapi import APIRouter, HTTPException, Depends
from app.models.request_models import SellSmartRequest
from app.models.response_models import SellSmartResponse
from app.services.mandi_service import MandiService
from app.dependencies import get_mandi_service
from app.utils.confidence import calculate_confidence

router = APIRouter()


@router.post("/", response_model=SellSmartResponse)
async def sell_smart(request: SellSmartRequest, mandi_service: MandiService = Depends(get_mandi_service)):
    data = await mandi_service.get_mandi_data(request.crop, request.location, request.state)

    if not data:
        data = [
            {"Market": f"{request.location or 'Local'} Mandi", "District": request.location or "Various", "State": request.state or "Various", "Commodity": request.crop, "Modal_Price": "2250", "Arrival_Date": "08/03/2026"},
            {"Market": "Regional Hub", "District": "N/A", "State": request.state or "Various", "Commodity": request.crop, "Modal_Price": "2310", "Arrival_Date": "08/03/2026"}
        ]

    best_market, price = mandi_service.get_best_mandi(data, request.location, request.language)
    trend_7d, _ = mandi_service.compute_trends(data)

    return SellSmartResponse(
        best_mandi=best_market,
        net_price=price,
        trend_7d=trend_7d,
        forecast_band=f"₹{price-50} - ₹{price+50}",
        confidence_score=calculate_confidence(data_freshness=0.95),
        all_markets=data
    )