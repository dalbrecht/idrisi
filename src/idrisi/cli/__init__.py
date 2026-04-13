"""Idrisi CLI — Typer-based command-line interface."""

from __future__ import annotations

import typer

from idrisi.cli.album_commands import album_app
from idrisi.cli.import_commands import import_app
from idrisi.cli.place_commands import place_app
from idrisi.cli.project_commands import project_app
from idrisi.cli.render_commands import render
from idrisi.cli.serve_command import serve
from idrisi.cli.trip_commands import trip_app

app = typer.Typer(
    name="idrisi",
    help="A Python map generation toolbox for travel cartography.",
    no_args_is_help=True,
)

app.add_typer(album_app)
app.add_typer(place_app)
app.add_typer(project_app)
app.add_typer(trip_app)
app.add_typer(import_app)

# Register top-level commands
app.command()(serve)
app.command()(render)
