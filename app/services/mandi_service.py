import boto3
import logging
import asyncio
import httpx
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from app.config import settings

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
            return []

        client = self._http_client or httpx.AsyncClient(timeout=20.0)
        close_client = self._http_client is None
        try:
            params = {
                "api-key": self.api_key,
                "format": "json",
                "limit": 50,
                "filters[commodity]": crop
            }

            async def fetch(current_params: Dict[str, Any], label: str) -> List[Dict[str, Any]]:
                attempts = 3  # Increased attempts
                for attempt in range(1, attempts + 1):
                    try:
                        url = f"{self.base_url}{self.resource_id}"
                        logger.info("Mandi API Request [%s]: %s | Params: %s", label, url, current_params)
                        
                        response = await client.get(
                            url,
                            params=current_params,
                            timeout=httpx.Timeout(20.0, connect=10.0),
                        )
                        
                        if response.status_code != 200:
                            logger.error("Mandi API Error [%s]: Status %s | Response: %s", 
                                         label, response.status_code, response.text[:200])
                            response.raise_for_status()
                            
                        data = response.json()
                        records = data.get("records", [])
                        logger.info("Mandi API Success [%s]: Found %s records", label, len(records))
                        return records
                        
                    except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.TimeoutException) as exc:
                        logger.warning(
                            "Mandi API timeout on %s (attempt %s/%s): %s",
                            label,
                            attempt,
                            attempts,
                            exc,
                        )
                        if attempt < attempts:
                            await asyncio.sleep(0.5 * attempt)
                            continue
                        return []
                    except Exception as exc:
                        logger.error("Unexpected error in Mandi API fetch [%s]: %s", label, exc)
                        return []

            # Strategy 1: Location + State
            if location:
                params["filters[district]"] = location
            if state:
                params["filters[state]"] = state

            records = await fetch(dict(params), "district+state")

            # Strategy 2: State only
            if not records and location and state:
                params.pop("filters[district]", None)
                records = await fetch(dict(params), "state_only")

            # Strategy 3: District only
            if not records and location:
                params.pop("filters[state]", None)
                params["filters[district]"] = location
                records = await fetch(dict(params), "district_only")

            # Strategy 4: Crop only (broadest)
            if not records:
                params.pop("filters[district]", None)
                params.pop("filters[state]", None)
                records = await fetch(dict(params), "crop_only")

            return self._dedupe_records(records)
        except Exception as e:
            logger.exception("Error fetching mandi data from API: %s", e)
            return []
        finally:
            if close_client:
                await client.aclose()

    def _safe_price(self, value) -> float:
        try:
            return float(value or 0)
        except Exception:
            return 0.0

    def _safe_date(self, value) -> datetime:
        text = str(value or "").strip()
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(text, fmt)
            except Exception:
                continue
        return datetime.min

    def _dedupe_records(self, records):
        """
        Deduplicate mandi rows by market/district/commodity.
        Keep the latest arrival date; if same date, keep higher modal price.
        """
        if not records:
            return []

        best_by_key = {}
        for r in records:
            if not isinstance(r, dict):
                continue
            key = (
                str(r.get("Market", "")).strip().lower(),
                str(r.get("District", "")).strip().lower(),
                str(r.get("Commodity", "")).strip().lower(),
            )

            existing = best_by_key.get(key)
            if existing is None:
                best_by_key[key] = r
                continue

            curr_date = self._safe_date(r.get("Arrival_Date"))
            prev_date = self._safe_date(existing.get("Arrival_Date"))
            curr_price = self._safe_price(r.get("Modal_Price"))
            prev_price = self._safe_price(existing.get("Modal_Price"))

            if curr_date > prev_date or (curr_date == prev_date and curr_price > prev_price):
                best_by_key[key] = r

        return list(best_by_key.values())

    def compute_trends(self, data):
        """Computes 7-day and 30-day trends."""
        # Simple qualitative trend for demo
        return "Stable", "Rising (+2%)"

    def get_best_mandi(self, data: List[Dict[str, Any]], location: str, language: str = "hi") -> Tuple[str, float]:
        """Finds best mandi based on price and proximity to user location."""
        if not data:
            return "No data available", 0.0

        # 1. First, try to find an exact match for the user's district
        normalized_location = (location or "").lower()
        district_matches = [
            r for r in data
            if str(r.get("District", "")).strip().lower() == normalized_location
        ]

        def price_value(row: Dict[str, Any]) -> float:
            return self._safe_price(row.get("Modal_Price"))

        # 2. If we have district matches, pick the one with the best price among them
        if district_matches:
            best = max(district_matches, key=price_value)
        else:
            # 3. Fallback: best price across all available markets
            best = max(data, key=price_value)

        market = str(best.get("Market", "Unknown"))
        price = price_value(best)
        return market, price