import math

from fastapi import HTTPException, status
from sqlalchemy import asc, case, desc, func, or_, select
from sqlalchemy.orm import Session

from backend.app.models.ticket import Ticket, TicketPriority, TicketStatus, utc_now
from backend.app.schemas.ticket import (
    PaginatedTicketsResponse,
    SortBy,
    SortOrder,
    TicketCreateRequest,
    TicketStatusUpdateRequest,
)


def get_ticket_or_404(db: Session, ticket_id: int) -> Ticket:
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket was not found.",
        )

    return ticket


def create_ticket(db: Session, payload: TicketCreateRequest) -> Ticket:
    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        status=TicketStatus.NEW,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


def list_tickets(
    db: Session,
    status_filter: TicketStatus | None,
    priority_filter: TicketPriority | None,
    search: str | None,
    sort_by: SortBy,
    sort_order: SortOrder,
    page: int,
    page_size: int,
) -> PaginatedTicketsResponse:
    conditions = []

    if status_filter is not None:
        conditions.append(Ticket.status == status_filter)

    if priority_filter is not None:
        conditions.append(Ticket.priority == priority_filter)

    if search:
        search_pattern = f"%{search.strip()}%"
        conditions.append(
            or_(
                Ticket.title.ilike(search_pattern),
                Ticket.description.ilike(search_pattern),
            )
        )

    count_query = select(func.count()).select_from(Ticket)

    if conditions:
        count_query = count_query.where(*conditions)

    total = db.scalar(count_query) or 0

    priority_order = case(
        (Ticket.priority == TicketPriority.LOW, 1),
        (Ticket.priority == TicketPriority.NORMAL, 2),
        (Ticket.priority == TicketPriority.HIGH, 3),
        else_=0,
    )

    order_column = Ticket.created_at if sort_by == "created_at" else priority_order
    order_expression = desc(order_column) if sort_order == "desc" else asc(order_column)

    query = select(Ticket)

    if conditions:
        query = query.where(*conditions)

    query = (
        query.order_by(order_expression, desc(Ticket.id))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    items = list(db.scalars(query).all())
    pages = math.ceil(total / page_size) if total else 0

    return PaginatedTicketsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def update_ticket_status(
    db: Session,
    ticket_id: int,
    payload: TicketStatusUpdateRequest,
) -> Ticket:
    ticket = get_ticket_or_404(db, ticket_id)

    if ticket.status == TicketStatus.DONE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ticket in done status cannot be edited.",
        )

    ticket.status = payload.status
    ticket.updated_at = utc_now()

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


def delete_ticket(db: Session, ticket_id: int) -> None:
    ticket = get_ticket_or_404(db, ticket_id)

    if ticket.status == TicketStatus.DONE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ticket in done status cannot be deleted.",
        )

    db.delete(ticket)
    db.commit()
