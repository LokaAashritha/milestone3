"""
app/main.py

Application entry point. Run with:

    uvicorn app.main:app --reload

Swagger UI will be available at http://127.0.0.1:8000/docs
ReDoc will be available at      http://127.0.0.1:8000/redoc
"""

import os
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.database import init_db
from app.routes import api_router

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("job_swipe_backend")

APP_NAME = os.getenv("APP_NAME", "Job Swipe Gateway API")
APP_ENV = os.getenv("APP_ENV", "development")
CORS_ORIGINS_RAW = os.getenv("CORS_ORIGINS", "http://localhost:5173")
configured_origins = [
    origin.strip() for origin in CORS_ORIGINS_RAW.split(",") if origin.strip()
]
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    *(origin for origin in configured_origins if origin != "*"),
]

app = FastAPI(
    title=APP_NAME,
    description=(
        "Unified backend gateway combining Auth/RBAC (Milestone 1) and "
        "Job Listings, Search, Swipes, Metrics, and Recommendations "
        "(Milestone 2) behind a single API surface."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    logger.info("Starting %s in '%s' mode", APP_NAME, APP_ENV)
    init_db()
    logger.info("Database tables verified/created successfully")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.get("/", tags=["Health"], summary="Root health check")
def root():
    return {
        "service": APP_NAME,
        "status": "ok",
        "environment": APP_ENV,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"], summary="Liveness/readiness probe")
def health():
    return {"status": "healthy"}


# Mount the unified gateway router
app.include_router(api_router, prefix="/api/v1")
