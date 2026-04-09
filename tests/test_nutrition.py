from app.nutrition import progress_status, scale_nutrients, sum_daily_nutrients


def test_scale_150g_portion() -> None:
    """150g Portion skaliert Nährwerte korrekt."""
    result = scale_nutrients(150.0, 200.0, 20.0, 10.0, 30.0)
    assert result == {
        "calories": 300.0,
        "protein_g": 30.0,
        "fat_g": 15.0,
        "carbs_g": 45.0,
    }


def test_sum_two_entries() -> None:
    """Summe von zwei Einträgen ergibt korrekte Tagessumme."""
    entries = [
        {"calories": 300.0, "protein_g": 30.0, "fat_g": 15.0, "carbs_g": 45.0},
        {"calories": 200.0, "protein_g": 10.0, "fat_g": 5.0, "carbs_g": 25.0},
    ]
    result = sum_daily_nutrients(entries)
    assert result == {
        "calories": 500.0,
        "protein_g": 40.0,
        "fat_g": 20.0,
        "carbs_g": 70.0,
    }


def test_progress_below_90() -> None:
    """Unter 90% gibt keinen Status zurück."""
    assert progress_status(80.0, 100.0) == ""


def test_progress_between_90_and_100() -> None:
    """Zwischen 90% und 100% gibt 'success' zurück."""
    assert progress_status(90.0, 100.0) == "success"


def test_progress_above_100() -> None:
    """Über 100% gibt 'danger' zurück."""
    assert progress_status(100.1, 100.0) == "danger"
