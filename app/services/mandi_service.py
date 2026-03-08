import boto3
import httpx
from app.config import settings
from app.utils.exceptions import ExternalServiceError


class MandiService:
    def __init__(self, api_key: str = settings.AGMARKNET_API_KEY, region: str = settings.AWS_REGION):
        self.s3 = boto3.client('s3', region_name=region)
        self.api_key = api_key
        self.resource_id = settings.AGMARKNET_RESOURCE_ID
        self.base_url = "https://api.data.gov.in/resource/"

    async def get_mandi_data(self, crop: str, location: str, state: str = None):
        """Fetches AGMARKNET data from Gov API."""
        try:
            params = {
                "api-key": self.api_key,
                "format": "json",
                "limit": 50,
                "filters[commodity]": crop
            }
            if location:
                params["filters[district]"] = location
            if state:
                params["filters[state]"] = state

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{self.base_url}{self.resource_id}", params=params)
                response.raise_for_status()
                data = response.json()

                records = data.get("records", [])
                if not records:
                    # District + State -> State only
                    if location and state:
                        params.pop("filters[district]", None)
                        response = await client.get(f"{self.base_url}{self.resource_id}", params=params)
                        response.raise_for_status()
                        records = response.json().get("records", [])

                    # State only -> District only
                    if not records and location:
                        if state:
                            params["filters[district]"] = location
                            params.pop("filters[state]", None)
                        response = await client.get(f"{self.base_url}{self.resource_id}", params=params)
                        response.raise_for_status()
                        records = response.json().get("records", [])

                    # District only -> Crop only
                    if not records:
                        params.pop("filters[district]", None)
                        params.pop("filters[state]", None)
                        response = await client.get(f"{self.base_url}{self.resource_id}", params=params)
                        response.raise_for_status()
                        records = response.json().get("records", [])

                return records

        except Exception as e:
            raise ExternalServiceError("AGMARKNET API", detail=str(e))

    def compute_trends(self, data):
        return "Stable", "Rising (+2%)"

    def get_best_mandi(self, data, location: str, language: str = "hi"):
        if not data:
            return "No data available", 0

        district_matches = [r for r in data if r.get('District', '').lower() == location.lower()]

        if district_matches:
            best = max(district_matches, key=lambda x: float(x.get('Modal_Price', 0)))
        else:
            best = max(data, key=lambda x: float(x.get('Modal_Price', 0)))

        market = best.get('Market', 'Unknown')
        price = float(best.get('Modal_Price', 0))

        return market, price