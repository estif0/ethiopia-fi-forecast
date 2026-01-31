"""
Unit tests for the DataLoader class.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil
from src.data_loader import DataLoader


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_unified_data():
    """Create sample unified data for testing."""
    data = {
        "record_id": ["OBS001", "OBS002", "EVT001", "IMP001", "TGT001"],
        "record_type": ["observation", "observation", "event", "impact_link", "target"],
        "pillar": ["access", "usage", None, "access", "access"],
        "indicator_code": [
            "ACC_OWNERSHIP",
            "USG_DIGITAL_PAYMENT",
            None,
            None,
            "ACC_OWNERSHIP",
        ],
        "value_numeric": [46.0, 35.0, None, None, 60.0],
        "observation_date": ["2021-01-01", "2021-01-01", None, None, "2027-12-31"],
        "event_date": [None, None, "2021-05-15", None, None],
        "category": [None, None, "product_launch", None, None],
        "confidence": ["high", "high", "high", "medium", "high"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_reference_codes():
    """Create sample reference codes for testing."""
    data = {
        "field_name": ["record_type", "record_type", "pillar", "pillar"],
        "valid_value": ["observation", "event", "access", "usage"],
        "description": [
            "Measured value",
            "Policy/event",
            "Account ownership",
            "Digital payments",
        ],
    }
    return pd.DataFrame(data)


def test_data_loader_initialization():
    """Test DataLoader initialization."""
    loader = DataLoader(data_dir="data/raw")
    assert loader.data_dir == Path("data/raw")
    assert loader.unified_data is None
    assert loader.reference_codes is None


def test_load_unified_data_success(temp_data_dir, sample_unified_data):
    """Test successful loading of unified data."""
    # Save sample data to temp directory
    csv_path = Path(temp_data_dir) / "test_data.csv"
    sample_unified_data.to_csv(csv_path, index=False)

    # Load data
    loader = DataLoader(data_dir=temp_data_dir)
    df = loader.load_unified_data(filename="test_data.csv")

    assert df is not None
    assert len(df) == 5
    assert loader.unified_data is not None
    assert "record_type" in df.columns


def test_load_unified_data_file_not_found():
    """Test error handling when data file doesn't exist."""
    loader = DataLoader(data_dir="nonexistent_dir")

    with pytest.raises(FileNotFoundError):
        loader.load_unified_data()


def test_load_unified_data_invalid_schema(temp_data_dir):
    """Test validation of data with missing required columns."""
    # Create data missing required columns
    invalid_data = pd.DataFrame({"col1": [1, 2, 3]})
    csv_path = Path(temp_data_dir) / "invalid_data.csv"
    invalid_data.to_csv(csv_path, index=False)

    loader = DataLoader(data_dir=temp_data_dir)

    with pytest.raises(ValueError, match="Missing required columns"):
        loader.load_unified_data(filename="invalid_data.csv")


def test_load_unified_data_invalid_record_type(temp_data_dir):
    """Test validation with invalid record_type values."""
    # Create data with invalid record_type
    invalid_data = pd.DataFrame(
        {"record_id": ["TEST001"], "record_type": ["invalid_type"]}
    )
    csv_path = Path(temp_data_dir) / "invalid_type.csv"
    invalid_data.to_csv(csv_path, index=False)

    loader = DataLoader(data_dir=temp_data_dir)

    with pytest.raises(ValueError, match="Invalid record_type values"):
        loader.load_unified_data(filename="invalid_type.csv")


def test_load_reference_codes_success(temp_data_dir, sample_reference_codes):
    """Test successful loading of reference codes."""
    csv_path = Path(temp_data_dir) / "ref_codes.csv"
    sample_reference_codes.to_csv(csv_path, index=False)

    loader = DataLoader(data_dir=temp_data_dir)
    df = loader.load_reference_codes(filename="ref_codes.csv")

    assert df is not None
    assert len(df) == 4
    assert loader.reference_codes is not None


def test_load_reference_codes_file_not_found():
    """Test error handling when reference codes file doesn't exist."""
    loader = DataLoader(data_dir="nonexistent_dir")

    with pytest.raises(FileNotFoundError):
        loader.load_reference_codes()


def test_validate_schema_success(temp_data_dir, sample_unified_data):
    """Test schema validation on loaded data."""
    csv_path = Path(temp_data_dir) / "test_data.csv"
    sample_unified_data.to_csv(csv_path, index=False)

    loader = DataLoader(data_dir=temp_data_dir)
    loader.load_unified_data(filename="test_data.csv")

    results = loader.validate_schema()

    assert results["total_records"] == 5
    assert "observation" in results["record_type_counts"]
    assert results["record_type_counts"]["observation"] == 2


def test_validate_schema_no_data_loaded():
    """Test that validate_schema raises error when no data is loaded."""
    loader = DataLoader()

    with pytest.raises(RuntimeError, match="No data loaded"):
        loader.validate_schema()


def test_get_records_by_type(temp_data_dir, sample_unified_data):
    """Test filtering records by type."""
    csv_path = Path(temp_data_dir) / "test_data.csv"
    sample_unified_data.to_csv(csv_path, index=False)

    loader = DataLoader(data_dir=temp_data_dir)
    loader.load_unified_data(filename="test_data.csv")

    # Test getting observations
    observations = loader.get_records_by_type("observation")
    assert len(observations) == 2
    assert all(observations["record_type"] == "observation")

    # Test getting events
    events = loader.get_records_by_type("event")
    assert len(events) == 1
    assert all(events["record_type"] == "event")


def test_get_records_by_type_invalid(temp_data_dir, sample_unified_data):
    """Test error handling for invalid record type."""
    csv_path = Path(temp_data_dir) / "test_data.csv"
    sample_unified_data.to_csv(csv_path, index=False)

    loader = DataLoader(data_dir=temp_data_dir)
    loader.load_unified_data(filename="test_data.csv")

    with pytest.raises(ValueError, match="Invalid record_type"):
        loader.get_records_by_type("invalid_type")


def test_get_records_by_type_no_data():
    """Test error when trying to filter without loaded data."""
    loader = DataLoader()

    with pytest.raises(RuntimeError, match="No data loaded"):
        loader.get_records_by_type("observation")


def test_get_indicators(temp_data_dir, sample_unified_data):
    """Test getting list of unique indicators."""
    csv_path = Path(temp_data_dir) / "test_data.csv"
    sample_unified_data.to_csv(csv_path, index=False)

    loader = DataLoader(data_dir=temp_data_dir)
    loader.load_unified_data(filename="test_data.csv")

    indicators = loader.get_indicators()

    assert "ACC_OWNERSHIP" in indicators
    assert "USG_DIGITAL_PAYMENT" in indicators
    assert len(indicators) == 2


def test_get_indicators_no_data():
    """Test error when getting indicators without loaded data."""
    loader = DataLoader()

    with pytest.raises(RuntimeError, match="No data loaded"):
        loader.get_indicators()


def test_summary_no_data(capsys):
    """Test summary output when no data is loaded."""
    loader = DataLoader()
    loader.summary()

    captured = capsys.readouterr()
    assert "No data loaded yet" in captured.out


def test_summary_with_data(temp_data_dir, sample_unified_data, capsys):
    """Test summary output with loaded data."""
    csv_path = Path(temp_data_dir) / "test_data.csv"
    sample_unified_data.to_csv(csv_path, index=False)

    loader = DataLoader(data_dir=temp_data_dir)
    loader.load_unified_data(filename="test_data.csv")
    loader.summary()

    captured = capsys.readouterr()
    assert "ETHIOPIA FINANCIAL INCLUSION DATASET SUMMARY" in captured.out
    assert "Total Records: 5" in captured.out
    assert "observation" in captured.out
