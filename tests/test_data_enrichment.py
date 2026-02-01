"""
Unit tests for the DataEnricher class.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil
from src.data_enrichment import DataEnricher


@pytest.fixture
def sample_unified_data():
    """Create sample unified data for testing."""
    data = {
        "record_id": ["OBS001", "EVT001"],
        "record_type": ["observation", "event"],
        "pillar": ["access", None],
        "indicator_code": ["ACC_OWNERSHIP", None],
        "value_numeric": [46.0, None],
        "confidence": ["high", "high"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for output files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_data_enricher_initialization(sample_unified_data):
    """Test DataEnricher initialization."""
    enricher = DataEnricher(sample_unified_data)

    assert enricher.unified_data is not None
    assert len(enricher.unified_data) == 2
    assert len(enricher.enrichment_log) == 0


def test_add_observation(sample_unified_data):
    """Test adding a new observation record."""
    enricher = DataEnricher(sample_unified_data)
    initial_count = len(enricher.unified_data)

    enricher.add_observation(
        record_id="OBS_NEW001",
        pillar="usage",
        indicator="Digital Payment Usage",
        indicator_code="USG_DIGITAL_PAYMENT",
        value_numeric=35.0,
        observation_date="2024-01-01",
        source_name="Global Findex 2024",
        source_url="https://example.com",
        confidence="high",
        collected_by="Test User",
        notes="Test addition",
    )

    # Check that record was added
    assert len(enricher.unified_data) == initial_count + 1
    assert len(enricher.enrichment_log) == 1

    # Verify the added record
    new_record = enricher.unified_data[
        enricher.unified_data["record_id"] == "OBS_NEW001"
    ].iloc[0]
    assert new_record["record_type"] == "observation"
    assert new_record["pillar"] == "usage"
    assert new_record["value_numeric"] == 35.0


def test_add_observation_invalid_pillar(sample_unified_data):
    """Test error handling for invalid pillar."""
    enricher = DataEnricher(sample_unified_data)

    with pytest.raises(ValueError, match="Invalid pillar"):
        enricher.add_observation(
            record_id="OBS_INVALID",
            pillar="invalid_pillar",
            indicator="Test",
            indicator_code="TEST",
            value_numeric=10.0,
            observation_date="2024-01-01",
            source_name="Test",
            source_url="https://example.com",
            confidence="high",
            collected_by="Test User",
        )


def test_add_observation_invalid_confidence(sample_unified_data):
    """Test error handling for invalid confidence level."""
    enricher = DataEnricher(sample_unified_data)

    with pytest.raises(ValueError, match="Invalid confidence"):
        enricher.add_observation(
            record_id="OBS_INVALID",
            pillar="access",
            indicator="Test",
            indicator_code="TEST",
            value_numeric=10.0,
            observation_date="2024-01-01",
            source_name="Test",
            source_url="https://example.com",
            confidence="invalid_confidence",
            collected_by="Test User",
        )


def test_add_observation_invalid_date(sample_unified_data):
    """Test error handling for invalid date format."""
    enricher = DataEnricher(sample_unified_data)

    with pytest.raises(ValueError, match="Invalid date format"):
        enricher.add_observation(
            record_id="OBS_INVALID",
            pillar="access",
            indicator="Test",
            indicator_code="TEST",
            value_numeric=10.0,
            observation_date="01-01-2024",  # Wrong format
            source_name="Test",
            source_url="https://example.com",
            confidence="high",
            collected_by="Test User",
        )


def test_add_event(sample_unified_data):
    """Test adding a new event record."""
    enricher = DataEnricher(sample_unified_data)
    initial_count = len(enricher.unified_data)

    enricher.add_event(
        record_id="EVT_NEW001",
        title="New Policy Launch",
        category="policy",
        event_date="2023-01-01",
        source_name="NBE Report",
        source_url="https://example.com",
        confidence="high",
        collected_by="Test User",
        description="Test event",
        notes="Test addition",
    )

    # Check that record was added
    assert len(enricher.unified_data) == initial_count + 1
    assert len(enricher.enrichment_log) == 1

    # Verify the added record
    new_record = enricher.unified_data[
        enricher.unified_data["record_id"] == "EVT_NEW001"
    ].iloc[0]
    assert new_record["record_type"] == "event"
    assert new_record["category"] == "policy"
    assert pd.isna(new_record["pillar"])  # Events should not have pillar


def test_add_event_invalid_category(sample_unified_data):
    """Test error handling for invalid event category."""
    enricher = DataEnricher(sample_unified_data)

    with pytest.raises(ValueError, match="Invalid category"):
        enricher.add_event(
            record_id="EVT_INVALID",
            title="Test Event",
            category="invalid_category",
            event_date="2023-01-01",
            source_name="Test",
            source_url="https://example.com",
            confidence="high",
            collected_by="Test User",
        )


def test_add_impact_link(sample_unified_data):
    """Test adding a new impact link record."""
    enricher = DataEnricher(sample_unified_data)
    initial_count = len(enricher.unified_data)

    enricher.add_impact_link(
        record_id="IMP_NEW001",
        parent_id="EVT001",
        pillar="access",
        related_indicator="ACC_OWNERSHIP",
        impact_direction="positive",
        impact_magnitude="medium",
        lag_months=6,
        evidence_basis="comparable",
        confidence="medium",
        collected_by="Test User",
        notes="Test impact link",
    )

    # Check that record was added
    assert len(enricher.unified_data) == initial_count + 1
    assert len(enricher.enrichment_log) == 1

    # Verify the added record
    new_record = enricher.unified_data[
        enricher.unified_data["record_id"] == "IMP_NEW001"
    ].iloc[0]
    assert new_record["record_type"] == "impact_link"
    assert new_record["parent_id"] == "EVT001"
    assert new_record["impact_direction"] == "positive"


def test_add_impact_link_invalid_direction(sample_unified_data):
    """Test error handling for invalid impact direction."""
    enricher = DataEnricher(sample_unified_data)

    with pytest.raises(ValueError, match="Invalid impact_direction"):
        enricher.add_impact_link(
            record_id="IMP_INVALID",
            parent_id="EVT001",
            pillar="access",
            related_indicator="ACC_OWNERSHIP",
            impact_direction="invalid_direction",
            impact_magnitude="medium",
            collected_by="Test User",
        )


def test_add_impact_link_invalid_magnitude(sample_unified_data):
    """Test error handling for invalid impact magnitude."""
    enricher = DataEnricher(sample_unified_data)

    with pytest.raises(ValueError, match="Invalid impact_magnitude"):
        enricher.add_impact_link(
            record_id="IMP_INVALID",
            parent_id="EVT001",
            pillar="access",
            related_indicator="ACC_OWNERSHIP",
            impact_direction="positive",
            impact_magnitude="invalid_magnitude",
            collected_by="Test User",
        )


def test_validate_record_success(sample_unified_data):
    """Test record validation with valid record."""
    enricher = DataEnricher(sample_unified_data)

    valid_record = {
        "record_id": "TEST001",
        "record_type": "observation",
        "pillar": "access",
    }

    assert enricher.validate_record(valid_record) is True


def test_validate_record_missing_id(sample_unified_data):
    """Test record validation with missing record_id."""
    enricher = DataEnricher(sample_unified_data)

    invalid_record = {"record_type": "observation", "pillar": "access"}

    with pytest.raises(ValueError, match="must have 'record_id'"):
        enricher.validate_record(invalid_record)


def test_validate_record_invalid_type(sample_unified_data):
    """Test record validation with invalid record_type."""
    enricher = DataEnricher(sample_unified_data)

    invalid_record = {"record_id": "TEST001", "record_type": "invalid_type"}

    with pytest.raises(ValueError, match="Invalid record_type"):
        enricher.validate_record(invalid_record)


def test_export_enriched_data(sample_unified_data, temp_output_dir):
    """Test exporting enriched data to CSV."""
    enricher = DataEnricher(sample_unified_data)

    # Add a record
    enricher.add_observation(
        record_id="OBS_NEW001",
        pillar="access",
        indicator="Test",
        indicator_code="TEST",
        value_numeric=10.0,
        observation_date="2024-01-01",
        source_name="Test",
        source_url="https://example.com",
        confidence="high",
        collected_by="Test User",
    )

    # Export data
    output_path = Path(temp_output_dir) / "enriched_data.csv"
    enricher.export_enriched_data(str(output_path))

    # Verify file was created
    assert output_path.exists()

    # Verify contents
    loaded_data = pd.read_csv(output_path)
    assert len(loaded_data) == 3  # Original 2 + 1 new


def test_export_enrichment_log(sample_unified_data, temp_output_dir):
    """Test exporting enrichment log to markdown."""
    enricher = DataEnricher(sample_unified_data)

    # Add some records
    enricher.add_observation(
        record_id="OBS_NEW001",
        pillar="access",
        indicator="Test",
        indicator_code="TEST",
        value_numeric=10.0,
        observation_date="2024-01-01",
        source_name="Test",
        source_url="https://example.com",
        confidence="high",
        collected_by="Test User",
    )

    enricher.add_event(
        record_id="EVT_NEW001",
        title="Test Event",
        category="policy",
        event_date="2023-01-01",
        source_name="Test",
        source_url="https://example.com",
        confidence="high",
        collected_by="Test User",
    )

    # Export log
    output_path = Path(temp_output_dir) / "enrichment_log.md"
    enricher.export_enrichment_log(str(output_path))

    # Verify file was created
    assert output_path.exists()

    # Verify contents
    with open(output_path, "r") as f:
        content = f.read()
        assert "Data Enrichment Log" in content
        assert "OBS_NEW001" in content
        assert "EVT_NEW001" in content


def test_get_enriched_data(sample_unified_data):
    """Test getting enriched data."""
    enricher = DataEnricher(sample_unified_data)

    enricher.add_observation(
        record_id="OBS_NEW001",
        pillar="access",
        indicator="Test",
        indicator_code="TEST",
        value_numeric=10.0,
        observation_date="2024-01-01",
        source_name="Test",
        source_url="https://example.com",
        confidence="high",
        collected_by="Test User",
    )

    enriched = enricher.get_enriched_data()

    assert len(enriched) == 3
    assert "OBS_NEW001" in enriched["record_id"].values


def test_get_enrichment_summary(sample_unified_data):
    """Test getting enrichment summary."""
    enricher = DataEnricher(sample_unified_data)

    # Add multiple records
    enricher.add_observation(
        record_id="OBS_NEW001",
        pillar="access",
        indicator="Test",
        indicator_code="TEST",
        value_numeric=10.0,
        observation_date="2024-01-01",
        source_name="Test",
        source_url="https://example.com",
        confidence="high",
        collected_by="User1",
    )

    enricher.add_event(
        record_id="EVT_NEW001",
        title="Test Event",
        category="policy",
        event_date="2023-01-01",
        source_name="Test",
        source_url="https://example.com",
        confidence="high",
        collected_by="User2",
    )

    summary = enricher.get_enrichment_summary()

    assert summary["total_additions"] == 2
    assert summary["current_total_records"] == 4
    assert "observation" in summary["additions_by_type"]
    assert "event" in summary["additions_by_type"]
    assert "User1" in summary["contributors"]
    assert "User2" in summary["contributors"]
