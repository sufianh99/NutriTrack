"""Unit Tests für app/api_client.py — alle API-Aufrufe sind gemockt."""

from unittest.mock import MagicMock, patch


def _mock_response(json_data, status_code=200):
    """Erstellt eine Mock-Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    if status_code >= 400:
        from requests.exceptions import HTTPError

        resp.raise_for_status.side_effect = HTTPError(response=resp)
    return resp


def test_search_returns_results():
    """Suche gibt normalisierte Ergebnisse zurück."""
    with patch("app.api_client.requests.get") as mock_get:
        mock_get.return_value = _mock_response(
            {
                "products": [
                    {
                        "product_name": "Haferflocken",
                        "nutriments": {
                            "energy-kcal_100g": 372,
                            "proteins_100g": 13.5,
                            "fat_100g": 7.0,
                            "carbohydrates_100g": 58.7,
                        },
                    }
                ]
            }
        )
        from app.api_client import search_food

        results = search_food("Haferflocken")
        assert len(results) == 1
        assert results[0]["name"] == "Haferflocken"
        assert results[0]["calories_per_100g"] == 372.0


def test_search_empty_returns_empty_list():
    """Keine Treffer gibt leere Liste zurück."""
    with patch("app.api_client.requests.get") as mock_get:
        mock_get.return_value = _mock_response({"products": []})
        from app.api_client import search_food

        assert search_food("xyznonexistent") == []


def test_search_exception_returns_empty_list():
    """Netzwerkfehler gibt leere Liste zurück."""
    with patch("app.api_client.requests.get") as mock_get:
        mock_get.side_effect = ConnectionError("Network error")
        from app.api_client import search_food

        assert search_food("Haferflocken") == []


def test_search_filters_empty_nutriments():
    """Produkte ohne Nährwerte werden herausgefiltert."""
    with patch("app.api_client.requests.get") as mock_get:
        mock_get.return_value = _mock_response(
            {
                "products": [
                    {"product_name": "Leer", "nutriments": {}},
                    {
                        "product_name": "Voll",
                        "nutriments": {"energy-kcal_100g": 200, "proteins_100g": 10},
                    },
                ]
            }
        )
        from app.api_client import search_food

        results = search_food("Produkt")
        assert len(results) == 1
        assert results[0]["name"] == "Voll"


def test_search_fallback_url():
    """Fallback auf zweite URL wenn erste fehlschlägt."""
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
        assert mock_get.call_count == 2
