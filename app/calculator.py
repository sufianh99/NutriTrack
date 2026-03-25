"""Pure-function calculator module for Mifflin-St-Jeor BMR, TDEE, and macros.

No Flask or SQLAlchemy imports allowed in this module.
"""

PAL_FACTORS: dict[str, float] = {
    "sedentary": 1.200,
    "light": 1.375,
    "moderate": 1.550,
    "active": 1.725,
    "very_active": 1.900,
}

GOAL_MODIFIERS: dict[str, float] = {
    "lose": 0.85,
    "maintain": 1.00,
    "gain": 1.10,
}

KCAL_PER_GRAM_PROTEIN: float = 4.0
KCAL_PER_GRAM_FAT: float = 9.0
KCAL_PER_GRAM_CARBS: float = 4.0


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Mifflin-St-Jeor BMR formula.

    Male:   (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    Female: (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    """
    base = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age)
    return base + 5.0 if gender == "male" else base - 161.0


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """TDEE = BMR * PAL factor for the given activity level."""
    return bmr * PAL_FACTORS[activity_level]


def apply_goal_modifier(tdee: float, goal: str) -> float:
    """Apply goal modifier to TDEE: lose=0.85, maintain=1.0, gain=1.10."""
    return tdee * GOAL_MODIFIERS[goal]


def calculate_macros(calorie_goal: float) -> dict[str, float]:
    """Calculate macro targets: protein 25%, fat 30%, carbs 45% of calorie goal."""
    return {
        "protein_g": round((calorie_goal * 0.25) / KCAL_PER_GRAM_PROTEIN, 1),
        "fat_g": round((calorie_goal * 0.30) / KCAL_PER_GRAM_FAT, 1),
        "carbs_g": round((calorie_goal * 0.45) / KCAL_PER_GRAM_CARBS, 1),
    }
