"""
app/controllers/auth_controller.py

Handles user registration, login, token refresh, and "who am I" endpoints.
Mounted at /api/v1/auth by app/routes.py.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    AccessTokenResponse,
    UserOut,
)
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_current_user,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user (Job Seeker, Recruiter, or Admin)",
)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists",
        )

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        skills=payload.skills or [],
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        subject=str(user.id),
        role=user.role.value,
        extra_claims={"id": str(user.id), "email": user.email, "skills": user.skills or []},
    )
    refresh_token = create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserOut.model_validate(user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate with email + password and receive JWT tokens",
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username.lower()).first()
    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been disabled. Contact an administrator.",
        )

    access_token = create_access_token(
        subject=str(user.id),
        role=user.role.value,
        extra_claims={"id": str(user.id), "email": user.email, "skills": user.skills or []},
    )
    refresh_token = create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserOut.model_validate(user),
    )


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Exchange a valid refresh token for a new access token",
)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    token_payload = decode_refresh_token(payload.refresh_token)
    user_id = token_payload.get("sub")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account has been disabled")

    new_access_token = create_access_token(
        subject=str(user.id),
        role=user.role.value,
        extra_claims={"id": str(user.id), "email": user.email, "skills": user.skills or []},
    )
    return AccessTokenResponse(access_token=new_access_token)


@router.get(
    "/me",
    response_model=UserOut,
    responses={
        200: {"description": "Current authenticated user"},
        401: {"model": dict, "description": "Authentication required"},
    },
    summary="Get the currently authenticated user's profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
