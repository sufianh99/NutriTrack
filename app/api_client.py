"""Open Food Facts API wrapper for NutriTrack."""

import logging

import openfoodfacts

logger = logging.getLogger("nutritrack")


class APIError(Exception):
    """Raised when the Open Food Facts API call fails."""


def search_food(query: str, max_results: int = 10) -> list[dict[str, float | str]]:
    """Search Open Food Facts for products matching the query.

    Returns a list of dicts with normalized nutrition keys.
    Returns empty list on network errors or when no products found.
    Never raises — all exceptions are caught and logged.
    """
    try:
        api = openfoodfacts.API(user_agent="NutriTrack/1.0")
        response = api.product.text_search(query)
        products = response.get("products", [])[:max_results]
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
