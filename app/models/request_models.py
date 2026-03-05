from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class UserBase(BaseModel):
    user_id: str
    crop: str
    location: str
    language: str = "hi"

class TodayRequest(UserBase):
    sowing_date: str

class SellSmartRequest(BaseModel):
    crop: str
    location: str
    language: str = "hi"

class ChatRequest(BaseModel):
    question: str
    language: str = "hi"
    crop: Optional[str] = None
    location: Optional[str] = None

class SchemeRequest(BaseModel):
    state: str
    land_size: float
    category: str
    crop: str
    language: str = "hi"

class LanguagePreferenceRequest(BaseModel):
    user_id: str
    language: str = Field(..., description="Preferred language: hi, en, te, ta, bn")
