import boto3
from app.config import settings

def get_db_client():
    return boto3.resource('dynamodb', region_name=settings.AWS_REGION)

def get_user_table():
    db = get_db_client()
    return db.Table(settings.DYNAMODB_TABLE_USERS)

def get_advisory_table():
    db = get_db_client()
    return db.Table(settings.DYNAMODB_TABLE_ADVISORY)

# Service Dependencies
from app.services.bedrock_service import BedrockService
from app.services.rag_service import RAGService
from app.services.weather_service import WeatherService
from app.services.mandi_service import MandiService
from app.services.recommendation_engine import RecommendationEngine

# Pre-instantiate services (could also be done per-request if needed)
_bedrock_service = BedrockService()
_rag_service = RAGService(_bedrock_service)
_weather_service = WeatherService()
_mandi_service = MandiService()
_recommendation_engine = RecommendationEngine(_weather_service, _mandi_service, _bedrock_service)

def get_bedrock_service() -> BedrockService:
    return _bedrock_service

def get_rag_service() -> RAGService:
    return _rag_service

def get_weather_service() -> WeatherService:
    return _weather_service

def get_mandi_service() -> MandiService:
    return _mandi_service

def get_recommendation_engine() -> RecommendationEngine:
    return _recommendation_engine
