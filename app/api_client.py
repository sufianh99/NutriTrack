"""Open Food Facts API wrapper for NutriTrack."""

import logging

import requests

logger = logging.getLogger("nutritrack")

# Elasticsearch-based search proxy — works when cgi/search.pl is down (503).
_SEARCH_URLS = [
    "https://search.openfoodfacts.org/search",
    "https://world.openfoodfacts.org/api/v2/search",
]
_TIMEOUT = 8
_USER_AGENT = "NutriTrack/1.0"


class APIError(Exception):
    """Raised when the Open Food Facts API call fails."""


def search_food(query: str, max_results: int = 10) -> list[dict[str, float | str]]:
    """Search Open Food Facts for products matching the query.

    Returns a list of dicts with normalized nutrition keys.
    Returns empty list on network errors or when no products found.
    Never raises — all exceptions are caught and logged.
    """
    try:
        products = _fetch_products(query, max_results)
        results: list[dict[str, float | str]] = []
        for product in products:
            nutriments = product.get("nutriments", {})
            name: str = product.get("product_name") or product.get(
                "product_name_de", "Unknown"
            )
            if not name:
                name = "Unknown"
            results.append(
                {
                    "name": name,
                    "calories_per_100g": float(nutriments.get("energy-kcal_100g", 0)),
                    "protein_per_100g": float(nutriments.get("proteins_100g", 0)),
                    "fat_per_100g": float(nutriments.get("fat_100g", 0)),
                    "carbs_per_100g": float(nutriments.get("carbohydrates_100g", 0)),
                }
            )
        return results
    except Exception as exc:
        logger.error("Open Food Facts search failed for query=%r: %s", query, exc)
        return []


def _fetch_products(query: str, max_results: int) -> list[dict]:
    """Try each search URL until one returns 200."""
    headers = {"User-Agent": _USER_AGENT}
    last_exc: Exception | None = None
    for url in _SEARCH_URLS:
        params: dict[str, str | int] = {
            "page_size": max_results,
            "fields": "product_name,product_name_de,nutriments",
        }
        # search.openfoodfacts.org uses 'q'; v2/search uses 'search_terms'
        if "search.openfoodfacts.org" in url:
            params["q"] = query
        else:
            params["search_terms"] = query
            params["json"] = 1
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            # ES proxy returns 'hits', v2 API returns 'products'
            products = data.get("hits") or data.get("products") or []
            return products  # type: ignore[no-any-return]
        except Exception as exc:
            logger.warning("OFF search failed on %s: %s", url, exc)
            last_exc = exc
    if last_exc:
        raise last_exc
    return []
