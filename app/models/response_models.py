from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

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

class SchemeItem(BaseModel):
    name: str = Field(..., description="Name of the government scheme")
    description: str = Field(..., description="Brief description of the scheme")
    documents: List[str] = Field(..., description="Required documents for this specific scheme")
    link: str = Field(..., description="Application link for this specific scheme")

class ChatMessageType(str, Enum):
    ADVICE = "advice"
    SCHEMES = "schemes"
    REFUSAL = "refusal"
    FALLBACK = "fallback"


class ChatResponse(BaseModel):
    # Conversation/thread metadata
    conversation_id: str = Field(..., description="Conversation id for continuing chat")
    message_id: str = Field(..., description="Assistant message id")

    # Message semantics
    message_type: ChatMessageType = Field(..., description="Type of assistant response")
    answer: str = Field(..., description="AI generated answer to the question")
    confidence_score: float = Field(..., ge=0, le=1)

    # Evidence
    citations: List[str] = Field(default_factory=list, description="Source document links")

    # Structured advisory blocks
    checklist: List[str] = Field(default_factory=list, description="3-step checklist")
    do: List[str] = Field(default_factory=list, description="Recommended actions")
    dont: List[str] = Field(default_factory=list, description="Actions to avoid")

    # Structured schemes output (if message_type == schemes)
    schemes: List[SchemeItem] = Field(default_factory=list, description="Eligible schemes with details")

    # Optional backward compatibility fields
    eligible_schemes: List[str] = Field(default_factory=list, description="Legacy list of scheme names")
    documents_required: List[str] = Field(default_factory=list, description="Legacy/global required documents")
    application_links: List[str] = Field(default_factory=list, description="Legacy/global application links")



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
