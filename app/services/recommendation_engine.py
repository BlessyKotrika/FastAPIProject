from typing import List, Dict, Any
from app.services.bedrock_service import bedrock_service
from app.utils.confidence import calculate_confidence

class RecommendationEngine:
    def generate_today_actions(self, crop: str, stage: str, weather_data: Dict[str, Any], language: str):
        """Generates actionable advice based on crop stage and weather."""
        
        # Simple rule-based preprocessing for weather risks
        rain_risk = any("Rain" in w['weather'][0]['main'] for w in weather_data.get('list', []))
        wind_risk = any(w['wind']['speed'] > 10 for w in weather_data.get('list', []))
        
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
        response_json = bedrock_service.invoke_claude(prompt, system_prompt)
        
        # Add metadata
        response_json["weather_risk"] = {
            "rain_forecast": rain_risk,
            "high_wind": wind_risk,
            "source": "OpenWeatherMap"
        }
        response_json["confidence_score"] = calculate_confidence(weather_certainty=0.9 if rain_risk else 0.8)
        response_json["sources"] = ["Regional Advisory Bulletin"]
        
        return response_json

recommendation_engine = RecommendationEngine()
