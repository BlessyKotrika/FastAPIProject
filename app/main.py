import logging
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.routers import today, sell, chat, schemes, preferences
from app.config import settings
from app.utils.exceptions import KhetiPulseException

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
    allow_origins=["*"],
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
app.include_router(preferences.router, prefix="/preferences", tags=["User Preferences"])
app.include_router(today.router, prefix="/today", tags=["Today Actions"])
app.include_router(sell.router, prefix="/sell-smart", tags=["Sell Smart"])
app.include_router(chat.router, prefix="/chat", tags=["Ask KhetiPulse"])
app.include_router(schemes.router, prefix="/schemes", tags=["Schemes"])

@app.get("/")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}

# Lambda Handler
handler = Mangum(app)
