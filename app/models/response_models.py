from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TodayResponse(BaseModel):
    do: List[str]
    avoid: List[str]
    prepare: List[str]
    weather_risk: Dict[str, Any]
    confidence_score: float
    sources: List[str] = []

class SellSmartResponse(BaseModel):
    best_mandi: str
    net_price: float
    trend_7d: str
    forecast_band: str
    confidence_score: float

class ChatResponse(BaseModel):
    answer: str
    confidence_score: float
    citations: Optional[List[str]] = []

class SchemeResponse(BaseModel):
    eligible_schemes: List[str]
    documents_required: List[str]
    application_links: List[str]
