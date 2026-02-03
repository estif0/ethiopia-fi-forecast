"""Tests for ImpactModel class."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.impact_model import ImpactModel


@pytest.fixture
def sample_data():
    """Create sample unified dataset for testing."""
    data = pd.DataFrame(
        [
            # Events
            {
                "record_id": "EVT001",
                "record_type": "event",
                "description": "Telebirr Launch",
                "event_date": "2021-05-01",
                "category": "product_launch",
                "indicator_code": None,
                "value_numeric": None,
            },
            {
                "record_id": "EVT002",
                "record_type": "event",
                "description": "Policy Change",
                "event_date": "2020-01-01",
                "category": "policy",
                "indicator_code": None,
                "value_numeric": None,
            },
            # Observations
            {
                "record_id": "OBS001",
                "record_type": "observation",
                "indicator_code": "ACC_MM_ACCOUNT",
                "observation_date": "2021-01-01",
                "value_numeric": 10.0,
                "description": None,
                "event_date": None,
                "category": None,
            },
            {
                "record_id": "OBS002",
                "record_type": "observation",
                "indicator_code": "ACC_OWNERSHIP",
                "observation_date": "2021-01-01",
                "value_numeric": 35.0,
                "description": None,
                "event_date": None,
                "category": None,
            },
            # Impact links
            {
                "record_id": "IMP001",
                "record_type": "impact_link",
                "parent_id": "EVT001",
                "indicator_code": "ACC_MM_ACCOUNT",
                "impact_direction": "positive",
                "impact_magnitude": 0.5,
                "description": None,
                "event_date": None,
                "category": None,
                "value_numeric": None,
            },
            {
                "record_id": "IMP002",
                "record_type": "impact_link",
                "parent_id": "EVT002",
                "indicator_code": "ACC_OWNERSHIP",
                "impact_direction": "positive",
                "impact_magnitude": 0.3,
                "description": None,
                "event_date": None,
                "category": None,
                "value_numeric": None,
            },
        ]
    )
    return data


def test_impact_model_initialization(sample_data):
    """Test ImpactModel initialization."""
    model = ImpactModel(sample_data)
    assert model.data is not None
    assert len(model.data) == len(sample_data)


def test_load_impact_links(sample_data):
    """Test loading impact link records."""
    model = ImpactModel(sample_data)
    impact_links = model.load_impact_links()

    assert impact_links is not None
    assert len(impact_links) == 2
    assert "parent_id" in impact_links.columns
    assert model.events is not None
    assert model.observations is not None


def test_create_event_indicator_matrix(sample_data):
    """Test creation of event-indicator association matrix."""
    model = ImpactModel(sample_data)
    matrix = model.create_event_indicator_matrix()

    assert matrix is not None
    assert "ACC_MM_ACCOUNT" in matrix.columns
    assert "ACC_OWNERSHIP" in matrix.columns
    assert "EVT001" in matrix.index
    assert matrix.loc["EVT001", "ACC_MM_ACCOUNT"] == 0.5  # positive * magnitude


def test_apply_lag_effects():
    """Test lag effect calculation."""
    model = ImpactModel(pd.DataFrame())

    # Event hasn't happened yet
    lag = model.apply_lag_effects("2020-01-01", "2020-06-01", lag_months=6)
    assert lag == 0.0

    # Event just happened
    lag = model.apply_lag_effects("2020-06-01", "2020-01-01", lag_months=6)
    assert 0.8 < lag <= 1.0

    # Impact fully realized
    lag = model.apply_lag_effects("2021-01-01", "2020-01-01", lag_months=6)
    assert lag == 1.0


def test_estimate_impact(sample_data):
    """Test impact estimation for event-indicator pair."""
    model = ImpactModel(sample_data)
    model.create_event_indicator_matrix()

    result = model.estimate_impact(
        "EVT001", "ACC_MM_ACCOUNT", baseline_value=10.0, observation_date="2022-01-01"
    )

    assert "impact" in result
    assert "direction" in result
    assert "confidence" in result
    assert result["direction"] == 1  # positive


def test_combine_multiple_events(sample_data):
    """Test combining impacts from multiple events."""
    model = ImpactModel(sample_data)
    model.create_event_indicator_matrix()

    result = model.combine_multiple_events(
        ["EVT001", "EVT002"],
        "ACC_OWNERSHIP",
        baseline_value=35.0,
        observation_date="2022-01-01",
    )

    assert "combined_impact" in result
    assert "individual_impacts" in result
    assert len(result["individual_impacts"]) <= 2


def test_get_events_for_indicator(sample_data):
    """Test getting events that impact a specific indicator."""
    model = ImpactModel(sample_data)
    model.create_event_indicator_matrix()

    events = model.get_events_for_indicator("ACC_MM_ACCOUNT")

    assert not events.empty
    assert "description" in events.columns
    assert "event_date" in events.columns


def test_get_indicators_for_event(sample_data):
    """Test getting indicators impacted by a specific event."""
    model = ImpactModel(sample_data)
    model.create_event_indicator_matrix()

    indicators = model.get_indicators_for_event("EVT001")

    assert not indicators.empty
    assert "indicator_code" in indicators.columns
    assert "impact_value" in indicators.columns


def test_empty_data():
    """Test model behavior with empty dataset."""
    empty_data = pd.DataFrame()
    model = ImpactModel(empty_data)

    with pytest.raises(Exception):
        model.load_impact_links()


def test_missing_parent_id():
    """Test handling of impact_links without parent_id."""
    data = pd.DataFrame(
        [
            {
                "record_id": "IMP001",
                "record_type": "impact_link",
                "indicator_code": "ACC_MM_ACCOUNT",
                "impact_direction": "positive",
            }
        ]
    )

    model = ImpactModel(data)
    with pytest.raises(Exception):
        model.load_impact_links()
