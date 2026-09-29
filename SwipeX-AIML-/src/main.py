from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.router import api_v1_router
from backend.app.core.config import settings

app = FastAPI(
    title="SwipeX Career Intelligence API",
    description="AI/ML Career Intelligence Service providing resume parsing, ATS scoring, job recommendations, swipe analytics, and career insights.",
    version=settings.VERSION,
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "SwipeX AI/ML Career Intelligence",
        "version": settings.VERSION,
        "mode": settings.GENERATED_BY_TAG,
    }


@app.get("/", tags=["System"])
def root():
    return {
        "message": "Welcome to SwipeX AI/ML Career Intelligence Service",
        "docs": "/docs",
        "health": "/health",
        "api_v1": settings.API_V1_STR,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
