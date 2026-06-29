from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from backend.app.models.ticket import TicketPriority, TicketStatus


class TicketCreateRequest(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=120,
        examples=["е работает принтер в бухгалтерии"],
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        examples=["ринтер HP LaserJet не печатает документы после замены картриджа."],
    )
    priority: TicketPriority = Field(
        default=TicketPriority.NORMAL,
        examples=[TicketPriority.NORMAL],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "е работает принтер в бухгалтерии",
                "description": "ринтер HP LaserJet не печатает документы после замены картриджа.",
                "priority": "normal",
            }
        }
    )


class TicketStatusUpdateRequest(BaseModel):
    status: TicketStatus = Field(examples=[TicketStatus.IN_PROGRESS])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "in_progress",
            }
        }
    )


class TicketResponse(BaseModel):
    id: int = Field(examples=[1])
    title: str = Field(examples=["е работает принтер в бухгалтерии"])
    description: str | None = Field(
        default=None,
        examples=["ринтер HP LaserJet не печатает документы после замены картриджа."],
    )
    status: TicketStatus = Field(examples=[TicketStatus.NEW])
    priority: TicketPriority = Field(examples=[TicketPriority.NORMAL])
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedTicketsResponse(BaseModel):
    items: list[TicketResponse]
    total: int = Field(examples=[42])
    page: int = Field(examples=[1])
    page_size: int = Field(examples=[10])
    pages: int = Field(examples=[5])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1,
                        "title": "е работает принтер в бухгалтерии",
                        "description": "ринтер HP LaserJet не печатает документы после замены картриджа.",
                        "status": "new",
                        "priority": "normal",
                        "created_at": "2026-06-26T10:00:00Z",
                        "updated_at": "2026-06-26T10:00:00Z",
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 10,
                "pages": 1,
            }
        }
    )


SortBy = Literal["created_at", "priority"]
SortOrder = Literal["asc", "desc"]
