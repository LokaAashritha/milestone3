import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal, run_migrations
from app.api.v1.router import api_router
from app.scripts.seed_data import seed_database
from app.core.cache import cache_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle handler.
    Auto-creates database tables, runs migrations, and seeds initial realistic dataset if needed.
    """
    logger.info("Initializing SwipeX Job & Data Intelligence Service...")
    run_migrations()
    
    # Auto-seed database if empty
    db = SessionLocal()
    try:
        seed_database(db)
    except Exception as e:
        logger.error(f"Seeding error on startup: {e}")
    finally:
        db.close()

    yield
    logger.info("Shutting down Job & Data Intelligence Service...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
# SwipeX — Job & Data Intelligence Service (Milestone 1)

This service manages the core data backbone for the SwipeX platform:
* **Rich Job Catalog**: Filter by company types (MNCs, Startups, Newly Founded), location, remote status, salary brackets, and skills.
* **Swipe Engine**: Record candidate interactions (Swipe Right = Apply/Save, Swipe Left = Skip).
* **Caching Layer**: Redis/Memory accelerated job feeds for high-throughput client swiping.
* **Full Integration Support**: Ready for API Gateway (Intern 1), ML Feature Engine (Intern 3), and Frontend (Intern 4).
    """,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health & Status"])
def root():
    return {
        "service": "SwipeX Job & Data Intelligence Service",
        "status": "online",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "api_v1_url": settings.API_V1_STR
    }


@app.get("/health", tags=["Health & Status"])
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "cache_type": "redis" if cache_manager._is_redis_available else "in-memory-fallback"
    }
