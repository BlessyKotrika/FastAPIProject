import httpx
import asyncio
import time
from app.config import settings
from app.utils.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self, http_client: Optional[httpx.AsyncClient] = None, api_key: str = settings.OPENWEATHER_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/forecast"
        self.cache_ttl_seconds = 120
        self._cache = {}
        self._inflight = {}

    async def get_forecast(self, location: str) -> Dict[str, Any]:
        """Fetches 48-hour weather forecast."""
        location_key = (location or "").strip().lower()
        cache_key = f"forecast:{location_key}:metric:16"
        now = time.time()

        cached = self._cache.get(cache_key)
        if cached and (now - cached["ts"]) <= self.cache_ttl_seconds:
            return cached["data"]

        if cache_key in self._inflight:
            return await self._inflight[cache_key]

        if not self.api_key:
            # Mock data for demonstration if API key is missing
            data = {
                "list": [
                    {"dt_txt": "2025-11-01 12:00:00", "main": {"temp": 25, "humidity": 60}, "weather": [{"main": "Clear"}], "wind": {"speed": 5}},
                    {"dt_txt": "2025-11-02 12:00:00", "main": {"temp": 22, "humidity": 80}, "weather": [{"main": "Rain"}], "wind": {"speed": 12}}
                ]
            }
            self._cache[cache_key] = {"ts": now, "data": data}
            return data

        async def _do_fetch():
            async with httpx.AsyncClient() as client:
                params = {
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric",
                    "cnt": 16 # 16 * 3 hours = 48 hours
                }
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                self._cache[cache_key] = {"ts": time.time(), "data": data}
                return data

        task = asyncio.create_task(_do_fetch())
        self._inflight[cache_key] = task
        try:
            return await task
        finally:
            self._inflight.pop(cache_key, None)
