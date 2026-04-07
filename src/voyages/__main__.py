"""Allow running voyages as a module: python -m voyages."""
from __future__ import annotations

from voyages.cli import app

if __name__ == "__main__":
    app()
