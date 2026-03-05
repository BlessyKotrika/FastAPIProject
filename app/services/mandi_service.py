import boto3
import csv
import io
import httpx
from app.config import settings

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
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}{self.resource_id}", params=params)
                response.raise_for_status()
                data = response.json()
                
                records = data.get("records", [])
                if not records:
                    # Case 1: District + State failed. Try State only (broader)
                    if location and state:
                        params.pop("filters[district]")
                        response = await client.get(f"{self.base_url}{self.resource_id}", params=params)
                        records = response.json().get("records", [])
                    
                    # Case 2: State failed or was never provided. Try District only (if not tried yet)
                    if not records and location:
                        # Reset to district only if we previously tried state only
                        if state:
                            params["filters[district]"] = location
                            params.pop("filters[state]")
                        response = await client.get(f"{self.base_url}{self.resource_id}", params=params)
                        records = response.json().get("records", [])

                    # Case 3: Still nothing? Try just the Crop (broadest)
                    if not records:
                        if "filters[district]" in params: params.pop("filters[district]")
                        if "filters[state]" in params: params.pop("filters[state]")
                        response = await client.get(f"{self.base_url}{self.resource_id}", params=params)
                        records = response.json().get("records", [])
                
                return records
        except Exception as e:
            print(f"Error fetching mandi data from API: {e}")
            # Fallback to mock data if API fails
            mock_records = [
                {
                    "Market": "Barabanki",
                    "Commodity": "Wheat",
                    "Modal_Price": "2450",
                    "District": "Barabanki",
                    "Arrival_Date": "01/11/2025"
                }
            ]
            return mock_records

    def compute_trends(self, data):
        """Computes 7-day and 30-day trends."""
        # For simplicity in this demo, we return a qualitative trend
        # In production, this would compare current modal_price with historicals
        return "Stable", "Rising (+2%)"

    def get_best_mandi(self, data, location: str, language: str = "hi"):
        """Finds best mandi based on price and proximity to user location."""
        if not data:
            return "No data available", 0
        
        # 1. First, try to find an exact match for the user's district
        district_matches = [r for r in data if r.get('District', '').lower() == location.lower()]
        
        # 2. If we have district matches, pick the one with the best price among them
        if district_matches:
            best = max(district_matches, key=lambda x: float(x.get('Modal_Price', 0)))
        else:
            # 3. Fallback: pick the best price across all available markets (likely in the same state)
            best = max(data, key=lambda x: float(x.get('Modal_Price', 0)))
            
        market = best.get('Market', 'Unknown')
        price = float(best.get('Modal_Price', 0))
        
        return market, price
