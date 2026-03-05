from fastapi import APIRouter, HTTPException
from app.models.request_models import TodayRequest
from app.models.response_models import TodayResponse
from app.services.weather_service import weather_service
from app.services.recommendation_engine import recommendation_engine

router = APIRouter()

@router.post("/", response_model=TodayResponse)
async def get_today_actions(request: TodayRequest):
    try:
        # Step 1: Fetch Weather
        weather_data = await weather_service.get_forecast(request.location)
        
        # Step 2: Determine Crop Stage (Mock logic based on sowing date)
        # In production, use more sophisticated logic or a separate service
        crop_stage = "Vegetative"
        
        # Step 3: Generate Actions
        actions = recommendation_engine.generate_today_actions(
            crop=request.crop,
            stage=crop_stage,
            weather_data=weather_data,
            language=request.language
        )
        
        return actions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
