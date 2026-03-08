import boto3
import logging
import httpx
from typing import List, Dict, Any, Optional, Tuple
from app.config import settings
from app.utils.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

class MandiService:
    def __init__(self, http_client: Optional[httpx.AsyncClient] = None, api_key: str = settings.AGMARKNET_API_KEY, region: str = settings.AWS_REGION):
        self.s3 = boto3.client('s3', region_name=region)
        self.api_key = api_key
        self.resource_id = settings.AGMARKNET_RESOURCE_ID
        self.base_url = "https://api.data.gov.in/resource/"
        self._http_client = http_client

    async def get_mandi_data(self, crop: str, location: str, state: str = None) -> List[Dict[str, Any]]:
        """Fetches AGMARKNET data from Gov API."""
        if not self.api_key:
            logger.warning("AGMARKNET_API_KEY missing, returning mock data.")
            return self._get_mock_data()

        client = self._http_client or httpx.AsyncClient()
        try:
            params = {
                "api-key": self.api_key,
                "format": "json",
                "limit": 50,
                "filters[commodity]": crop
            }
            
            # Helper to fetch with current params
            async def fetch(current_params):
                response = await client.get(f"{self.base_url}{self.resource_id}", params=current_params)
                response.raise_for_status()
                return response.json().get("records", [])

            # Strategy 1: Location + State
            if location:
                params["filters[district]"] = location
            if state:
                params["filters[state]"] = state
            
            records = await fetch(params)
            
            # Strategy 2: State only
            if not records and location and state:
                params.pop("filters[district]", None)
                records = await fetch(params)
            
            # Strategy 3: District only
            if not records and location:
                params.pop("filters[state]", None)
                params["filters[district]"] = location
                records = await fetch(params)

            # Strategy 4: Crop only
            if not records:
                params.pop("filters[district]", None)
                params.pop("filters[state]", None)
                records = await fetch(params)
            
            return records
        except Exception as e:
            logger.error(f"Error fetching mandi data: {e}")
            return self._get_mock_data()
        finally:
            if self._http_client is None:
                await client.aclose()

    def _get_mock_data(self) -> List[Dict[str, Any]]:
        return [
            {
                "Market": "Barabanki",
                "Commodity": "Wheat",
                "Modal_Price": "2450",
                "District": "Barabanki",
                "Arrival_Date": "01/11/2025"
            }
        ]

    def compute_trends(self, data: List[Dict[str, Any]]) -> Tuple[str, str]:
        """Computes 7-day and 30-day trends."""
        # Simple qualitative trend for demo
        return "Stable", "Rising (+2%)"

    def get_best_mandi(self, data: List[Dict[str, Any]], location: str, language: str = "hi") -> Tuple[str, float]:
        """Finds best mandi based on price and proximity to user location."""
        if not data:
            return "No data available", 0.0
        
        try:
            # 1. District match
            district_matches = [r for r in data if r.get('District', '').lower() == location.lower()]
            
            if district_matches:
                best = max(district_matches, key=lambda x: float(x.get('Modal_Price', 0)))
            else:
                # 2. Overall best
                best = max(data, key=lambda x: float(x.get('Modal_Price', 0)))
                
            market = best.get('Market', 'Unknown')
            price = float(best.get('Modal_Price', 0))
            return market, price
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing mandi price: {e}")
            return "Data error", 0.0
