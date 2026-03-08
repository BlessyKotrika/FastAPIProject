from typing import List, Dict, Any
from app.services.bedrock_service import BedrockService
from app.utils.confidence import calculate_confidence
from app.utils.exceptions import ExternalServiceError

class RecommendationEngine:
    def __init__(self, weather_service, mandi_service, bedrock_service: BedrockService):
        self.weather_service = weather_service
        self.mandi_service = mandi_service
        self.bedrock_service = bedrock_service

    def generate_today_actions(self, crop: str, stage: str, weather_data: Dict[str, Any], language: str):
        """Generates actionable advice based on crop stage and weather."""
        weather_list = weather_data.get('list', []) or []
        first_slot = weather_list[0] if weather_list else {}

        # Simple rule-based preprocessing for weather risks
        rain_risk = any("Rain" in (w.get('weather', [{}])[0].get('main', '')) for w in weather_list)
        wind_risk = any((w.get('wind', {}).get('speed', 0) or 0) > 10 for w in weather_list)
        
        weather_summary = f"Weather: {'Rain' if rain_risk else 'Dry'}, {'High Wind' if wind_risk else 'Low Wind'}."
        
        system_prompt = f"""You are KhetiPulse AI, a senior agricultural consultant.
        Provide structured action cards for a farmer.
        Crop: {crop}. Stage: {stage}. {weather_summary}.
        Language: {language}.
        
        Rules:
        - Avoid spraying if rain is forecast or wind > 10 km/h.
        - Provide 'Do Today', 'Avoid Today', and 'Prepare' (next 48h).
        - Return output as JSON with keys: 'do', 'avoid', 'prepare', 'weather_risk'.
        """
        
        prompt = f"Generate action cards for {crop} at {stage} stage given the weather summary: {weather_summary}."
        try:
            response_json = self.bedrock_service.invoke_claude(prompt, system_prompt)
        except Exception as e:
            raise ExternalServiceError("Bedrock LLM", detail=str(e))
        
        # Add metadata
        response_json["weather_risk"] = {
            "rain_forecast": rain_risk,
            "high_wind": wind_risk,
            "source": "OpenWeatherMap"
        }
        response_json["current_weather"] = {
            "temp": (first_slot.get("main", {}) or {}).get("temp"),
            "humidity": (first_slot.get("main", {}) or {}).get("humidity"),
            "wind_speed": (first_slot.get("wind", {}) or {}).get("speed"),
            "condition": ((first_slot.get("weather", [{}]) or [{}])[0] or {}).get("main"),
            "description": ((first_slot.get("weather", [{}]) or [{}])[0] or {}).get("description"),
            "timestamp": first_slot.get("dt_txt"),
        }
        response_json["confidence_score"] = calculate_confidence(weather_certainty=0.9 if rain_risk else 0.8)
        response_json["sources"] = ["Regional Advisory Bulletin"]
        
        return response_json
