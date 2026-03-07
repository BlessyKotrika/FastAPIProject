from typing import Optional
import boto3
import json
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

def get_secret(secret_name: str, region_name: str = "us-east-1") -> str:
    """Retrieve secret from AWS Secrets Manager."""
    client = boto3.client("secretsmanager", region_name=region_name)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        if 'SecretString' in response:
            return response['SecretString']
        else:
            # Binary secret
            return response['SecretBinary'].decode('utf-8')
    except Exception as e:
        print(f"Error retrieving secret {secret_name}: {e}")
        return ""

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
    # Hardcoded table names
    DYNAMODB_TABLE_USERS: str = "Users"
    DYNAMODB_TABLE_ADVISORY: str = "AdvisoryHistory"
    
    # Secrets from AWS Secrets Manager
    S3_BUCKET_NAME: str = Field(default_factory=lambda: get_secret("/khetipulse/prod/S3_BUCKET_NAME"))
    BEDROCK_KB_ID: str = Field(default_factory=lambda: get_secret("/khetipulse/prod/BEDROCK_KB_ID"))
    
    # Bedrock Model IDs
    CLAUDE_MODEL_ID: str = "anthropic.claude-3-haiku-20240307-v1:0"
    TITAN_EMBED_MODEL_ID: str = "amazon.titan-embed-text-v1"
    
    # Mandi API - from Secrets Manager
    AGMARKNET_API_KEY: str = Field(default_factory=lambda: get_secret("/khetipulse/prod/AGMARKNET_API_KEY"))
    AGMARKNET_RESOURCE_ID: str = "35985678-0d79-46b4-9ed6-6f13308a1d24"
    
    # API Keys from Secrets Manager
    OPENWEATHER_API_KEY: str = Field(default_factory=lambda: get_secret("/khetipulse/prod/OPENWEATHER_API_KEY"))

    # JWT Settings
    SECRET_KEY: str = Field(default_factory=lambda: get_secret("/khetipulse/prod/SECRET_KEY"))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    # CORS Settings
    CORS_ORIGINS: str = "*"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
