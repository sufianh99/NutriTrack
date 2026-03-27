"""Unit tests for app/api_client.py — all HTTP calls are mocked."""

from unittest.mock import MagicMock, patch

import pytest


def _mock_response(json_data, status_code=200):
    """Create a mock requests.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    if status_code >= 400:
        from requests.exceptions import HTTPError

        resp.raise_for_status.side_effect = HTTPError(response=resp)
    return resp


@pytest.fixture
def mock_api_response():
    """Standard mock response from OFF v2/search."""
    return {
        "products": [
            {
                "product_name": "Haferflocken",
                "nutriments": {
                    "energy-kcal_100g": 372,
                    "proteins_100g": 13.5,
                    "fat_100g": 7.0,
                    "carbohydrates_100g": 58.7,
                },
            },
            {
                "product_name": "Bio Haferflocken",
                "nutriments": {
                    "energy-kcal_100g": 360,
                    "proteins_100g": 12.0,
                    "fat_100g": 6.5,
                    "carbohydrates_100g": 60.0,
                },
            },
        ]
    }


def test_search_food_returns_normalized_dicts(mock_api_response):
    """Test 1: search_food returns list of dicts with expected keys."""
    with patch("app.api_client.requests.get") as mock_get:
        mock_get.return_value = _mock_response(mock_api_response)

        from app.api_client import search_food

        results = search_food("Haferflocken")

        assert isinstance(results, list)
        assert len(results) == 2
        first = results[0]
        assert first["name"] == "Haferflocken"
        assert first["calories_per_100g"] == 372.0
        assert first["protein_per_100g"] == 13.5
        assert first["fat_per_100g"] == 7.0
        assert first["carbs_per_100g"] == 58.7


def test_search_food_empty_products_returns_empty_list():
    """Test 2: search_food returns empty list when API returns no products."""
    with patch("app.api_client.requests.get") as mock_get:
        mock_get.return_value = _mock_response({"products": []})

        from app.api_client import search_food

        results = search_food("xyznonexistent")
        assert results == []


def test_search_food_returns_empty_on_exception():
    """Test 3: search_food returns empty list when request raises an exception."""
    with patch("app.api_client.requests.get") as mock_get:
        mock_get.side_effect = ConnectionError("Network error")

        from app.api_client import search_food

        results = search_food("Haferflocken")
        assert results == []


def test_search_food_missing_nutriments_default_to_zero():
    """Test 4: Missing nutriments keys default to 0.0 (not KeyError)."""
    with patch("app.api_client.requests.get") as mock_get:
        mock_get.return_value = _mock_response(
            {
                "products": [
                    {
                        "product_name": "Unbekanntes Produkt",
                        "nutriments": {},
                    }
                ]
            }
        )

        from app.api_client import search_food

        results = search_food("Unbekanntes Produkt")
        assert len(results) == 1
        assert results[0]["calories_per_100g"] == 0.0
        assert results[0]["protein_per_100g"] == 0.0
        assert results[0]["fat_per_100g"] == 0.0
        assert results[0]["carbs_per_100g"] == 0.0


def test_search_food_limits_results_to_max():
    """Test 5: search_food passes max_results as page_size to API."""
    with patch("app.api_client.requests.get") as mock_get:
        products = [
            {
                "product_name": f"Produkt {i}",
                "nutriments": {"energy-kcal_100g": 100 * i},
            }
            for i in range(15)
        ]
        mock_get.return_value = _mock_response({"products": products})

        from app.api_client import search_food

        results = search_food("Produkt")
        # API returns all 15 but page_size=10 was requested
        assert len(results) == 15  # we trust the API to limit; client parses all

        # With explicit max_results, page_size is set accordingly
        results_5 = search_food("Produkt", max_results=5)
        call_args = mock_get.call_args
        assert call_args[1]["params"]["page_size"] == 5


def test_search_food_fallback_to_second_url():
    """Test 6: Falls back to second URL when first returns 503."""
    good_response = _mock_response(
        {
            "products": [
                {
                    "product_name": "Milch",
                    "nutriments": {"energy-kcal_100g": 64},
                }
            ]
        }
    )
    with patch("app.api_client.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_response({}, status_code=503),
            good_response,
        ]

        from app.api_client import search_food

        results = search_food("Milch")
        assert len(results) == 1
        assert results[0]["name"] == "Milch"
        assert mock_get.call_count == 2
