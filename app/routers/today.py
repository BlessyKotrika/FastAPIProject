from fastapi import APIRouter, HTTPException, Depends
from app.models.request_models import TodayRequest
from app.models.response_models import TodayResponse
from app.services.weather_service import WeatherService
from app.services.recommendation_engine import RecommendationEngine
from app.dependencies import get_weather_service, get_recommendation_engine
from app.utils.exceptions import KhetiPulseException

router = APIRouter()

@router.post("/", response_model=TodayResponse)
async def get_today_actions(
    request: TodayRequest,
    weather_service: WeatherService = Depends(get_weather_service),
    recommendation_engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    print(f"DEBUG: get_today_actions called with {request}")
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
    except KhetiPulseException as e:
        raise e
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
