"""Tests for ImpactValidator class."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.impact_validator import ImpactValidator


@pytest.fixture
def sample_observations():
    """Create sample observations for testing."""
    return pd.DataFrame(
        [
            {
                "record_id": "OBS001",
                "indicator_code": "ACC_MM_ACCOUNT",
                "observation_date": "2020-01-01",
                "value_numeric": 10.0,
            },
            {
                "record_id": "OBS002",
                "indicator_code": "ACC_MM_ACCOUNT",
                "observation_date": "2021-01-01",
                "value_numeric": 12.0,
            },
            {
                "record_id": "OBS003",
                "indicator_code": "ACC_MM_ACCOUNT",
                "observation_date": "2022-01-01",
                "value_numeric": 18.0,
            },
            {
                "record_id": "OBS004",
                "indicator_code": "ACC_OWNERSHIP",
                "observation_date": "2020-01-01",
                "value_numeric": 35.0,
            },
            {
                "record_id": "OBS005",
                "indicator_code": "ACC_OWNERSHIP",
                "observation_date": "2022-01-01",
                "value_numeric": 38.0,
            },
        ]
    )


@pytest.fixture
def sample_events():
    """Create sample events for testing."""
    return pd.DataFrame(
        [
            {
                "record_id": "EVT001",
                "description": "Telebirr Launch",
                "event_date": "2021-05-01",
                "category": "product_launch",
            },
            {
                "record_id": "EVT002",
                "description": "Policy Change",
                "event_date": "2020-06-01",
                "category": "policy",
            },
        ]
    )


@pytest.fixture
def sample_impact_links():
    """Create sample impact links for testing."""
    return pd.DataFrame(
        [
            {
                "record_id": "IMP001",
                "parent_id": "EVT001",
                "indicator_code": "ACC_MM_ACCOUNT",
                "impact_direction": "positive",
                "impact_magnitude": 0.5,
            },
            {
                "record_id": "IMP002",
                "parent_id": "EVT002",
                "indicator_code": "ACC_OWNERSHIP",
                "impact_direction": "positive",
                "impact_magnitude": 0.1,
            },
        ]
    )


def test_validator_initialization(
    sample_observations, sample_events, sample_impact_links
):
    """Test ImpactValidator initialization."""
    validator = ImpactValidator(sample_observations, sample_events, sample_impact_links)

    assert validator.observations is not None
    assert validator.events is not None
    assert validator.impact_links is not None
    assert len(validator.observations) == 5
    assert len(validator.events) == 2


def test_validate_against_historical(
    sample_observations, sample_events, sample_impact_links
):
    """Test historical validation of event impact."""
    validator = ImpactValidator(sample_observations, sample_events, sample_impact_links)

    result = validator.validate_against_historical(
        event_id="EVT001",
        indicator_code="ACC_MM_ACCOUNT",
        pre_period_end="2021-01-01",
        post_period_end="2022-01-01",
    )

    assert "error" not in result
    assert "actual_change" in result
    assert "predicted_change" in result
    assert "residual" in result
    assert "direction_correct" in result


def test_calculate_residuals(sample_observations, sample_events, sample_impact_links):
    """Test residual calculation."""
    validator = ImpactValidator(sample_observations, sample_events, sample_impact_links)

    # Run validation first
    validator.validate_against_historical(
        "EVT001", "ACC_MM_ACCOUNT", "2021-01-01", "2022-01-01"
    )

    residuals_df, summary = validator.calculate_residuals()

    assert not residuals_df.empty
    assert "mean_residual" in summary
    assert "direction_accuracy" in summary


def test_generate_validation_report(
    sample_observations, sample_events, sample_impact_links
):
    """Test validation report generation."""
    validator = ImpactValidator(sample_observations, sample_events, sample_impact_links)

    # No validations yet
    report = validator.generate_validation_report()
    assert "No validation results" in report

    # Run validation
    validator.validate_against_historical(
        "EVT001", "ACC_MM_ACCOUNT", "2021-01-01", "2022-01-01"
    )

    report = validator.generate_validation_report()
    assert "VALIDATION REPORT" in report
    assert "Direction Accuracy" in report


def test_validate_event_batch(sample_observations, sample_events, sample_impact_links):
    """Test batch validation of multiple event-indicator pairs."""
    validator = ImpactValidator(sample_observations, sample_events, sample_impact_links)

    pairs = [
        ("EVT001", "ACC_MM_ACCOUNT", "2021-01-01", "2022-01-01"),
        ("EVT002", "ACC_OWNERSHIP", "2020-01-01", "2022-01-01"),
    ]

    results = validator.validate_event_batch(pairs)

    assert not results.empty
    assert len(results) <= len(pairs)


def test_compare_predicted_actual_trends(
    sample_observations, sample_events, sample_impact_links
):
    """Test trend comparison."""
    validator = ImpactValidator(sample_observations, sample_events, sample_impact_links)

    result = validator.compare_predicted_actual_trends(
        "ACC_MM_ACCOUNT", "2020-01-01", "2022-01-01"
    )

    assert "error" not in result
    assert "actual_slope" in result
    assert "num_events" in result


def test_validation_with_missing_data(
    sample_observations, sample_events, sample_impact_links
):
    """Test validation with incomplete data."""
    validator = ImpactValidator(sample_observations, sample_events, sample_impact_links)

    # Non-existent event
    result = validator.validate_against_historical(
        "EVT999", "ACC_MM_ACCOUNT", "2021-01-01", "2022-01-01"
    )
    assert "error" in result

    # Non-existent indicator
    result = validator.validate_against_historical(
        "EVT001", "NONEXISTENT", "2021-01-01", "2022-01-01"
    )
    assert "error" in result


def test_empty_validation_results():
    """Test behavior with no validation results."""
    validator = ImpactValidator(pd.DataFrame(), pd.DataFrame(), pd.DataFrame())

    result = validator.calculate_residuals([])
    assert result.empty
