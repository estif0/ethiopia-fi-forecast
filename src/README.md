# Source Code Modules

This directory contains modular, object-oriented Python code for the Ethiopia Financial Inclusion Forecasting project.

## Modules

### `data_loader.py`
**DataLoader class** - Load and validate financial inclusion datasets.

**Usage:**
```python
from src.data_loader import DataLoader

# Initialize loader
loader = DataLoader(data_dir="data/raw")

# Load datasets
unified_data = loader.load_unified_data()
reference_codes = loader.load_reference_codes()

# Get specific record types
observations = loader.get_records_by_type('observation')
events = loader.get_records_by_type('event')

# Validate and summarize
validation_results = loader.validate_schema()
loader.summary()

# Get list of indicators
indicators = loader.get_indicators()
```

**Key Methods:**
- `load_unified_data()` - Load main dataset with schema validation
- `load_reference_codes()` - Load categorical field reference codes
- `get_records_by_type()` - Filter by record_type (observation, event, impact_link, target)
- `validate_schema()` - Comprehensive schema validation
- `get_indicators()` - List unique indicator codes
- `summary()` - Print dataset overview

### `data_enrichment.py`
**DataEnricher class** - Add new records to the unified dataset with validation.

**Usage:**
```python
from src.data_loader import DataLoader
from src.data_enrichment import DataEnricher

# Load existing data
loader = DataLoader(data_dir="data/raw")
unified_data = loader.load_unified_data()

# Initialize enricher
enricher = DataEnricher(unified_data)

# Add new observation
enricher.add_observation(
    record_id='OBS_NEW001',
    pillar='access',
    indicator='Account Ownership Rate',
    indicator_code='ACC_OWNERSHIP',
    value_numeric=52.0,
    observation_date='2025-01-01',
    source_name='NBE Report 2025',
    source_url='https://nbe.gov.et/report',
    confidence='high',
    collected_by='Your Name',
    notes='Why this data is useful'
)

# Add new event
enricher.add_event(
    record_id='EVT_NEW001',
    title='New Mobile Money Regulation',
    category='policy',
    event_date='2024-06-01',
    source_name='NBE Directive',
    source_url='https://nbe.gov.et/directive',
    confidence='high',
    collected_by='Your Name',
    notes='Expected to increase competition'
)

# Add impact link
enricher.add_impact_link(
    record_id='IMP_NEW001',
    parent_id='EVT_NEW001',
    pillar='access',
    related_indicator='ACC_MM_ACCOUNT',
    impact_direction='positive',
    impact_magnitude='medium',
    lag_months=12,
    evidence_basis='comparable',
    confidence='medium',
    collected_by='Your Name'
)

# Export enriched data
enricher.export_enriched_data('data/processed/ethiopia_fi_enriched.csv')
enricher.export_enrichment_log('data/processed/data_enrichment_log.md')
```

**Key Methods:**
- `add_observation()` - Add new observation with full documentation
- `add_event()` - Add new event (no pillar - effects via impact_links)
- `add_impact_link()` - Link events to indicator impacts
- `validate_record()` - Validate record schema compliance
- `export_enriched_data()` - Save enriched dataset
- `export_enrichment_log()` - Save log of all additions
- `get_enrichment_summary()` - Get statistics on additions

---

## Development Guidelines

- **Type Hints**: All functions use type hints
- **Docstrings**: Google-style docstrings for all classes and methods
- **Error Handling**: Specific exceptions with helpful messages
- **Testing**: Each module has corresponding test file in `tests/`
