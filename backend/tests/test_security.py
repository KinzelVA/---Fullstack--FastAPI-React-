from datetime import timedelta

from jose import jwt

from backend.app.core.config import get_settings
from backend.app.core.security import create_access_token, hash_password, verify_password


def test_password_hash_is_not_plain_text() -> None:
    password_hash = hash_password("admin")

    assert password_hash != "admin"
    assert password_hash.startswith("pbkdf2_sha256$")


def test_verify_password_success_and_failure() -> None:
    password_hash = hash_password("admin")

    assert verify_password("admin", password_hash) is True
    assert verify_password("wrong", password_hash) is False


def test_create_access_token_contains_subject() -> None:
    settings = get_settings()

    token = create_access_token(
        subject="admin",
        expires_delta=timedelta(minutes=5),
        extra_claims={"is_admin": True},
    )

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    assert payload["sub"] == "admin"
    assert payload["is_admin"] is True
