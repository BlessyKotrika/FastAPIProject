from fastapi import APIRouter, Depends, HTTPException
from app.models.request_models import UserProfileUpdateRequest
from app.models.response_models import UserResponse
from app.db.database import get_db
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def read_profile(current_user: dict = Depends(get_current_user)):
    # simply return the user item (will include profile fields)
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    update: UserProfileUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    # transform to dict excluding None
    data = {k: v for k, v in update.dict().items() if v is not None}

    # Keep backward compatibility between single crop and multi-crop profile fields.
    if "crops" in data and "crop" not in data:
        crops = [c for c in data["crops"] if isinstance(c, str) and c.strip()]
        data["crops"] = crops
        data["crop"] = crops[0] if crops else ""
    elif "crop" in data and "crops" not in data:
        crop = str(data["crop"]).strip()
        data["crop"] = crop
        data["crops"] = [crop] if crop else []

    with get_db() as db:
        success = db.update_profile(current_user['user_id'], data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update profile")
        # fetch updated item
        user = db.get_item(current_user['user_id'])
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
