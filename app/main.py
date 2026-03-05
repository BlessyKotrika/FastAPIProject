import logging
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.routers import today, sell, chat, schemes, preferences
from app.config import settings

# Structured Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered multilingual farmer decision support system",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error Handling Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Path: {request.url.path} Method: {request.method}")
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

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
