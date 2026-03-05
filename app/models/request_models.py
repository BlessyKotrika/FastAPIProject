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
    language: Language = Field(default=Language.HINDI)

class ChatRequest(BaseModel):
    question: str = Field(..., example="When should I harvest my wheat?")
    language: Language = Field(default=Language.HINDI)
    crop: Optional[str] = Field(None, example="Wheat")
    location: Optional[str] = Field(None, example="Barabanki")

class SchemeRequest(BaseModel):
    state: str = Field(..., example="Uttar Pradesh")
    land_size: float = Field(..., gt=0, example=2.5)
    category: str = Field(..., example="Small")
    crop: str = Field(..., example="Wheat")
    language: Language = Field(default=Language.HINDI)

class LanguagePreferenceRequest(BaseModel):
    user_id: str = Field(..., example="user_123")
    language: Language = Field(..., description="Preferred language")
