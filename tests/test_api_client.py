"""Unit tests for app/api_client.py — all SDK calls are mocked."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_sdk_response():
    """Standard mock response from api.product.text_search."""
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


def test_search_food_returns_normalized_dicts(mock_sdk_response):
    """Test 1: search_food returns list of dicts with expected keys."""
    with patch("app.api_client.openfoodfacts") as mock_off:
        mock_api = MagicMock()
        mock_off.API.return_value = mock_api
        mock_api.product.text_search.return_value = mock_sdk_response

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
    """Test 2: search_food returns empty list when SDK returns no products."""
    with patch("app.api_client.openfoodfacts") as mock_off:
        mock_api = MagicMock()
        mock_off.API.return_value = mock_api
        mock_api.product.text_search.return_value = {"products": []}

        from app.api_client import search_food

        results = search_food("xyznonexistent")
        assert results == []


def test_search_food_returns_empty_on_exception():
    """Test 3: search_food returns empty list when SDK raises an exception."""
    with patch("app.api_client.openfoodfacts") as mock_off:
        mock_api = MagicMock()
        mock_off.API.return_value = mock_api
        mock_api.product.text_search.side_effect = ConnectionError("Network error")

        from app.api_client import search_food

        results = search_food("Haferflocken")
        assert results == []


def test_search_food_missing_nutriments_default_to_zero():
    """Test 4: Missing nutriments keys default to 0.0 (not KeyError)."""
    with patch("app.api_client.openfoodfacts") as mock_off:
        mock_api = MagicMock()
        mock_off.API.return_value = mock_api
        mock_api.product.text_search.return_value = {
            "products": [
                {
                    "product_name": "Unbekanntes Produkt",
                    "nutriments": {},  # all nutriment values missing
                }
            ]
        }

        from app.api_client import search_food

        results = search_food("Unbekanntes Produkt")
        assert len(results) == 1
        assert results[0]["calories_per_100g"] == 0.0
        assert results[0]["protein_per_100g"] == 0.0
        assert results[0]["fat_per_100g"] == 0.0
        assert results[0]["carbs_per_100g"] == 0.0


def test_search_food_limits_results_to_max():
    """Test 5: search_food limits results to max_results (default 10)."""
    products = [
        {"product_name": f"Produkt {i}", "nutriments": {"energy-kcal_100g": 100 * i}}
        for i in range(15)
    ]
    with patch("app.api_client.openfoodfacts") as mock_off:
        mock_api = MagicMock()
        mock_off.API.return_value = mock_api
        mock_api.product.text_search.return_value = {"products": products}

        from app.api_client import search_food

        results = search_food("Produkt")
        assert len(results) == 10

        results_5 = search_food("Produkt", max_results=5)
        assert len(results_5) == 5
