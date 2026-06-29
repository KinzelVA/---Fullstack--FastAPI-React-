from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app import models as _models  # noqa: F401
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.tickets import router as tickets_router
from backend.app.core.config import get_settings
from backend.app.core.rate_limit import InMemoryRateLimitMiddleware
from backend.app.db.database import Base, SessionLocal, engine
from backend.app.db.seed import seed_admin_user


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        seed_admin_user(db)

    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API for internal request tracking test assignment.",
    lifespan=lifespan,
)

app.add_middleware(
    InMemoryRateLimitMiddleware,
    limit=settings.rate_limit_default,
    path_prefix="/api/v1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(tickets_router, prefix="/api/v1")


@app.get(
    "/health",
    tags=["System"],
    summary="Healthcheck",
)
def healthcheck() -> dict[str, str]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
    }
