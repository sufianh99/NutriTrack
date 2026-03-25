"""Pure-function nutrition module for portion scaling, summation, and progress status.

No Flask or SQLAlchemy imports allowed in this module.
"""


def scale_nutrients(
    amount_g: float,
    calories_per_100g: float,
    protein_per_100g: float,
    fat_per_100g: float,
    carbs_per_100g: float,
) -> dict[str, float]:
    """Scale nutrient values from per-100g to the given portion size.

    Args:
        amount_g: Portion size in grams.
        calories_per_100g: Calories per 100g.
        protein_per_100g: Protein in grams per 100g.
        fat_per_100g: Fat in grams per 100g.
        carbs_per_100g: Carbohydrates in grams per 100g.

    Returns:
        Dict with keys "calories", "protein_g", "fat_g", "carbs_g" scaled to amount_g.
    """
    factor = amount_g / 100.0
    return {
        "calories": round(calories_per_100g * factor, 1),
        "protein_g": round(protein_per_100g * factor, 1),
        "fat_g": round(fat_per_100g * factor, 1),
        "carbs_g": round(carbs_per_100g * factor, 1),
    }


def sum_daily_nutrients(entries: list[dict[str, float]]) -> dict[str, float]:
    """Sum a list of scaled nutrient entries into daily totals.

    Args:
        entries: List of dicts with keys "calories", "protein_g", "fat_g", "carbs_g".

    Returns:
        Dict with summed totals for each nutrient key. Empty list returns all zeros.
    """
    return {
        "calories": round(sum(e["calories"] for e in entries), 1),
        "protein_g": round(sum(e["protein_g"] for e in entries), 1),
        "fat_g": round(sum(e["fat_g"] for e in entries), 1),
        "carbs_g": round(sum(e["carbs_g"] for e in entries), 1),
    }


def progress_status(actual: float, goal: float) -> str:
    """Return Bootstrap colour class for progress towards a nutrition goal.

    Thresholds per ROADMAP.md success criteria:
        - Below 90%: "" (neutral / no colour)
        - 90% to 100% inclusive: "success" (green)
        - Above 100%: "danger" (red)

    Args:
        actual: Actual nutrient intake value.
        goal: Target nutrient goal value.

    Returns:
        Bootstrap contextual class string: "", "success", or "danger".
    """
    if goal <= 0:
        return ""
    ratio = actual / goal
    if ratio < 0.90:
        return ""
    if ratio <= 1.00:
        return "success"
    return "danger"
