from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "KhetiPulse Backend"
    DEBUG: bool = False
    VERSION: str = "1.0.0"

    # AWS Credentials
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_SESSION_TOKEN: Optional[str] = None

    # AWS Settings
    AWS_REGION: str = "us-east-1"
    DYNAMODB_TABLE_USERS: str = "Users"
    DYNAMODB_TABLE_ADVISORY: str = "AdvisoryHistory"
    S3_BUCKET_NAME: str = "khetipulse-data"
    BEDROCK_KB_ID: str = ""
    
    # Bedrock Model IDs
    CLAUDE_MODEL_ID: str = "anthropic.claude-3-haiku-20240307-v1:0"
    TITAN_EMBED_MODEL_ID: str = "amazon.titan-embed-text-v1"
    
    # Mandi API
    AGMARKNET_API_KEY: str = Field(
        default="579b464db66ec23bdd000001fee029797c5f45b9462e3f8d384d4730",
        description="Public API key for Agmarknet"
    )
    AGMARKNET_RESOURCE_ID: str = "35985678-0d79-46b4-9ed6-6f13308a1d24"
    
    # API Keys
    OPENWEATHER_API_KEY: str = ""

    # JWT Settings
    SECRET_KEY: str = "khetipulse-super-secret-key-replace-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
