from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class Language(str, Enum):
    HINDI = "hi"
    ENGLISH = "en"
    TELUGU = "te"
    TAMIL = "ta"
    BENGALI = "bn"

class UserBase(BaseModel):
    user_id: str = Field(..., example="user_123")
    crop: str = Field(..., example="Wheat")
    location: str = Field(..., example="Barabanki")
    language: Language = Field(default=Language.HINDI)

class TodayRequest(UserBase):
    sowing_date: str = Field(..., example="2024-10-15")

class SellSmartRequest(BaseModel):
    crop: str = Field(..., example="Wheat")
    location: str = Field(..., example="Barabanki")
    state: Optional[str] = Field(None, example="Uttar Pradesh")
    language: Language = Field(default=Language.HINDI)

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, example="When should I harvest my wheat?")
    language: Language = Field(default=Language.HINDI)
    crop: Optional[str] = Field(None, example="Wheat")
    location: Optional[str] = Field(None, example="Barabanki")

    # New fields for conversation continuity
    conversation_id: Optional[str] = Field(
        None,
        description="Existing conversation id for multi-turn chat",
        example="conv_1f8f0f3a"
    )
    client_message_id: Optional[str] = Field(
        None,
        description="Client-generated idempotency key for this user message",
        example="msg_client_123"
    )
    advisory_mode: Optional[str] = Field("llm", description="llm or schemes")

class SchemeRequest(BaseModel):
    state: str = Field(..., example="Uttar Pradesh")
    land_size: float = Field(..., gt=0, example=2.5)
    category: str = Field(..., example="Small")
    crop: str = Field(..., example="Wheat")
    language: Language = Field(default=Language.HINDI)

class LanguagePreferenceRequest(BaseModel):
    user_id: str = Field(..., example="user_123")
    language: Language = Field(..., description="Preferred language")

class UserLoginRequest(BaseModel):
    username: str = Field(..., example="farmer_john")
    password: str = Field(..., example="secure_password")

class UserRegisterRequest(BaseModel):
    username: str = Field(..., example="farmer_john")
    password: str = Field(..., min_length=6, example="secure_password")
    full_name: Optional[str] = Field(None, example="John Doe")
    mobile_number: Optional[str] = Field(None, example="9876543210")
