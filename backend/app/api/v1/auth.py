from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.security import create_access_token
from backend.app.db.database import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import AdminUserResponse, LoginRequest, TokenResponse
from backend.app.services.auth_service import authenticate_user, get_current_admin

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Admin login",
    responses={
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid username or password."
                    }
                }
            },
        }
    },
)
def login(
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    user = authenticate_user(
        db=db,
        username=payload.username,
        password=payload.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    access_token = create_access_token(
        subject=user.username,
        extra_claims={"is_admin": user.is_admin},
    )

    return TokenResponse(access_token=access_token)


@router.get(
    "/me",
    response_model=AdminUserResponse,
    summary="Get current admin user",
    responses={
        401: {
            "description": "Missing or invalid token",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Could not validate authentication credentials."
                    }
                }
            },
        },
        403: {
            "description": "User is not admin",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Admin privileges are required."
                    }
                }
            },
        },
    },
)
def get_me(
    current_admin: Annotated[User, Depends(get_current_admin)],
) -> AdminUserResponse:
    return AdminUserResponse.model_validate(current_admin)
