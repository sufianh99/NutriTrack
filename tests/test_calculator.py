import pytest

from app.calculator import (
    apply_goal_modifier,
    calculate_bmr,
    calculate_macros,
    calculate_tdee,
)


def test_bmr_male() -> None:
    """30yo, 70kg, 175cm male: (10*70) + (6.25*175) - (5*30) + 5 = 1648.75."""
    result = calculate_bmr(weight_kg=70.0, height_cm=175.0, age=30, gender="male")
    assert result == pytest.approx(1648.75, abs=0.01)


def test_bmr_female() -> None:
    """60kg, 165cm, 25yo female: (10*60) + (6.25*165) - (5*25) - 161 = 1345.25."""
    result = calculate_bmr(weight_kg=60.0, height_cm=165.0, age=25, gender="female")
    assert result == pytest.approx(1345.25, abs=0.01)


def test_tdee_activity_levels() -> None:
    """Alle Aktivitätslevel ergeben korrekte TDEE-Werte."""
    bmr = 1648.75
    expected = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    for level, factor in expected.items():
        assert calculate_tdee(bmr, level) == pytest.approx(bmr * factor, abs=0.01)


def test_goal_modifier_lose() -> None:
    """Abnehmen = -15% Kalorien."""
    assert apply_goal_modifier(2000.0, "lose") == pytest.approx(1700.0, abs=0.01)


def test_macros_split() -> None:
    """Makroverteilung: 25% Protein, 30% Fett, 45% Kohlenhydrate."""
    macros = calculate_macros(2000.0)
    assert macros["protein_g"] == pytest.approx(125.0, abs=0.1)
    assert macros["fat_g"] == pytest.approx(66.7, abs=0.1)
    assert macros["carbs_g"] == pytest.approx(225.0, abs=0.1)
