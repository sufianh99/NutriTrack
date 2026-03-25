from app.nutrition import progress_status, scale_nutrients, sum_daily_nutrients


class TestScaleNutrients:
    def test_150g_portion(self) -> None:
        """150g portion: 200 kcal, 20g protein, 10g fat, 30g carbs per 100g."""
        result = scale_nutrients(150.0, 200.0, 20.0, 10.0, 30.0)
        assert result == {
            "calories": 300.0,
            "protein_g": 30.0,
            "fat_g": 15.0,
            "carbs_g": 45.0,
        }

    def test_zero_amount(self) -> None:
        """0g portion returns all zeros."""
        result = scale_nutrients(0.0, 200.0, 20.0, 10.0, 30.0)
        assert result == {
            "calories": 0.0,
            "protein_g": 0.0,
            "fat_g": 0.0,
            "carbs_g": 0.0,
        }

    def test_identity_at_100g(self) -> None:
        """100g portion returns same values as per-100g nutrients (identity)."""
        result = scale_nutrients(100.0, 200.0, 20.0, 10.0, 30.0)
        assert result == {
            "calories": 200.0,
            "protein_g": 20.0,
            "fat_g": 10.0,
            "carbs_g": 30.0,
        }


class TestSumDailyNutrients:
    def test_two_entries(self) -> None:
        """Sum of two entries returns correct totals."""
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

    def test_empty_list(self) -> None:
        """Empty list returns all zeros."""
        result = sum_daily_nutrients([])
        assert result == {
            "calories": 0.0,
            "protein_g": 0.0,
            "fat_g": 0.0,
            "carbs_g": 0.0,
        }


class TestProgressStatus:
    def test_below_90_percent(self) -> None:
        """80% is below 90% threshold — returns empty string."""
        assert progress_status(80.0, 100.0) == ""

    def test_just_below_90(self) -> None:
        """89.9% is just below 90% threshold — returns empty string."""
        assert progress_status(89.9, 100.0) == ""

    def test_exactly_90(self) -> None:
        """Exactly 90% — returns 'success'."""
        assert progress_status(90.0, 100.0) == "success"

    def test_exactly_100(self) -> None:
        """Exactly 100% — returns 'success'."""
        assert progress_status(100.0, 100.0) == "success"

    def test_just_above_100(self) -> None:
        """100.1% is just above 100% — returns 'danger'."""
        assert progress_status(100.1, 100.0) == "danger"

    def test_well_above_100(self) -> None:
        """150% is well above 100% — returns 'danger'."""
        assert progress_status(150.0, 100.0) == "danger"

    def test_zero_goal(self) -> None:
        """Zero goal returns empty string (avoid division by zero)."""
        assert progress_status(50.0, 0.0) == ""
