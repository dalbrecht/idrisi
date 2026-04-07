"""Integration tests: project creation and render workflow via API."""

from __future__ import annotations

from starlette.testclient import TestClient

from voyages.server import create_app


def _make_client() -> TestClient:
    return TestClient(create_app(database_url="sqlite://"))


class TestProjectRenderWorkflow:
    """Create project -> render -> verify valid output."""

    def test_create_project_and_render(self) -> None:
        """Create a project with no associated data and verify it renders to a valid PNG."""
        with _make_client() as client:
            project_resp = client.post(
                "/api/projects",
                json={"name": "Test Map", "map_type": "travel"},
            )
            assert project_resp.status_code == 201
            project_id = project_resp.json()["id"]

            render_resp = client.post(f"/api/render/{project_id}")
            assert render_resp.status_code == 200
            assert render_resp.content[:8] == b"\x89PNG\r\n\x1a\n"
