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
    all_markets: List[Dict[str, Any]] = Field(default=[], description="List of all available markets")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI generated answer to the question")
    confidence_score: float = Field(..., ge=0, le=1)
    citations: List[str] = Field(default=[], description="Source document links")

class SchemeItem(BaseModel):
    name: str = Field(..., description="Name of the government scheme")
    description: str = Field(..., description="Brief description of the scheme")
    documents: List[str] = Field(..., description="Required documents for this specific scheme")
    link: str = Field(..., description="Application link for this specific scheme")

class SchemeResponse(BaseModel):
    schemes: List[SchemeItem] = Field(..., description="List of eligible government schemes with their details")
    # Maintain backward compatibility if needed, but the user wants it under each
    eligible_schemes: List[str] = Field(default=[], description="List of eligible government scheme names")
    documents_required: List[str] = Field(default=[], description="Global required documents (optional)")
    application_links: List[str] = Field(default=[], description="Global application links (optional)")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    user_id: str
    username: str
    full_name: Optional[str] = None
    mobile_number: Optional[str] = None
