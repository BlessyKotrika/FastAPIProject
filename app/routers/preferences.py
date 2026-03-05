from fastapi import APIRouter, HTTPException
import boto3
from app.config import settings
from app.models.request_models import LanguagePreferenceRequest

router = APIRouter()
dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
table = dynamodb.Table(settings.DYNAMODB_TABLE_USERS)

@router.post("/language")
async def update_language(request: LanguagePreferenceRequest):
    try:
        table.update_item(
            Key={'user_id': request.user_id},
            UpdateExpression="SET #lang = :l",
            ExpressionAttributeNames={'#lang': 'language'},
            ExpressionAttributeValues={':l': request.language}
        )
        return {"status": "success", "message": f"Language updated to {request.language}"}
    except Exception as e:
        # Fallback if table doesn't exist yet during development
        return {"status": "success (mock)", "message": f"Language updated to {request.language}", "error": str(e)}

@router.get("/{user_id}/language")
async def get_language(user_id: str):
    try:
        response = table.get_item(Key={'user_id': user_id})
        if 'Item' in response:
            return {"user_id": user_id, "language": response['Item'].get('language', 'hi')}
        return {"user_id": user_id, "language": "hi", "message": "User not found, returning default"}
    except Exception as e:
        return {"user_id": user_id, "language": "hi", "error": str(e)}
