import logging
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.routers import onboarding, today, sell, chat, schemes, preferences, auth, profile
from app.config import settings
from app.utils.exceptions import KhetiPulseException

from app.utils.http_client import HttpClientManager

# Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered multilingual farmer decision support system",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.on_event("shutdown")
async def shutdown_event():
    await HttpClientManager.close_client()

# Exception Handlers
@app.exception_handler(KhetiPulseException)
async def khetipulse_exception_handler(request: Request, exc: KhetiPulseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "message": exc.message,
            "extra": exc.extra
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for Pydantic validation errors to return a string detail."""
    errors = exc.errors()
    # Format the first error into a readable string
    if errors:
        error = errors[0]
        field = " -> ".join([str(l) for l in error.get("loc", []) if l != "body"])
        msg = error.get("msg")
        detail = f"Validation Error: {field} {msg}" if field else f"Validation Error: {msg}"
    else:
        detail = "Validation Error"
        
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if hasattr(settings, 'CORS_ORIGINS') and settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Path: {request.url.path} Method: {request.method}")
    response = await call_next(request)
    return response

# Routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(profile.router, prefix="", tags=["User Profile"])
app.include_router(preferences.router, prefix="/preferences", tags=["User Preferences"])
app.include_router(onboarding.router, prefix="/onboarding", tags=["Onboarding"])
app.include_router(today.router, prefix="/today", tags=["Today Actions"])
app.include_router(sell.router, prefix="/sell-smart", tags=["Sell Smart"])
app.include_router(chat.router, prefix="/chat", tags=["Ask KhetiPulse"])
app.include_router(schemes.router, prefix="/schemes", tags=["Schemes"])

@app.get("/")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}

# For local development and ECS deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
