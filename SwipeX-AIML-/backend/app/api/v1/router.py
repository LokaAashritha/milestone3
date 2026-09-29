from fastapi import APIRouter

from backend.app.api.v1.endpoints.career import router as career_router
from backend.app.api.v1.endpoints.recommendations import (
    router as recommendations_router,
)
from backend.app.api.v1.endpoints.resume import router as resume_router
from backend.app.api.v1.endpoints.swipes import router as swipes_router

api_v1_router = APIRouter()

api_v1_router.include_router(resume_router)
api_v1_router.include_router(recommendations_router)
api_v1_router.include_router(swipes_router)
api_v1_router.include_router(career_router)
