"""Tests for Nominatim geocoding client."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from idrisi.domain.value_objects import Coordinates
from idrisi.infrastructure.geocoding.nominatim import NominatimGeocodingService


def _mock_search_response() -> list[dict]:
    return [
        {
            "display_name": "Paris, Ile-de-France, France",
            "lat": "48.8566",
            "lon": "2.3522",
            "address": {
                "country": "France",
                "state": "Ile-de-France",
            },
        },
        {
            "display_name": "Paris, Texas, USA",
            "lat": "33.6609",
            "lon": "-95.5555",
            "address": {
                "country": "United States",
                "state": "Texas",
            },
        },
    ]


def _mock_reverse_response() -> dict:
    return {
        "display_name": "Eiffel Tower, Paris, France",
        "lat": "48.8584",
        "lon": "2.2945",
        "address": {
            "country": "France",
            "state": "Ile-de-France",
        },
    }


class TestNominatimSearch:
    @patch("idrisi.infrastructure.geocoding.nominatim.httpx.get")
    def test_search_returns_places(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _mock_search_response()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = NominatimGeocodingService()
        results = service.search("Paris")

        assert len(results) == 2
        assert results[0].name == "Paris, Ile-de-France, France"
        assert results[0].latitude == 48.8566
        assert results[0].longitude == 2.3522
        assert results[0].country == "France"
        assert results[0].admin1 == "Ile-de-France"
        assert results[0].source == "nominatim"
        assert results[1].country == "United States"

    @patch("idrisi.infrastructure.geocoding.nominatim.httpx.get")
    def test_search_empty_results(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = NominatimGeocodingService()
        results = service.search("xyznonexistent")

        assert results == []


class TestNominatimReverseGeocode:
    @patch("idrisi.infrastructure.geocoding.nominatim.httpx.get")
    def test_reverse_geocode_returns_place(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _mock_reverse_response()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = NominatimGeocodingService()
        coords = Coordinates(latitude=48.8584, longitude=2.2945)
        result = service.reverse_geocode(coords)

        assert result is not None
        assert result.name == "Eiffel Tower, Paris, France"
        assert result.country == "France"

    @patch("idrisi.infrastructure.geocoding.nominatim.httpx.get")
    def test_reverse_geocode_error_returns_none(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "Unable to geocode"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = NominatimGeocodingService()
        coords = Coordinates(latitude=0.0, longitude=0.0)
        result = service.reverse_geocode(coords)

        assert result is None
