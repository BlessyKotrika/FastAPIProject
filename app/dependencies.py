import boto3
from fastapi import Depends
from app.config import settings

def get_db_client():
    return boto3.resource('dynamodb', region_name=settings.AWS_REGION)

def get_user_table():
    db = get_db_client()
    return db.Table(settings.DYNAMODB_TABLE_USERS)

def get_advisory_table():
    db = get_db_client()
    return db.Table(settings.DYNAMODB_TABLE_ADVISORY)

from app.utils.http_client import get_http_client

# Service Dependencies
from app.services.bedrock_service import BedrockService
from app.services.rag_service import RAGService
from app.services.weather_service import WeatherService
from app.services.mandi_service import MandiService
from app.services.recommendation_engine import RecommendationEngine
from app.services.chat_history_service import ChatHistoryService

# Pre-instantiate services (could also be done per-request if needed)
_bedrock_service = None
_rag_service = None
_chat_history_service = None

def get_bedrock_service() -> BedrockService:
    global _bedrock_service
    if _bedrock_service is None:
        _bedrock_service = BedrockService()
    return _bedrock_service

def get_rag_service(bedrock: BedrockService = Depends(get_bedrock_service)) -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService(bedrock)
    return _rag_service

def get_chat_history_service() -> ChatHistoryService:
    global _chat_history_service
    if _chat_history_service is None:
        _chat_history_service = ChatHistoryService()
    return _chat_history_service

async def get_weather_service(http_client = Depends(get_http_client)) -> WeatherService:
    return WeatherService(http_client=http_client)

async def get_mandi_service(http_client = Depends(get_http_client)) -> MandiService:
    return MandiService(http_client=http_client)

async def get_recommendation_engine(
    bedrock: BedrockService = Depends(get_bedrock_service),
    weather: WeatherService = Depends(get_weather_service),
    mandi: MandiService = Depends(get_mandi_service)
) -> RecommendationEngine:
    return RecommendationEngine(weather, mandi, bedrock)

async def get_chat_history_service() -> ChatHistoryService:
    return _chat_history_service