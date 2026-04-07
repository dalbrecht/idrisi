"""Voyages CLI — Typer-based command-line interface."""

from __future__ import annotations

import typer

from voyages.cli.place_commands import place_app
from voyages.cli.project_commands import project_app
from voyages.cli.serve_command import serve
from voyages.cli.trip_commands import trip_app

app = typer.Typer(
    name="voyages",
    help="A Python map generation toolbox for travel cartography.",
    no_args_is_help=True,
)

# Register sub-apps
app.add_typer(place_app)
app.add_typer(project_app)
app.add_typer(trip_app)

# Register top-level commands
app.command()(serve)
