from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    LoginResponse,
)



router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


DASHBOARD_PATHS = {
    "SALES": "/sales/dashboard",
    "ACCOUNT_DIRECTOR": "/account-director/dashboard",
    "PRESALES": "/presales/dashboard",
    "RESOURCE_MANAGER": "/resource-manager/dashboard",
    "EXECUTIVE": "/executive/dashboard",
}


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    normalized_email = login_data.email.strip().lower()

    user = db.scalar(
        select(User)
        .options(joinedload(User.role))
        .where(User.email == normalized_email)
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(
        login_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    if not user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have an assigned role",
        )

    if not user.role.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Assigned role is inactive",
        )

    role_name = user.role.name

    dashboard_path = DASHBOARD_PATHS.get(role_name)

    if not dashboard_path:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role is not allowed to access the CRM",
        )

    access_token = create_access_token(
        subject=str(user.id),
        additional_claims={
            "email": user.email,
            "role": role_name,
        },
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        dashboard_path=dashboard_path,
        user={
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": role_name,
        },
    )

@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
def get_logged_in_user(
    current_user: User = Depends(get_current_user),
):
    role_name = current_user.role.name

    return CurrentUserResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        role=role_name,
        dashboard_path=DASHBOARD_PATHS[role_name],
    )