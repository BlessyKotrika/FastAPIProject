from fastapi import APIRouter, HTTPException, Depends
from app.models.request_models import LanguagePreferenceRequest
from app.dependencies import get_user_table

router = APIRouter()

@router.post("/language")
async def update_language(request: LanguagePreferenceRequest, table = Depends(get_user_table)):
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
async def get_language(user_id: str, table = Depends(get_user_table)):
    try:
        response = table.get_item(Key={'user_id': user_id})
        if 'Item' in response:
            return {"user_id": user_id, "language": response['Item'].get('language', 'hi')}
        return {"user_id": user_id, "language": "hi", "message": "User not found, returning default"}
    except Exception as e:
        return {"user_id": user_id, "language": "hi", "error": str(e)}
