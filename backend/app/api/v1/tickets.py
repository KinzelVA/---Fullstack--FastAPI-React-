from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.ticket import TicketPriority, TicketStatus
from backend.app.models.user import User
from backend.app.schemas.ticket import (
    PaginatedTicketsResponse,
    SortBy,
    SortOrder,
    TicketCreateRequest,
    TicketResponse,
    TicketStatusUpdateRequest,
)
from backend.app.services.auth_service import get_current_admin
from backend.app.services.ticket_service import (
    create_ticket,
    delete_ticket,
    list_tickets,
    update_ticket_status,
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create ticket",
    responses={
        201: {
            "description": "Ticket created",
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "string_too_short",
                                "loc": ["body", "title"],
                                "msg": "String should have at least 3 characters",
                                "input": "Hi",
                                "ctx": {"min_length": 3},
                            }
                        ]
                    }
                }
            },
        },
    },
)
def create_ticket_endpoint(
    payload: TicketCreateRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TicketResponse:
    ticket = create_ticket(db=db, payload=payload)
    return TicketResponse.model_validate(ticket)


@router.get(
    "",
    response_model=PaginatedTicketsResponse,
    summary="List tickets with backend filtering, search, sorting and pagination",
)
def list_tickets_endpoint(
    db: Annotated[Session, Depends(get_db)],
    status_filter: Annotated[
        TicketStatus | None,
        Query(alias="status", description="Filter by ticket status"),
    ] = None,
    priority_filter: Annotated[
        TicketPriority | None,
        Query(alias="priority", description="Filter by ticket priority"),
    ] = None,
    search: Annotated[
        str | None,
        Query(max_length=120, description="Search in title and description"),
    ] = None,
    sort_by: Annotated[
        SortBy,
        Query(description="Sort by created_at or priority"),
    ] = "created_at",
    sort_order: Annotated[
        SortOrder,
        Query(description="Sort direction"),
    ] = "desc",
    page: Annotated[
        int,
        Query(ge=1, description="Page number, starts from 1"),
    ] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=100, description="Items per page"),
    ] = 10,
) -> PaginatedTicketsResponse:
    return list_tickets(
        db=db,
        status_filter=status_filter,
        priority_filter=priority_filter,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )


@router.patch(
    "/{ticket_id}/status",
    response_model=TicketResponse,
    summary="Update ticket status",
    responses={
        404: {
            "description": "Ticket not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Ticket was not found."
                    }
                }
            },
        },
        409: {
            "description": "Business rule violation",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Ticket in done status cannot be edited."
                    }
                }
            },
        },
    },
)
def update_ticket_status_endpoint(
    ticket_id: int,
    payload: TicketStatusUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TicketResponse:
    ticket = update_ticket_status(
        db=db,
        ticket_id=ticket_id,
        payload=payload,
    )

    return TicketResponse.model_validate(ticket)


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete ticket as admin",
    responses={
        204: {
            "description": "Ticket deleted",
        },
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
            "description": "Admin privileges are required",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Admin privileges are required."
                    }
                }
            },
        },
        404: {
            "description": "Ticket not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Ticket was not found."
                    }
                }
            },
        },
        409: {
            "description": "Business rule violation",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Ticket in done status cannot be deleted."
                    }
                }
            },
        },
    },
)
def delete_ticket_endpoint(
    ticket_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
) -> Response:
    _ = current_admin

    delete_ticket(db=db, ticket_id=ticket_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
