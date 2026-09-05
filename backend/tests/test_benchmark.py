from app.services.benchmark_service import synthetic_benchmark


def test_benchmark_uses_one_fixed_ground_truth_cohort():
    result = synthetic_benchmark()

    assert result["cohort_size"] == 5000
    assert result["revenue_at_risk"] > 0
    assert 0 <= result["recoverai_recovered_revenue"] <= result["always_retry_recovered_revenue"]
    expected = round((result["recoverai_recovered_revenue"] - result["always_retry_recovered_revenue"]) / result["always_retry_recovered_revenue"] * 100, 2)
    assert result["improvement_percentage"] == expected
    assert "Synthetic benchmark" in result["label"]
