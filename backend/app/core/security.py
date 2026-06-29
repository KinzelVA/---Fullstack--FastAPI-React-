import base64
import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt

from backend.app.core.config import get_settings

PASSWORD_HASH_ALGORITHM = "pbkdf2_sha256"
PASSWORD_HASH_ITERATIONS = 390_000
SALT_BYTES = 16


def hash_password(plain_password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )

    salt_b64 = base64.b64encode(salt).decode("ascii")
    hash_b64 = base64.b64encode(password_hash).decode("ascii")

    return (
        f"{PASSWORD_HASH_ALGORITHM}"
        f"${PASSWORD_HASH_ITERATIONS}"
        f"${salt_b64}"
        f"${hash_b64}"
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        algorithm, iterations_raw, salt_b64, expected_hash_b64 = hashed_password.split(
            "$",
            maxsplit=3,
        )
    except ValueError:
        return False

    if algorithm != PASSWORD_HASH_ALGORITHM:
        return False

    try:
        iterations = int(iterations_raw)
        salt = base64.b64decode(salt_b64.encode("ascii"))
        expected_hash = base64.b64decode(expected_hash_b64.encode("ascii"))
    except (ValueError, TypeError):
        return False

    actual_hash = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt,
        iterations,
    )

    return secrets.compare_digest(actual_hash, expected_hash)


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    settings = get_settings()

    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
