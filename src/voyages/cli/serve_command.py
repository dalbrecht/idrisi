"""Serve command — launch the Voyages web server."""

from __future__ import annotations

import typer


def serve(
    port: int = typer.Option(8080, help="Port to listen on."),
    host: str = typer.Option("127.0.0.1", help="Host to bind to."),
) -> None:
    """Start the Voyages web server."""
    import uvicorn  # noqa: PLC0415

    from voyages.server import create_app  # noqa: PLC0415

    application = create_app()
    uvicorn.run(application, host=host, port=port)
