import httpx
from app.config import settings

class WeatherService:
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5/forecast"

    async def get_forecast(self, location: str):
        """Fetches 48-hour weather forecast."""
        if not self.api_key:
            # Mock data for demonstration if API key is missing
            return {
                "list": [
                    {"dt_txt": "2025-11-01 12:00:00", "main": {"temp": 25, "humidity": 60}, "weather": [{"main": "Clear"}], "wind": {"speed": 5}},
                    {"dt_txt": "2025-11-02 12:00:00", "main": {"temp": 22, "humidity": 80}, "weather": [{"main": "Rain"}], "wind": {"speed": 12}}
                ]
            }
        
        async with httpx.AsyncClient() as client:
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric",
                "cnt": 16 # 16 * 3 hours = 48 hours
            }
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()

weather_service = WeatherService()
