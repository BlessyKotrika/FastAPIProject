import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # AWS Credentials
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN: Optional[str] = os.getenv("AWS_SESSION_TOKEN")

    # AWS Settings
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    DYNAMODB_TABLE_USERS: str = os.getenv("DYNAMODB_TABLE_USERS", "Users")
    DYNAMODB_TABLE_ADVISORY: str = os.getenv("DYNAMODB_TABLE_ADVISORY", "AdvisoryHistory")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "khetipulse-data")
    BEDROCK_KB_ID: str = os.getenv("BEDROCK_KB_ID", "")
    
    # Bedrock Model IDs
    CLAUDE_MODEL_ID: str = os.getenv("CLAUDE_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    TITAN_EMBED_MODEL_ID: str = "amazon.titan-embed-text-v1"
    
    # Mandi API
    AGMARKNET_API_KEY: str = os.getenv("AGMARKNET_API_KEY", "579b464db66ec23bdd000001fee029797c5f45b9462e3f8d384d4730")
    AGMARKNET_RESOURCE_ID: str = "35985678-0d79-46b4-9ed6-6f13308a1d24"
    
    # API Keys
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    
    # App Settings
    APP_NAME: str = "KhetiPulse Backend"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    class Config:
        env_file = ".env"

settings = Settings()
