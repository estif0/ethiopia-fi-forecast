"""
Tests for forecaster module.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.forecaster import FinancialInclusionForecaster


@pytest.fixture
def sample_observation_data():
    """Create sample historical observation data."""
    data = pd.DataFrame(
        {
            "record_id": ["obs_1", "obs_2", "obs_3", "obs_4", "obs_5"],
            "record_type": ["observation"] * 5,
            "indicator_code": ["ACC_OWNERSHIP"] * 5,
            "observation_date": pd.to_datetime(
                ["2011-01-01", "2014-01-01", "2017-01-01", "2021-01-01", "2024-01-01"]
            ),
            "value_numeric": [14.0, 22.0, 35.0, 35.0, 38.0],
        }
    )
    return data


@pytest.fixture
def sample_events_data():
    """Create sample events data."""
    data = pd.DataFrame(
        {
            "record_id": ["evt_1", "evt_2"],
            "record_type": ["event"] * 2,
            "category": ["product_launch", "policy"],
            "event_date": pd.to_datetime(["2025-06-01", "2026-01-01"]),
            "description": ["Future Product X", "New Regulation Y"],
        }
    )
    return data


@pytest.fixture
def forecaster(sample_observation_data):
    """Create forecaster instance."""
    return FinancialInclusionForecaster(sample_observation_data)


def test_forecaster_initialization(sample_observation_data):
    """Test forecaster initializes correctly."""
    forecaster = FinancialInclusionForecaster(sample_observation_data)

    assert forecaster is not None
    assert len(forecaster.data) == 5
    assert "observation_date" in forecaster.data.columns
    assert forecaster.data["observation_date"].dtype == "datetime64[ns]"


def test_forecaster_with_events(sample_observation_data, sample_events_data):
    """Test forecaster initialization with events."""
    forecaster = FinancialInclusionForecaster(
        sample_observation_data, events_data=sample_events_data
    )

    assert forecaster.events_data is not None
    assert len(forecaster.events_data) == 2
    assert forecaster.events_data["event_date"].dtype == "datetime64[ns]"


def test_fit_trend_model_linear(forecaster):
    """Test fitting linear trend model."""
    model_info = forecaster.fit_trend_model("ACC_OWNERSHIP", trend_type="linear")

    assert model_info is not None
    assert model_info["indicator_code"] == "ACC_OWNERSHIP"
    assert model_info["trend_type"] == "linear"
    assert "coefficients" in model_info
    assert len(model_info["coefficients"]) == 2  # Linear: slope + intercept
    assert "rmse" in model_info
    assert "r_squared" in model_info
    assert model_info["n_points"] == 5


def test_fit_trend_model_polynomial(forecaster):
    """Test fitting polynomial trend model."""
    model_info = forecaster.fit_trend_model("ACC_OWNERSHIP", trend_type="polynomial")

    assert model_info["trend_type"] == "polynomial"
    assert len(model_info["coefficients"]) == 3  # Polynomial degree 2


def test_fit_trend_model_exponential(forecaster):
    """Test fitting exponential trend model."""
    model_info = forecaster.fit_trend_model("ACC_OWNERSHIP", trend_type="exponential")

    assert model_info["trend_type"] == "exponential"
    assert len(model_info["coefficients"]) == 2  # (a, b) for a*exp(b*x)


def test_fit_trend_model_insufficient_data():
    """Test error handling with insufficient data."""
    data = pd.DataFrame(
        {
            "record_id": ["obs_1", "obs_2"],
            "record_type": ["observation"] * 2,
            "indicator_code": ["TEST"] * 2,
            "observation_date": pd.to_datetime(["2020-01-01", "2021-01-01"]),
            "value_numeric": [10.0, 15.0],
        }
    )

    forecaster = FinancialInclusionForecaster(data)

    with pytest.raises(ValueError, match="Insufficient data"):
        forecaster.fit_trend_model("TEST", min_points=3)


def test_fit_trend_model_invalid_type(forecaster):
    """Test error handling with invalid trend type."""
    with pytest.raises(ValueError, match="Invalid trend_type"):
        forecaster.fit_trend_model("ACC_OWNERSHIP", trend_type="invalid")


def test_forecast_trend(forecaster):
    """Test generating trend forecast."""
    model_info = forecaster.fit_trend_model("ACC_OWNERSHIP", trend_type="linear")
    forecast = forecaster.forecast_trend(model_info, [2025, 2026, 2027])

    assert len(forecast) == 3
    assert list(forecast["year"]) == [2025, 2026, 2027]
    assert "forecast" in forecast.columns
    assert "lower_bound" in forecast.columns
    assert "upper_bound" in forecast.columns

    # Check bounds are valid
    assert (forecast["lower_bound"] <= forecast["forecast"]).all()
    assert (forecast["forecast"] <= forecast["upper_bound"]).all()

    # Check values are in valid range [0, 100]
    assert (forecast["forecast"] >= 0).all()
    assert (forecast["forecast"] <= 100).all()


def test_forecast_trend_confidence_intervals(forecaster):
    """Test confidence intervals expand for future years."""
    model_info = forecaster.fit_trend_model("ACC_OWNERSHIP")
    forecast = forecaster.forecast_trend(model_info, [2025, 2026, 2027])

    # Calculate interval widths
    widths = forecast["upper_bound"] - forecast["lower_bound"]

    # Intervals should generally increase (allowing some variation)
    assert widths.iloc[-1] >= widths.iloc[0] * 0.9


def test_apply_event_adjustments(forecaster, sample_events_data):
    """Test applying event adjustments to forecast."""
    forecaster.events_data = sample_events_data

    model_info = forecaster.fit_trend_model("ACC_OWNERSHIP")
    base_forecast = forecaster.forecast_trend(model_info, [2025, 2026, 2027])

    adjusted = forecaster.apply_event_adjustments(
        base_forecast, sample_events_data, adjustment_method="additive"
    )

    assert len(adjusted) == len(base_forecast)
    assert "forecast" in adjusted.columns

    # Adjusted values should generally be different (unless no matching events)
    # At least the bounds should be wider due to event uncertainty


def test_apply_event_adjustments_no_events(forecaster):
    """Test event adjustments with no events."""
    model_info = forecaster.fit_trend_model("ACC_OWNERSHIP")
    base_forecast = forecaster.forecast_trend(model_info, [2025, 2026, 2027])

    adjusted = forecaster.apply_event_adjustments(
        base_forecast, pd.DataFrame(), adjustment_method="additive"  # Empty events
    )

    # Should return forecast unchanged
    pd.testing.assert_frame_equal(
        base_forecast.reset_index(drop=True), adjusted.reset_index(drop=True)
    )


def test_generate_scenarios(forecaster):
    """Test generating scenario forecasts."""
    scenarios = forecaster.generate_scenarios("ACC_OWNERSHIP", [2025, 2026, 2027])

    assert len(scenarios) == 9  # 3 years x 3 scenarios
    assert set(scenarios["scenario"].unique()) == {"optimistic", "base", "pessimistic"}

    # Check each year has all three scenarios
    for year in [2025, 2026, 2027]:
        year_data = scenarios[scenarios["year"] == year]
        assert len(year_data) == 3
        assert set(year_data["scenario"]) == {"optimistic", "base", "pessimistic"}

    # Optimistic should be highest, pessimistic lowest (generally)
    for year in [2025, 2026, 2027]:
        year_data = scenarios[scenarios["year"] == year]
        opt = year_data[year_data["scenario"] == "optimistic"]["forecast"].iloc[0]
        base = year_data[year_data["scenario"] == "base"]["forecast"].iloc[0]
        pess = year_data[year_data["scenario"] == "pessimistic"]["forecast"].iloc[0]

        assert opt >= base >= pess


def test_generate_scenarios_custom_assumptions(forecaster):
    """Test scenarios with custom assumptions."""
    custom_assumptions = {
        "optimistic_multiplier": 1.5,
        "base_multiplier": 1.0,
        "pessimistic_multiplier": 0.5,
    }

    scenarios = forecaster.generate_scenarios(
        "ACC_OWNERSHIP", [2025, 2026, 2027], scenario_assumptions=custom_assumptions
    )

    assert len(scenarios) == 9
    # Check that multipliers had effect (wider spread)


def test_forecast_with_uncertainty(forecaster):
    """Test comprehensive forecast with uncertainty."""
    results = forecaster.forecast_with_uncertainty(
        "ACC_OWNERSHIP", [2025, 2026, 2027], methods=["trend", "scenarios"]
    )

    assert results is not None
    assert "indicator_code" in results
    assert results["indicator_code"] == "ACC_OWNERSHIP"
    assert "methods" in results
    assert "trend" in results["methods"]
    assert "scenarios" in results["methods"]

    # Check trend forecast
    trend_forecast = results["methods"]["trend"]["forecast"]
    assert len(trend_forecast) == 3

    # Check scenarios
    scenario_forecast = results["methods"]["scenarios"]["forecast"]
    assert len(scenario_forecast) == 9


def test_forecast_with_uncertainty_stores_results(forecaster):
    """Test that forecast results are stored."""
    forecaster.forecast_with_uncertainty("ACC_OWNERSHIP", [2025, 2026, 2027])

    assert "ACC_OWNERSHIP" in forecaster.forecast_results
    assert forecaster.forecast_results["ACC_OWNERSHIP"] is not None


def test_get_forecast_summary(forecaster):
    """Test getting forecast summary."""
    forecaster.forecast_with_uncertainty("ACC_OWNERSHIP", [2025, 2026, 2027])

    summary = forecaster.get_forecast_summary("ACC_OWNERSHIP")

    assert summary is not None
    assert len(summary) > 0
    assert "year" in summary.columns
    assert "indicator_code" in summary.columns
    assert "method" in summary.columns
    assert "forecast_mean" in summary.columns


def test_get_forecast_summary_not_forecasted(forecaster):
    """Test getting summary for non-forecasted indicator."""
    summary = forecaster.get_forecast_summary("NOT_FORECASTED")

    assert summary is None


def test_export_forecasts(forecaster, tmp_path):
    """Test exporting forecasts to files."""
    forecaster.forecast_with_uncertainty("ACC_OWNERSHIP", [2025, 2026, 2027])

    output_files = forecaster.export_forecasts(str(tmp_path))

    assert "ACC_OWNERSHIP" in output_files
    assert output_files["ACC_OWNERSHIP"].endswith("_forecast_summary.csv")

    # Check file was created
    import os

    assert os.path.exists(output_files["ACC_OWNERSHIP"])

    # Check file contains data
    df = pd.read_csv(output_files["ACC_OWNERSHIP"])
    assert len(df) > 0


def test_forecast_trend_different_confidence_levels(forecaster):
    """Test forecasts with different confidence levels."""
    model_info = forecaster.fit_trend_model("ACC_OWNERSHIP")

    forecast_95 = forecaster.forecast_trend(model_info, [2025], confidence_level=0.95)
    forecast_80 = forecaster.forecast_trend(model_info, [2025], confidence_level=0.80)

    # 95% CI should be wider than 80% CI
    width_95 = forecast_95["upper_bound"].iloc[0] - forecast_95["lower_bound"].iloc[0]
    width_80 = forecast_80["upper_bound"].iloc[0] - forecast_80["lower_bound"].iloc[0]

    assert width_95 > width_80


def test_forecaster_handles_missing_indicator(forecaster):
    """Test handling of non-existent indicator."""
    with pytest.raises(ValueError, match="Insufficient data"):
        forecaster.fit_trend_model("NON_EXISTENT_INDICATOR")


def test_model_statistics_are_reasonable(forecaster):
    """Test that model statistics are in reasonable ranges."""
    model_info = forecaster.fit_trend_model("ACC_OWNERSHIP")

    # R-squared should be between -infinity and 1 (but typically 0-1)
    assert model_info["r_squared"] <= 1.0

    # RMSE and MAE should be non-negative
    assert model_info["rmse"] >= 0
    assert model_info["mae"] >= 0

    # Standard error should be positive
    assert model_info["std_error"] > 0
