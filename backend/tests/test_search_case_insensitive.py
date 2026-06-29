"""Regression tests for case-insensitive search over Cyrillic text."""

from fastapi.testclient import TestClient

from backend.tests.conftest import create_ticket


def test_search_title_is_case_insensitive_for_cyrillic(
    client: TestClient,
) -> None:
    create_ticket(
        client,
        title="\u041f\u0440\u0438\u043d\u0442\u0435\u0440 \u0441\u043b\u043e\u043c\u0430\u043d",
        description="\u041d\u0435 \u043f\u0435\u0447\u0430\u0442\u0430\u0435\u0442 \u043f\u043e\u0441\u043b\u0435 \u0437\u0430\u043c\u0435\u043d\u044b \u043a\u0430\u0440\u0442\u0440\u0438\u0434\u0436\u0430",
        priority="high",
    )

    lower_response = client.get(
        "/api/v1/tickets",
        params={"search": "\u043f\u0440\u0438\u043d\u0442\u0435\u0440"},
    )
    assert lower_response.status_code == 200
    assert lower_response.json()["total"] == 1

    upper_response = client.get(
        "/api/v1/tickets",
        params={"search": "\u041f\u0420\u0418\u041d\u0422\u0415\u0420"},
    )
    assert upper_response.status_code == 200
    assert upper_response.json()["total"] == 1


def test_search_description_is_case_insensitive_for_cyrillic(
    client: TestClient,
) -> None:
    create_ticket(
        client,
        title="\u0417\u0430\u044f\u0432\u043a\u0430",
        description="\u041a\u0410\u0420\u0422\u0420\u0418\u0414\u0416 \u0437\u0430\u043a\u043e\u043d\u0447\u0438\u043b\u0441\u044f",
        priority="normal",
    )

    response = client.get(
        "/api/v1/tickets",
        params={"search": "\u043a\u0430\u0440\u0442\u0440\u0438\u0434\u0436"},
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_search_still_works_for_ascii(client: TestClient) -> None:
    create_ticket(
        client,
        title="Printer is broken",
        description="No output",
        priority="normal",
    )

    response = client.get("/api/v1/tickets", params={"search": "PRINTER"})
    assert response.status_code == 200
    assert response.json()["total"] == 1
