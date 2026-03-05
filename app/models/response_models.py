from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TodayResponse(BaseModel):
    do: List[str] = Field(..., description="List of recommended actions for today")
    avoid: List[str] = Field(..., description="List of actions to avoid today")
    prepare: List[str] = Field(..., description="Preparation steps for upcoming days")
    weather_risk: Dict[str, Any] = Field(..., description="Weather risk details")
    confidence_score: float = Field(..., ge=0, le=1)
    sources: List[str] = Field(default=[], description="Information sources")

class SellSmartResponse(BaseModel):
    best_mandi: str = Field(..., description="Name of the best market to sell")
    net_price: float = Field(..., description="Expected net price per unit")
    trend_7d: str = Field(..., description="7-day price trend")
    forecast_band: str = Field(..., description="Forecasted price range")
    confidence_score: float = Field(..., ge=0, le=1)

class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI generated answer to the question")
    confidence_score: float = Field(..., ge=0, le=1)
    citations: List[str] = Field(default=[], description="Source document links")

class SchemeResponse(BaseModel):
    eligible_schemes: List[str] = Field(..., description="List of eligible government schemes")
    documents_required: List[str] = Field(..., description="Required documents for application")
    application_links: List[str] = Field(..., description="Links to apply for the schemes")
