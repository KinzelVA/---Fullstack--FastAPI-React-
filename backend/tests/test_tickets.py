from fastapi.testclient import TestClient

from backend.tests.conftest import create_ticket


def test_create_ticket_success(client: TestClient) -> None:
    response = client.post(
        "/api/v1/tickets",
        json={
            "title": "Printer is not working",
            "description": "Printer does not print after cartridge replacement",
            "priority": "high",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["title"] == "Printer is not working"
    assert data["description"] == "Printer does not print after cartridge replacement"
    assert data["status"] == "new"
    assert data["priority"] == "high"
    assert data["created_at"]
    assert data["updated_at"]


def test_create_ticket_validation_error_for_short_title(client: TestClient) -> None:
    response = client.post(
        "/api/v1/tickets",
        json={
            "title": "No",
            "description": "Too short title",
            "priority": "normal",
        },
    )

    assert response.status_code == 422


def test_list_tickets_with_backend_search_filter_sort_and_pagination(
    client: TestClient,
) -> None:
    create_ticket(
        client,
        title="Printer is not working",
        description="Printer does not print after cartridge replacement",
        priority="high",
    )
    create_ticket(
        client,
        title="Keyboard replacement",
        description="Need a new keyboard",
        priority="normal",
    )
    create_ticket(
        client,
        title="Office chair issue",
        description="Chair needs repair",
        priority="low",
    )

    search_response = client.get(
        "/api/v1/tickets",
        params={
            "search": "printer",
            "priority": "high",
            "sort_by": "priority",
            "sort_order": "desc",
            "page": 1,
            "page_size": 5,
        },
    )

    assert search_response.status_code == 200

    search_data = search_response.json()

    assert search_data["total"] == 1
    assert search_data["page"] == 1
    assert search_data["page_size"] == 5
    assert search_data["pages"] == 1
    assert search_data["items"][0]["title"] == "Printer is not working"

    pagination_response = client.get(
        "/api/v1/tickets",
        params={
            "sort_by": "priority",
            "sort_order": "desc",
            "page": 1,
            "page_size": 2,
        },
    )

    assert pagination_response.status_code == 200

    pagination_data = pagination_response.json()

    assert pagination_data["total"] == 3
    assert pagination_data["pages"] == 2
    assert len(pagination_data["items"]) == 2
    assert pagination_data["items"][0]["priority"] == "high"
    assert pagination_data["items"][1]["priority"] == "normal"


def test_unicode_search_works_on_backend(client: TestClient) -> None:
    create_ticket(
        client,
        title="е работает принтер",
        description="ринтер не печатает после замены картриджа",
        priority="high",
    )

    response = client.get(
        "/api/v1/tickets",
        params={
            "search": "принтер",
            "priority": "high",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["title"] == "е работает принтер"


def test_update_ticket_status_success(client: TestClient) -> None:
    ticket = create_ticket(client)

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == ticket["id"]
    assert data["status"] == "in_progress"


def test_done_ticket_cannot_be_updated(client: TestClient) -> None:
    ticket = create_ticket(client)

    done_response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={
            "status": "done",
        },
    )

    assert done_response.status_code == 200
    assert done_response.json()["status"] == "done"

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Ticket in done status cannot be edited."
    }


def test_delete_ticket_requires_admin_token(client: TestClient) -> None:
    ticket = create_ticket(client)

    response = client.delete(f"/api/v1/tickets/{ticket['id']}")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate authentication credentials."
    }


def test_admin_can_delete_ticket(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    ticket = create_ticket(client)

    delete_response = client.delete(
        f"/api/v1/tickets/{ticket['id']}",
        headers=admin_headers,
    )

    assert delete_response.status_code == 204

    list_response = client.get("/api/v1/tickets")

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 0


def test_done_ticket_cannot_be_deleted_even_by_admin(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    ticket = create_ticket(client)

    done_response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={
            "status": "done",
        },
    )

    assert done_response.status_code == 200
    assert done_response.json()["status"] == "done"

    delete_response = client.delete(
        f"/api/v1/tickets/{ticket['id']}",
        headers=admin_headers,
    )

    assert delete_response.status_code == 409
    assert delete_response.json() == {
        "detail": "Ticket in done status cannot be deleted."
    }
