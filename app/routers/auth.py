from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import uuid
from datetime import datetime
from app.db.database import get_db
from app.models.request_models import UserLoginRequest, UserRegisterRequest
from app.models.response_models import TokenResponse, UserResponse
from app.services.auth_service import verify_password, get_password_hash, create_access_token
from app.config import settings

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    with get_db() as db:
        user = db.get_item_by_username(username)
        if user is None:
            raise credentials_exception
        return user

@router.post("/register", response_model=UserResponse)
async def register(request: UserRegisterRequest):
    with get_db() as db:
        # Check if username already exists
        existing_user = db.get_item_by_username(request.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(request.password)
        user_data = {
            "user_id": user_id,
            "username": request.username,
            "password_hash": hashed_password,
            "full_name": request.full_name,
            "mobile_number": request.mobile_number,
            "created_at": datetime.utcnow().isoformat()
        }
        
        if not db.put_item(user_data):
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        return {
            "user_id": user_id,
            "username": request.username,
            "full_name": request.full_name,
            "mobile_number": request.mobile_number
        }

@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest):
    with get_db() as db:
        user = db.get_item_by_username(request.username)
        
        if not user or not verify_password(request.password, user.get("password_hash", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": user["username"]})
        return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
