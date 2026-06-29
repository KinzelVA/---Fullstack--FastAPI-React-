"""Regression tests for search query edge cases."""

from fastapi.testclient import TestClient

from backend.tests.conftest import create_ticket


def test_empty_search_query_is_treated_as_no_filter(client: TestClient) -> None:
    create_ticket(
        client,
        title="Printer is broken",
        description="No output",
        priority="normal",
    )

    response = client.get("/api/v1/tickets", params={"search": ""})

    assert response.status_code == 200
    assert response.json()["total"] == 1
