import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.core.rate_limit import InMemoryRateLimitMiddleware, parse_rate_limit


def test_parse_rate_limit_success() -> None:
    assert parse_rate_limit("100/minute") == (100, 60)
    assert parse_rate_limit("5/second") == (5, 1)
    assert parse_rate_limit("10/hour") == (10, 3600)


@pytest.mark.parametrize(
    "invalid_limit",
    [
        "",
        "wrong",
        "0/minute",
        "-1/minute",
        "100/day",
    ],
)
def test_parse_rate_limit_invalid(invalid_limit: str) -> None:
    with pytest.raises(ValueError):
        parse_rate_limit(invalid_limit)


def test_rate_limit_middleware_returns_429() -> None:
    test_app = FastAPI()
    test_app.add_middleware(
        InMemoryRateLimitMiddleware,
        limit="2/minute",
        path_prefix="/api",
    )

    @test_app.get("/api/ping")
    def ping() -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(test_app)

    first_response = client.get("/api/ping")
    second_response = client.get("/api/ping")
    third_response = client.get("/api/ping")

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    assert third_response.status_code == 429
    assert third_response.json() == {
        "detail": "Rate limit exceeded. Try again later."
    }
    assert third_response.headers["X-RateLimit-Limit"] == "2"
    assert third_response.headers["X-RateLimit-Remaining"] == "0"
