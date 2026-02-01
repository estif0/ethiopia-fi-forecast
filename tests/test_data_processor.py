"""
Unit tests for DataProcessor class.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.data_processor import DataProcessor


@pytest.fixture
def sample_data():
    """Create sample unified dataset for testing."""
    data = {
        "record_id": [f"REC_{i:03d}" for i in range(1, 16)],
        "record_type": [
            "observation",
            "observation",
            "observation",
            "observation",
            "observation",
            "observation",
            "observation",
            "observation",
            "event",
            "event",
            "event",
            "impact_link",
            "impact_link",
            "target",
            "target",
        ],
        "pillar": [
            "access",
            "access",
            "usage",
            "usage",
            "access",
            "infrastructure",
            "infrastructure",
            "access",
            None,
            None,
            None,
            None,
            None,
            "access",
            "usage",
        ],
        "indicator_code": [
            "ACC_OWNERSHIP",
            "ACC_OWNERSHIP",
            "USG_DIGITAL_PAYMENT",
            "USG_DIGITAL_PAYMENT",
            "ACC_MM_ACCOUNT",
            "ACC_4G_COV",
            "ACC_MOBILE_PEN",
            "ACC_OWNERSHIP",
            None,
            None,
            None,
            None,
            None,
            "ACC_OWNERSHIP",
            "USG_DIGITAL_PAYMENT",
        ],
        "value_numeric": [
            35.0,
            38.5,
            12.0,
            15.5,
            25.0,
            45.0,
            80.0,
            41.2,
            None,
            None,
            None,
            None,
            None,
            55.0,
            35.0,
        ],
        "observation_date": pd.to_datetime(
            [
                "2021-12-31",
                "2024-12-31",
                "2021-12-31",
                "2024-12-31",
                "2024-12-31",
                "2023-12-31",
                "2023-12-31",
                "2017-12-31",
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ]
        ),  # type: ignore
        "event_date": pd.to_datetime(
            [
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                "2021-05-15",
                "2023-08-01",
                "2022-06-01",
                None,
                None,
                None,
                None,
            ]
        ),
        "target_date": pd.to_datetime(
            [
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                "2027-12-31",
                "2027-12-31",
            ]
        ),
        "collection_date": pd.to_datetime(["2025-01-15"] * 15),
        "confidence": [
            "high",
            "high",
            "high",
            "high",
            "medium",
            "medium",
            "high",
            "high",
            None,
            None,
            None,
            None,
            None,
            "high",
            "high",
        ],
        "source_type": [
            "survey",
            "survey",
            "survey",
            "survey",
            "industry_report",
            "government",
            "government",
            "survey",
            "press_release",
            "press_release",
            "regulatory",
            None,
            None,
            "projection",
            "projection",
        ],
        "category": [
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "product_launch",
            "product_launch",
            "policy",
            None,
            None,
            None,
            None,
        ],
        "title": [
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "Telebirr Launch",
            "M-Pesa Ethiopia",
            "KYC Relaxation",
            None,
            None,
            None,
            None,
        ],
    }
    return pd.DataFrame(data)


@pytest.fixture
def reference_codes():
    """Create sample reference codes."""
    return pd.DataFrame(
        {
            "code": ["ACC_OWNERSHIP", "USG_DIGITAL_PAYMENT", "ACC_MM_ACCOUNT"],
            "description": [
                "Account Ownership Rate",
                "Digital Payment Usage",
                "Mobile Money Accounts",
            ],
            "pillar": ["access", "usage", "access"],
        }
    )


def test_init_valid_data(sample_data, reference_codes):
    """Test DataProcessor initialization with valid data."""
    processor = DataProcessor(sample_data, reference_codes)
    assert processor.data is not None
    assert len(processor.data) == 15
    assert processor.reference_codes is not None


def test_init_empty_data():
    """Test that empty data raises ValueError."""
    with pytest.raises(ValueError, match="Data cannot be None or empty"):
        DataProcessor(pd.DataFrame())


def test_init_missing_required_columns(sample_data):
    """Test that missing required columns raises ValueError."""
    invalid_data = sample_data.drop(columns=["record_type"])
    with pytest.raises(ValueError, match="Data missing required columns"):
        DataProcessor(invalid_data)


def test_filter_by_record_type_single(sample_data):
    """Test filtering by single record type."""
    processor = DataProcessor(sample_data)
    obs = processor.filter_by_record_type(["observation"])
    assert len(obs) == 8
    assert all(obs["record_type"] == "observation")


def test_filter_by_record_type_multiple(sample_data):
    """Test filtering by multiple record types."""
    processor = DataProcessor(sample_data)
    result = processor.filter_by_record_type(["observation", "event"])
    assert len(result) == 11
    assert set(result["record_type"].unique()) == {"observation", "event"}


def test_filter_by_record_type_none(sample_data):
    """Test that None returns all records."""
    processor = DataProcessor(sample_data)
    result = processor.filter_by_record_type(None)
    assert len(result) == 15


def test_filter_by_record_type_invalid(sample_data):
    """Test that invalid record type raises ValueError."""
    processor = DataProcessor(sample_data)
    with pytest.raises(ValueError, match="Invalid record types"):
        processor.filter_by_record_type(["invalid_type"])


def test_get_time_series_valid_indicator(sample_data):
    """Test extracting time series for valid indicator."""
    processor = DataProcessor(sample_data)
    ts = processor.get_time_series("ACC_OWNERSHIP")
    assert len(ts) == 3  # Three observations for ACC_OWNERSHIP
    assert "observation_date" in ts.columns
    assert "value_numeric" in ts.columns
    assert ts["observation_date"].is_monotonic_increasing


def test_get_time_series_invalid_indicator(sample_data):
    """Test that invalid indicator raises ValueError."""
    processor = DataProcessor(sample_data)
    with pytest.raises(ValueError, match="No data found for indicator"):
        processor.get_time_series("INVALID_CODE")


def test_calculate_growth_rates_absolute(sample_data):
    """Test absolute growth rate calculation."""
    processor = DataProcessor(sample_data)
    growth = processor.calculate_growth_rates("ACC_OWNERSHIP", period_type="absolute")
    assert "growth_absolute" in growth.columns
    assert len(growth) == 2  # Two growth periods from three observations


def test_calculate_growth_rates_percentage(sample_data):
    """Test percentage growth rate calculation."""
    processor = DataProcessor(sample_data)
    growth = processor.calculate_growth_rates("ACC_OWNERSHIP", period_type="percentage")
    assert "growth_percentage" in growth.columns
    # Check that percentage is calculated correctly
    # 2017: 41.2, 2021: 35.0, 2024: 38.5
    # Growth 2017->2021: (35-41.2)/41.2 * 100 = -15.05%
    # Growth 2021->2024: (38.5-35)/35 * 100 = 10%
    assert growth.iloc[0]["growth_percentage"] < 0  # Negative growth
    assert growth.iloc[1]["growth_percentage"] > 0  # Positive growth


def test_calculate_growth_rates_annualized(sample_data):
    """Test annualized growth rate calculation."""
    processor = DataProcessor(sample_data)
    growth = processor.calculate_growth_rates("ACC_OWNERSHIP", period_type="annualized")
    assert "growth_annualized" in growth.columns
    assert "years_elapsed" in growth.columns


def test_calculate_growth_rates_invalid_period(sample_data):
    """Test that invalid period type raises ValueError."""
    processor = DataProcessor(sample_data)
    with pytest.raises(ValueError, match="Invalid period_type"):
        processor.calculate_growth_rates("ACC_OWNERSHIP", period_type="invalid")


def test_calculate_growth_rates_insufficient_data(sample_data):
    """Test that insufficient data points raises ValueError."""
    processor = DataProcessor(sample_data)
    with pytest.raises(ValueError, match="Insufficient data points"):
        processor.calculate_growth_rates("ACC_4G_COV")  # Only 1 observation


def test_get_disaggregated_data_by_pillar(sample_data):
    """Test disaggregation by pillar."""
    processor = DataProcessor(sample_data)
    disagg = processor.get_disaggregated_data(dimension="pillar")
    assert "pillar" in disagg.columns
    assert "total_records" in disagg.columns
    assert "unique_indicators" in disagg.columns
    # Should have access, usage, infrastructure
    assert len(disagg) == 3


def test_get_disaggregated_data_by_confidence(sample_data):
    """Test disaggregation by confidence level."""
    processor = DataProcessor(sample_data)
    disagg = processor.get_disaggregated_data(dimension="confidence")
    assert "confidence" in disagg.columns
    # Should have high and medium
    assert len(disagg) == 2


def test_get_disaggregated_data_invalid_dimension(sample_data):
    """Test that invalid dimension raises ValueError."""
    processor = DataProcessor(sample_data)
    with pytest.raises(ValueError, match="Dimension column .* not found"):
        processor.get_disaggregated_data(dimension="invalid_dimension")


def test_get_temporal_coverage(sample_data):
    """Test temporal coverage analysis."""
    processor = DataProcessor(sample_data)
    coverage = processor.get_temporal_coverage()
    assert "indicator_code" in coverage.columns
    assert "earliest_date" in coverage.columns
    assert "latest_date" in coverage.columns
    assert "observation_count" in coverage.columns
    assert "year_span" in coverage.columns
    # ACC_OWNERSHIP should have 3 observations
    acc_row = coverage[coverage["indicator_code"] == "ACC_OWNERSHIP"]
    assert len(acc_row) == 1
    assert acc_row.iloc[0]["observation_count"] == 3


def test_get_data_quality_summary(sample_data):
    """Test data quality summary generation."""
    processor = DataProcessor(sample_data)
    quality = processor.get_data_quality_summary()
    assert "by_confidence" in quality
    assert "by_source_type" in quality
    assert "by_record_type" in quality
    assert "missing_values" in quality
    # Check record type distribution
    assert quality["by_record_type"].loc["observation", "count"] == 8
    assert quality["by_record_type"].loc["event", "count"] == 3


def test_get_correlation_matrix(sample_data):
    """Test correlation matrix generation."""
    processor = DataProcessor(sample_data)
    corr = processor.get_correlation_matrix()
    assert isinstance(corr, pd.DataFrame)
    # Should be square matrix
    assert corr.shape[0] == corr.shape[1]
    # Diagonal elements should be 1.0 or NaN (for single-value indicators)
    diagonal = np.diag(corr)
    assert all((np.isclose(diagonal, 1.0)) | (np.isnan(diagonal)))


def test_get_event_summary(sample_data):
    """Test event summary generation."""
    processor = DataProcessor(sample_data)
    summary = processor.get_event_summary()
    assert "category" in summary.columns
    assert "year" in summary.columns
    assert "event_count" in summary.columns
    assert len(summary) == 3  # Three events in sample data


def test_prepare_indicator_for_plotting(sample_data):
    """Test preparing indicator data for plotting."""
    processor = DataProcessor(sample_data)
    ts_data, events_data = processor.prepare_indicator_for_plotting(
        "ACC_OWNERSHIP", include_events=True
    )
    assert ts_data is not None
    assert len(ts_data) == 3
    assert events_data is not None  # Should have events within date range


def test_prepare_indicator_for_plotting_no_events(sample_data):
    """Test preparing indicator without events."""
    processor = DataProcessor(sample_data)
    ts_data, events_data = processor.prepare_indicator_for_plotting(
        "ACC_OWNERSHIP", include_events=False
    )
    assert ts_data is not None
    assert events_data is None
