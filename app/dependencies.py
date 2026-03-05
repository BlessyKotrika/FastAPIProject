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
