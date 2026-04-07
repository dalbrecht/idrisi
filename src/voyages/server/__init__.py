"""FastAPI application factory for the Voyages server."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool

from voyages.domain.errors import EntityNotFoundError
from voyages.infrastructure.db.models import Base
from voyages.infrastructure.db.session import get_session
from voyages.server.routes.places import create_places_router
from voyages.server.routes.projects import create_projects_router
from voyages.server.routes.regions import create_regions_router
from voyages.server.routes.render import create_render_router
from voyages.server.routes.trips import create_trips_router


def _create_engine_for_url(database_url: str) -> Engine:
    """Create a SQLAlchemy engine, using StaticPool for in-memory SQLite."""
    if database_url in ("sqlite://", "sqlite:///:memory:"):
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def create_app(database_url: str = "sqlite:///voyages.db") -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        database_url: SQLAlchemy-compatible database URL.

    Returns:
        A configured FastAPI instance.
    """
    app = FastAPI(title="Voyages API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    engine: Engine = _create_engine_for_url(database_url)

    @app.middleware("http")
    async def db_session_middleware(request: Request, call_next: Any) -> Response:
        session = get_session(engine)
        request.state.db = session
        try:
            response: Response = await call_next(request)
        finally:
            session.close()
        return response

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(
        request: Request, exc: EntityNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    # Include API routers
    app.include_router(create_places_router(), prefix="/api")
    app.include_router(create_trips_router(), prefix="/api")
    app.include_router(create_projects_router(), prefix="/api")
    app.include_router(create_regions_router(), prefix="/api")
    app.include_router(create_render_router(), prefix="/api")

    # Mount static files for SPA if directory exists
    static_dir = Path(__file__).resolve().parent / "static"
    if static_dir.is_dir():
        from starlette.staticfiles import StaticFiles  # noqa: PLC0415

        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app
