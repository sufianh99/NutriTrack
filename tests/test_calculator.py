import pytest
from app.calculator import (
    calculate_bmr,
    calculate_tdee,
    apply_goal_modifier,
    calculate_macros,
    PAL_FACTORS,
    GOAL_MODIFIERS,
)


def test_bmr_male_reference_value() -> None:
    """30yo, 70kg, 175cm male: standard Mifflin-St-Jeor.

    Formula: (10 * 70) + (6.25 * 175) - (5 * 30) + 5 = 700 + 1093.75 - 150 + 5 = 1648.75
    Note: Project spec states 1673.75 but standard Mifflin-St-Jeor formula produces 1648.75.
    The standard formula is correct; this test uses 1648.75.
    """
    result = calculate_bmr(weight_kg=70.0, height_cm=175.0, age=30, gender="male")
    assert result == pytest.approx(1648.75, abs=0.01)


def test_bmr_female_constant() -> None:
    """Female constant is -161; male-female diff = 166 for same inputs.

    male constant = +5, female constant = -161, difference = 5 - (-161) = 166
    """
    male = calculate_bmr(70.0, 175.0, 30, "male")
    female = calculate_bmr(70.0, 175.0, 30, "female")
    assert male - female == pytest.approx(166.0, abs=0.01)


def test_bmr_female_direct() -> None:
    """60kg, 165cm, 25yo female = 1345.25.

    Formula: (10 * 60) + (6.25 * 165) - (5 * 25) - 161 = 600 + 1031.25 - 125 - 161 = 1345.25
    """
    result = calculate_bmr(weight_kg=60.0, height_cm=165.0, age=25, gender="female")
    assert result == pytest.approx(1345.25, abs=0.01)


def test_tdee_sedentary() -> None:
    bmr = 1648.75
    assert calculate_tdee(bmr, "sedentary") == pytest.approx(bmr * 1.2, abs=0.01)


def test_tdee_all_activity_levels() -> None:
    bmr = 1648.75
    expected_factors = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    for level, factor in expected_factors.items():
        assert calculate_tdee(bmr, level) == pytest.approx(
            bmr * factor, abs=0.01
        ), f"Failed for {level}"


def test_goal_modifier_lose() -> None:
    assert apply_goal_modifier(2000.0, "lose") == pytest.approx(1700.0, abs=0.01)


def test_goal_modifier_maintain() -> None:
    assert apply_goal_modifier(2000.0, "maintain") == pytest.approx(2000.0, abs=0.01)


def test_goal_modifier_gain() -> None:
    assert apply_goal_modifier(2000.0, "gain") == pytest.approx(2200.0, abs=0.01)


def test_macros_standard_split() -> None:
    macros = calculate_macros(2000.0)
    assert macros["protein_g"] == pytest.approx(125.0, abs=0.1)
    assert macros["fat_g"] == pytest.approx(66.7, abs=0.1)
    assert macros["carbs_g"] == pytest.approx(225.0, abs=0.1)


def test_macros_rounding() -> None:
    """Verify macros are rounded to 1 decimal place."""
    macros = calculate_macros(1500.0)
    for key in ("protein_g", "fat_g", "carbs_g"):
        value_str = str(macros[key])
        if "." in value_str:
            assert len(value_str.split(".")[1]) <= 1
