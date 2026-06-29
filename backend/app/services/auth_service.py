from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.core.security import verify_password
from backend.app.db.database import get_db
from backend.app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def authenticate_user(
    db: Session,
    username: str,
    password: str,
) -> User | None:
    user = db.scalar(select(User).where(User.username == username))

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise credentials_exception()

    settings = get_settings()

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise credentials_exception() from exc

    username = payload.get("sub")

    if not isinstance(username, str) or not username:
        raise credentials_exception()

    user = db.scalar(select(User).where(User.username == username))

    if user is None:
        raise credentials_exception()

    return user


def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges are required.",
        )

    return current_user
