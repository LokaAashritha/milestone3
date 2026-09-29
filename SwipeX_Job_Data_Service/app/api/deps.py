from typing import Generator, Optional
from fastapi import Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.cache import cache_manager, CacheManager


def get_cache() -> CacheManager:
    """Dependency to inject the cache manager."""
    return cache_manager


def get_current_user_id(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id", description="User ID for authentication/identification"),
    authorization: Optional[str] = Header(None, alias="Authorization", description="Bearer JWT token or user info")
) -> str:
    """
    Extracts or defaults user_id. In Milestone 1, if Intern 1's JWT is passed,
    or custom X-User-Id header is passed, it is used; otherwise defaults to 'demo-user-1'.
    """
    if x_user_id:
        return x_user_id
    if authorization and authorization.startswith("Bearer "):
        # Basic token fallback for M1 before full JWT middleware
        token = authorization.replace("Bearer ", "").strip()
        if token and len(token) < 50:
            return token
    return "demo-user-1"
