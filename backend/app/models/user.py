from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    username: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
