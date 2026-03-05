from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from app.db.database import get_db
from app.models.request_models import UserLoginRequest, UserRegisterRequest, GoogleAuthRequest
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
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, full_name, mobile_number, picture FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user is None:
            raise credentials_exception
        return dict(user)

@router.post("/register", response_model=UserResponse)
async def register(request: UserRegisterRequest):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (request.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already registered")
        
        hashed_password = get_password_hash(request.password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, full_name, mobile_number) VALUES (?, ?, ?, ?)",
            (request.username, hashed_password, request.full_name, request.mobile_number)
        )
        conn.commit()
        user_id = cursor.lastrowid
        
        return {
            "id": user_id,
            "username": request.username,
            "full_name": request.full_name,
            "mobile_number": request.mobile_number
        }

@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, password_hash FROM users WHERE username = ?", (request.username,))
        user = cursor.fetchone()
        
        if not user or not verify_password(request.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": user["username"]})
        return {"access_token": access_token, "token_type": "bearer"}

@router.post("/google", response_model=TokenResponse)
async def google_auth(request: GoogleAuthRequest):
    try:
        # Verify the ID Token
        id_info = google_id_token.verify_oauth2_token(
            request.id_token, 
            google_requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )

        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # Extract user info
        google_id = id_info['sub']
        email = id_info['email']
        name = id_info.get('name')
        picture = id_info.get('picture')

        with get_db() as conn:
            cursor = conn.cursor()
            # Check if user exists
            cursor.execute("SELECT username FROM users WHERE google_id = ? OR email = ?", (google_id, email))
            user = cursor.fetchone()

            if not user:
                # Register new user
                username = email.split('@')[0]
                cursor.execute(
                    "INSERT INTO users (username, email, google_id, full_name, picture) VALUES (?, ?, ?, ?, ?)",
                    (username, email, google_id, name, picture)
                )
                conn.commit()
                username_final = username
            else:
                username_final = user["username"]

            access_token = create_access_token(data={"sub": username_final})
            return {"access_token": access_token, "token_type": "bearer"}

    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid Google Token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Auth Error: {str(e)}")

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
