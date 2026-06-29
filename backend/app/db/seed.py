from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.core.security import hash_password
from backend.app.models.user import User


def seed_admin_user(db: Session) -> None:
    settings = get_settings()

    existing_admin = db.scalar(
        select(User).where(User.username == settings.admin_username)
    )

    if existing_admin is not None:
        return

    admin = User(
        username=settings.admin_username,
        hashed_password=hash_password(settings.admin_password),
        is_admin=True,
    )

    db.add(admin)
    db.commit()
