from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base


class TicketStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TicketPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


def utc_now() -> datetime:
    return datetime.now(UTC)


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[TicketStatus] = mapped_column(
        SqlEnum(
            TicketStatus,
            values_callable=lambda enum_class: [item.value for item in enum_class],
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        default=TicketStatus.NEW,
        index=True,
    )

    priority: Mapped[TicketPriority] = mapped_column(
        SqlEnum(
            TicketPriority,
            values_callable=lambda enum_class: [item.value for item in enum_class],
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        default=TicketPriority.NORMAL,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )
