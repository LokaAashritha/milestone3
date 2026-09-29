"""
app/routes.py

Unified Single Gateway Entry Point.

All service routers are mounted here, under a single top-level APIRouter
that main.py includes with the "/api/v1" prefix:

    /api/v1/auth/*            -> Auth Service
    /api/v1/jobs/*            -> Job Service
    /api/v1/companies/*       -> Company Service
    /api/v1/swipes/*          -> Swipe Service
    /api/v1/recommendations/* -> Matching Engine / Recommendation Gateway
    /api/v1/resumes/*         -> Resume Service
    /api/v1/ats/*             -> ATS Scoring Service
"""
from fastapi import APIRouter

from app.controllers import (
    auth_controller,
    job_controller,
    company_controller,
    swipe_controller,
    recommendation_controller,
    resume_controller,
    ats_controller,
    saved_job_controller,
)

api_router = APIRouter()

api_router.include_router(
    auth_controller.router,
    prefix="/auth",
    tags=["Auth"],
)

api_router.include_router(
    job_controller.router,
    prefix="/jobs",
    tags=["Jobs"],
)

api_router.include_router(
    company_controller.router,
    prefix="/companies",
    tags=["Companies"],
)

api_router.include_router(
    swipe_controller.router,
    prefix="/swipes",
    tags=["Swipes"],
)

api_router.include_router(
    recommendation_controller.router,
    prefix="/recommendations",
    tags=["Recommendations"],
)

api_router.include_router(
    resume_controller.router,
    prefix="/resumes",
    tags=["Resumes"],
)

api_router.include_router(
    ats_controller.router,
    prefix="/ats",
    tags=["ATS Scoring"],
)

api_router.include_router(
    saved_job_controller.router,
    prefix="/saved-jobs",
    tags=["Saved Jobs"],
)