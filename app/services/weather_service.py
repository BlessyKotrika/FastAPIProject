import httpx
import logging
from typing import Dict, Any, Optional
from app.config import settings
from app.utils.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self, http_client: Optional[httpx.AsyncClient] = None, api_key: str = settings.OPENWEATHER_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/forecast"
        self._http_client = http_client

    async def get_forecast(self, location: str) -> Dict[str, Any]:
        """Fetches 48-hour weather forecast."""
        if not self.api_key:
            logger.warning("OPENWEATHER_API_KEY missing, returning mock data.")
            return {
                "list": [
                    {"dt_txt": "2025-11-01 12:00:00", "main": {"temp": 25, "humidity": 60}, "weather": [{"main": "Clear"}], "wind": {"speed": 5}},
                    {"dt_txt": "2025-11-02 12:00:00", "main": {"temp": 22, "humidity": 80}, "weather": [{"main": "Rain"}], "wind": {"speed": 12}}
                ]
            }
        
        client = self._http_client or httpx.AsyncClient()
        try:
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric",
                "cnt": 16 # 16 * 3 hours = 48 hours
            }
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Weather API error: {e}")
            raise ExternalServiceError("OpenWeatherMap", detail=str(e))
        finally:
            if self._http_client is None:
                await client.aclose()
