"""Integration tests: full-stack place CRUD workflow via API."""

from __future__ import annotations

from starlette.testclient import TestClient

from voyages.server import create_app


def _make_client() -> TestClient:
    return TestClient(create_app(database_url="sqlite://"))


class TestPlaceCrudWorkflow:
    """Create -> list -> verify -> delete -> verify gone."""

    def test_full_place_lifecycle(self) -> None:
        with _make_client() as client:
            create_resp = client.post(
                "/api/places",
                json={
                    "name": "Paris",
                    "lat": 48.8566,
                    "lon": 2.3522,
                    "source": "manual",
                    "country": "France",
                },
            )
            assert create_resp.status_code == 201
            place_id = create_resp.json()["id"]

            list_resp = client.get("/api/places")
            assert list_resp.status_code == 200
            names = [p["name"] for p in list_resp.json()]
            assert "Paris" in names

            delete_resp = client.delete(f"/api/places/{place_id}")
            assert delete_resp.status_code == 204

            list_resp2 = client.get("/api/places")
            assert list_resp2.json() == []

    def test_create_multiple_and_search(self) -> None:
        with _make_client() as client:
            client.post(
                "/api/places",
                json={"name": "Paris", "lat": 48.85, "lon": 2.35, "source": "manual"},
            )
            client.post(
                "/api/places",
                json={"name": "Parma", "lat": 44.80, "lon": 10.33, "source": "manual"},
            )
            client.post(
                "/api/places",
                json={"name": "Berlin", "lat": 52.52, "lon": 13.40, "source": "manual"},
            )

            search_resp = client.get("/api/places/search", params={"q": "Par"})
            assert search_resp.status_code == 200
            results = search_resp.json()
            result_names = [r["name"] for r in results]
            assert "Paris" in result_names
            assert "Parma" in result_names
            assert "Berlin" not in result_names
