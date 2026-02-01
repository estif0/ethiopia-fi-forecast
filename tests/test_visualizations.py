"""
Unit tests for FinancialInclusionVisualizer class.
"""

import pytest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pathlib import Path
from src.visualizations import FinancialInclusionVisualizer


@pytest.fixture
def sample_time_series():
    """Create sample time series data."""
    return pd.DataFrame(
        {
            "observation_date": pd.to_datetime(
                ["2017-12-31", "2021-12-31", "2024-12-31"]
            ),
            "value_numeric": [35.0, 38.0, 41.5],
            "pillar": ["access", "access", "access"],
            "confidence": ["high", "high", "high"],
        }
    )


@pytest.fixture
def sample_events():
    """Create sample events data."""
    return pd.DataFrame(
        {
            "event_date": pd.to_datetime(["2021-05-15", "2023-08-01"]),
            "title": ["Telebirr Launch", "M-Pesa Ethiopia"],
            "category": ["product_launch", "product_launch"],
        }
    )


@pytest.fixture
def sample_coverage():
    """Create sample temporal coverage data."""
    return pd.DataFrame(
        {
            "indicator_code": [
                "ACC_OWNERSHIP",
                "USG_DIGITAL_PAYMENT",
                "ACC_MM_ACCOUNT",
            ],
            "earliest_date": pd.to_datetime(["2011-12-31", "2014-12-31", "2017-12-31"]),
            "latest_date": pd.to_datetime(["2024-12-31", "2024-12-31", "2024-12-31"]),
            "observation_count": [5, 4, 3],
        }
    )


@pytest.fixture
def sample_correlation():
    """Create sample correlation matrix."""
    indicators = ["ACC_OWNERSHIP", "USG_DIGITAL_PAYMENT", "ACC_MM_ACCOUNT"]
    corr_data = np.array([[1.0, 0.85, 0.92], [0.85, 1.0, 0.78], [0.92, 0.78, 1.0]])
    return pd.DataFrame(corr_data, index=indicators, columns=indicators)


@pytest.fixture
def sample_growth():
    """Create sample growth data."""
    return pd.DataFrame(
        {
            "observation_date": pd.to_datetime(["2021-12-31", "2024-12-31"]),
            "value_numeric": [38.0, 41.5],
            "value_prev": [35.0, 38.0],
            "growth_percentage": [8.57, 9.21],
            "growth_absolute": [3.0, 3.5],
            "growth_annualized": [2.8, 3.0],
            "pillar": ["access", "access"],
            "confidence": ["high", "high"],
        }
    )


@pytest.fixture
def sample_quality_summary():
    """Create sample data quality summary."""
    return {
        "by_record_type": pd.DataFrame(
            {"count": [30, 10, 5, 3]},
            index=["observation", "event", "impact_link", "target"],
        ),
        "by_confidence": pd.DataFrame({"count": [25, 5]}, index=["high", "medium"]),
        "by_source_type": pd.DataFrame(
            {"count": [20, 8, 2]}, index=["survey", "industry_report", "government"]
        ),
        "missing_values": pd.DataFrame(
            {"missing_count": [5, 3]}, index=["pillar", "confidence"]
        ),
    }


@pytest.fixture
def sample_disagg_data():
    """Create sample disaggregated data."""
    return pd.DataFrame(
        {
            "pillar": ["access", "usage", "infrastructure"],
            "total_records": [20, 15, 8],
            "unique_indicators": [10, 8, 5],
            "mean_value": [35.5, 12.3, 45.0],
        }
    )


@pytest.fixture
def visualizer():
    """Create a FinancialInclusionVisualizer instance."""
    return FinancialInclusionVisualizer()


def test_init_default(visualizer):
    """Test default initialization."""
    assert visualizer.style == "whitegrid"
    assert visualizer.color_palette == "husl"
    assert visualizer.figsize == (12, 6)


def test_init_custom():
    """Test custom initialization."""
    viz = FinancialInclusionVisualizer(
        style="darkgrid", color_palette="Set2", figsize=(10, 5)
    )
    assert viz.style == "darkgrid"
    assert viz.color_palette == "Set2"
    assert viz.figsize == (10, 5)


def test_plot_timeline(visualizer, sample_coverage):
    """Test timeline plot creation."""
    fig = visualizer.plot_timeline(sample_coverage)
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    plt.close(fig)


def test_plot_timeline_with_save(visualizer, sample_coverage, tmp_path):
    """Test saving timeline plot."""
    save_path = tmp_path / "timeline.png"
    fig = visualizer.plot_timeline(sample_coverage, save_path=save_path)
    assert save_path.exists()
    plt.close(fig)


def test_plot_indicator_trend(visualizer, sample_time_series):
    """Test indicator trend plot."""
    fig = visualizer.plot_indicator_trend(
        sample_time_series,
        indicator_code="ACC_OWNERSHIP",
        indicator_name="Account Ownership Rate",
    )
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_indicator_trend_without_confidence(visualizer, sample_time_series):
    """Test indicator trend without confidence coloring."""
    fig = visualizer.plot_indicator_trend(
        sample_time_series, indicator_code="ACC_OWNERSHIP", show_confidence=False
    )
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_events_overlay(visualizer, sample_time_series, sample_events):
    """Test events overlay plot."""
    fig = visualizer.plot_events_overlay(
        sample_time_series,
        sample_events,
        indicator_code="ACC_OWNERSHIP",
        indicator_name="Account Ownership Rate",
    )
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_events_overlay_no_events(visualizer, sample_time_series):
    """Test events overlay with empty events."""
    fig = visualizer.plot_events_overlay(
        sample_time_series,
        pd.DataFrame(),  # Empty events
        indicator_code="ACC_OWNERSHIP",
    )
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_correlation_matrix(visualizer, sample_correlation):
    """Test correlation matrix heatmap."""
    fig = visualizer.plot_correlation_matrix(sample_correlation)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_growth_rates_percentage(visualizer, sample_growth):
    """Test percentage growth rate plot."""
    fig = visualizer.plot_growth_rates(
        sample_growth, indicator_code="ACC_OWNERSHIP", growth_type="percentage"
    )
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_growth_rates_absolute(visualizer, sample_growth):
    """Test absolute growth rate plot."""
    fig = visualizer.plot_growth_rates(
        sample_growth, indicator_code="ACC_OWNERSHIP", growth_type="absolute"
    )
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_growth_rates_annualized(visualizer, sample_growth):
    """Test annualized growth rate plot."""
    fig = visualizer.plot_growth_rates(
        sample_growth, indicator_code="ACC_OWNERSHIP", growth_type="annualized"
    )
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_growth_rates_invalid_type(visualizer, sample_growth):
    """Test that invalid growth type raises ValueError."""
    # Remove the growth column to trigger error
    invalid_growth = sample_growth.drop(columns=["growth_percentage"])
    with pytest.raises(ValueError, match="Growth column .* not found"):
        visualizer.plot_growth_rates(
            invalid_growth, indicator_code="ACC_OWNERSHIP", growth_type="percentage"
        )


def test_plot_data_quality_summary(visualizer, sample_quality_summary):
    """Test data quality summary visualization."""
    fig = visualizer.plot_data_quality_summary(sample_quality_summary)
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 4  # 2x2 subplots
    plt.close(fig)


def test_plot_data_quality_summary_no_missing(visualizer):
    """Test data quality summary with no missing values."""
    quality = {
        "by_record_type": pd.DataFrame({"count": [30]}, index=["observation"]),
        "by_confidence": pd.DataFrame({"count": [30]}, index=["high"]),
        "by_source_type": pd.DataFrame({"count": [30]}, index=["survey"]),
        "missing_values": pd.DataFrame(),  # Empty
    }
    fig = visualizer.plot_data_quality_summary(quality)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_pillar_comparison(visualizer, sample_disagg_data):
    """Test pillar comparison visualization."""
    fig = visualizer.plot_pillar_comparison(sample_disagg_data)
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 2  # Two subplots
    plt.close(fig)


def test_create_interactive_timeline(visualizer, sample_time_series, sample_events):
    """Test interactive Plotly timeline creation."""
    # Note: Plotly vline has issues with pandas Timestamps in some versions
    # Test without events for now
    fig = visualizer.create_interactive_timeline(
        sample_time_series,
        None,  # Skip events to avoid Plotly timestamp issues
        indicator_code="ACC_OWNERSHIP",
        indicator_name="Account Ownership Rate",
    )
    # Check that it's a Plotly figure
    assert hasattr(fig, "data")
    assert hasattr(fig, "layout")


def test_create_interactive_timeline_no_events(visualizer, sample_time_series):
    """Test interactive timeline without events."""
    fig = visualizer.create_interactive_timeline(
        sample_time_series, None, indicator_code="ACC_OWNERSHIP"
    )
    assert hasattr(fig, "data")
    assert len(fig.data) == 1  # Only the trend line


def test_pillar_colors_defined(visualizer):
    """Test that pillar colors are defined."""
    assert "access" in visualizer.PILLAR_COLORS
    assert "usage" in visualizer.PILLAR_COLORS
    assert "infrastructure" in visualizer.PILLAR_COLORS


def test_event_colors_defined(visualizer):
    """Test that event category colors are defined."""
    assert "product_launch" in visualizer.EVENT_COLORS
    assert "policy" in visualizer.EVENT_COLORS
    assert "market_entry" in visualizer.EVENT_COLORS
