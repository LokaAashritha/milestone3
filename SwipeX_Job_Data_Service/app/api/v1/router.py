from fastapi import APIRouter
from app.api.v1 import jobs, swipes, companies, saved_jobs, resumes, ats

api_router = APIRouter()

api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs & Feed"])
api_router.include_router(swipes.router, prefix="/swipes", tags=["Swipes & Interactions"])
api_router.include_router(companies.router, prefix="/companies", tags=["Companies & Startups"])
api_router.include_router(saved_jobs.router, prefix="/saved-jobs", tags=["Saved Jobs & Bookmarks"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["Resumes & Versions"])
api_router.include_router(ats.router, prefix="/ats", tags=["ATS Scoring & Compatibility"])
