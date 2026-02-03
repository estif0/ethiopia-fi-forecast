# Source Code Modules

This directory contains modular, object-oriented Python code for the Ethiopia Financial Inclusion Forecasting project.

## Modules Overview
- **data_loader.py**: Load and validate datasets
- **data_enrichment.py**: Add new records with validation
- **data_processor.py**: Transform and aggregate data
- **visualizations.py**: Create analysis visualizations
- **impact_model.py**: Model event impacts on indicators
- **impact_validator.py**: Validate impact models against historical data
- **forecaster.py**: Generate forecasts with uncertainty quantification

---

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

### `data_processor.py`
**DataProcessor class** - Process and analyze financial inclusion data.

**Usage:**
```python
from src.data_loader import DataLoader
from src.data_processor import DataProcessor

# Load data
loader = DataLoader(data_dir="data/processed")
data = loader.load_unified_data('ethiopia_fi_enriched.csv')
ref_codes = loader.load_reference_codes()

# Initialize processor
processor = DataProcessor(data, ref_codes)

# Filter by record type
observations = processor.filter_by_record_type(['observation'])
events = processor.filter_by_record_type(['event'])

# Extract time series
acc_ts = processor.get_time_series('ACC_OWNERSHIP')
mm_ts = processor.get_time_series('ACC_MM_ACCOUNT', disaggregate_by='gender')

# Calculate growth rates
growth = processor.calculate_growth_rates('ACC_OWNERSHIP', period_type='percentage')
abs_growth = processor.calculate_growth_rates('ACC_OWNERSHIP', period_type='absolute')

# Analyze data quality
quality = processor.get_data_quality_summary()
coverage = processor.get_temporal_coverage()

# Get disaggregated data
gender_data = processor.get_disaggregated_data(dimension='gender')

# Event analysis
event_summary = processor.get_event_summary()

# Prepare for plotting with events
ts, events_df = processor.prepare_indicator_for_plotting(
    'ACC_OWNERSHIP',
    include_events=True
)
```

**Key Methods:**
- `filter_by_record_type()` - Filter by observation/event/impact_link/target
- `get_time_series()` - Extract time series with optional disaggregation
- `calculate_growth_rates()` - Compute absolute/percentage/annualized growth
- `get_disaggregated_data()` - Group by gender/urban-rural/age
- `get_temporal_coverage()` - Analyze observation span by indicator
- `get_data_quality_summary()` - Comprehensive quality metrics
- `get_correlation_matrix()` - Calculate indicator correlations
- `get_event_summary()` - Summarize events by category and year
- `prepare_indicator_for_plotting()` - Align indicators with events

### `visualizations.py`
**FinancialInclusionVisualizer class** - Create publication-ready visualizations.

**Usage:**
```python
from src.visualizations import FinancialInclusionVisualizer
from src.data_processor import DataProcessor
import matplotlib.pyplot as plt

# Initialize visualizer
viz = FinancialInclusionVisualizer()

# Plot indicator trend
acc_ts = processor.get_time_series('ACC_OWNERSHIP')
fig = viz.plot_indicator_trend(
    acc_ts,
    indicator_code='ACC_OWNERSHIP',
    indicator_name='Account Ownership Rate (%)'
)
plt.savefig('acc_ownership.png', dpi=300, bbox_inches='tight')

# Overlay events on trend
ts, events = processor.prepare_indicator_for_plotting('ACC_OWNERSHIP', include_events=True)
fig = viz.plot_events_overlay(
    ts,
    events,
    indicator_code='ACC_OWNERSHIP',
    indicator_name='Account Ownership Rate (%)'
)

# Plot growth rates
growth = processor.calculate_growth_rates('ACC_OWNERSHIP')
fig = viz.plot_growth_rates(
    growth,
    indicator_code='ACC_OWNERSHIP',
    indicator_name='Account Ownership'
)

# Data quality visualization
quality = processor.get_data_quality_summary()
fig = viz.plot_data_quality_summary(quality)

# Temporal coverage timeline
coverage = processor.get_temporal_coverage()
fig = viz.plot_timeline(coverage, title="Temporal Coverage by Indicator")

# Interactive timeline (Plotly)
interactive_fig = viz.create_interactive_timeline(
    acc_ts,
    events,
    indicator_code='ACC_OWNERSHIP'
)
```

**Key Methods:**
- `plot_timeline()` - Temporal coverage horizontal bars
- `plot_indicator_trend()` - Time series with confidence coloring
- `plot_events_overlay()` - Events as vertical lines on trends
- `plot_correlation_matrix()` - Seaborn heatmap
- `plot_growth_rates()` - Bar charts color-coded by direction
- `plot_data_quality_summary()` - 4-panel quality assessment
- `plot_pillar_comparison()` - Dual bar charts by pillar
- `create_interactive_timeline()` - Plotly interactive figure

**Color Schemes:**
- Pillars: Access (blue), Usage (purple), Infrastructure (orange)
- Events: product_launch (green), policy (blue), infrastructure (orange), milestone (red)

### `impact_model.py`
**ImpactModel class** - Model event impacts on financial inclusion indicators.

**Usage:**
```python
from src.data_loader import DataLoader
from src.impact_model import ImpactModel

# Load data
loader = DataLoader()
data = loader.load_unified_data()

# Initialize impact model
model = ImpactModel(data)

# Load and analyze impact links
impact_links = model.load_impact_links()

# Create event-indicator association matrix
matrix = model.create_event_indicator_matrix()

# Estimate impact for specific event-indicator pair
impact = model.estimate_impact(
    event_id='EVT001',
    indicator_code='ACC_MM_ACCOUNT',
    baseline_value=10.0,
    observation_date='2022-01-01'
)

# Combine impacts from multiple events
combined = model.combine_multiple_events(
    event_ids=['EVT001', 'EVT002'],
    indicator_code='ACC_OWNERSHIP',
    baseline_value=35.0,
    observation_date='2022-01-01'
)

# Get events affecting a specific indicator
events = model.get_events_for_indicator('ACC_OWNERSHIP', min_magnitude=0.1)

# Get indicators affected by a specific event
indicators = model.get_indicators_for_event('EVT001')
```

**Key Methods:**
- `load_impact_links()` - Load and parse impact relationship records
- `create_event_indicator_matrix()` - Build event-indicator association matrix
- `apply_lag_effects()` - Model temporal lag between event and impact
- `estimate_impact()` - Calculate impact magnitude for event-indicator pair
- `combine_multiple_events()` - Aggregate impacts from concurrent events
- `get_events_for_indicator()` - Find events impacting an indicator
- `get_indicators_for_event()` - Find indicators impacted by an event

### `impact_validator.py`
**ImpactValidator class** - Validate impact models against historical observations.

**Usage:**
```python
from src.data_loader import DataLoader
from src.impact_validator import ImpactValidator

# Load data
loader = DataLoader()
data = loader.load_unified_data()

observations = data[data['record_type'] == 'observation']
events = data[data['record_type'] == 'event']
impact_links = data[data['record_type'] == 'impact_link']

# Initialize validator
validator = ImpactValidator(observations, events, impact_links)

# Validate specific event impact
result = validator.validate_against_historical(
    event_id='EVT001',
    indicator_code='ACC_MM_ACCOUNT',
    pre_period_end='2021-01-01',
    post_period_end='2022-01-01'
)

# Calculate residuals
residuals_df, summary = validator.calculate_residuals()

# Generate validation report
report = validator.generate_validation_report()
print(report)

# Batch validation
pairs = [
    ('EVT001', 'ACC_MM_ACCOUNT', '2021-01-01', '2022-01-01'),
    ('EVT002', 'ACC_OWNERSHIP', '2020-01-01', '2022-01-01')
]
results_df = validator.validate_event_batch(pairs)

# Compare predicted vs actual trends
trend_comparison = validator.compare_predicted_actual_trends(
    'ACC_OWNERSHIP',
    start_date='2020-01-01',
    end_date='2024-01-01'
)
```

**Key Methods:**
- `validate_against_historical()` - Compare predicted vs actual impact
- `calculate_residuals()` - Measure prediction errors across validations
- `generate_validation_report()` - Create formatted report
- `validate_event_batch()` - Validate multiple event-indicator pairs
- `compare_predicted_actual_trends()` - Compare overall trends

---

### `forecaster.py`
**FinancialInclusionForecaster class** - Generate forecasts for financial inclusion indicators using multiple methodologies.

**Usage:**
```python
from src.data_loader import DataLoader
from src.forecaster import FinancialInclusionForecaster

# Load observations
loader = DataLoader()
observations = loader.get_observations()

# Initialize forecaster
forecaster = FinancialInclusionForecaster(observations)

# Fit trend model
model_info = forecaster.fit_trend_model(
    'ACC_OWNERSHIP',
    trend_type='linear'  # or 'polynomial', 'exponential'
)

# Generate forecast with confidence intervals
forecast = forecaster.forecast_trend(
    model_info,
    forecast_years=[2025, 2026, 2027],
    confidence_level=0.95
)

# Generate scenario forecasts
scenarios = forecaster.generate_scenarios(
    'ACC_OWNERSHIP',
    forecast_years=[2025, 2026, 2027],
    scenario_assumptions={
        'optimistic_multiplier': 1.3,
        'base_multiplier': 1.0,
        'pessimistic_multiplier': 0.7
    }
)

# Event-augmented forecasting
events_data = loader.get_events()
forecaster = FinancialInclusionForecaster(
    observations,
    events_data=events_data
)

base_forecast = forecaster.forecast_trend(model_info, [2025, 2026, 2027])
future_events = events_data[events_data['event_date'] >= '2025-01-01']
adjusted = forecaster.apply_event_adjustments(
    base_forecast,
    future_events,
    adjustment_method='additive'
)

# Comprehensive forecast with multiple methods
results = forecaster.forecast_with_uncertainty(
    'ACC_OWNERSHIP',
    forecast_years=[2025, 2026, 2027],
    methods=['trend', 'scenarios']
)

# Get summary across methods
summary = forecaster.get_forecast_summary('ACC_OWNERSHIP')

# Export forecasts
output_files = forecaster.export_forecasts(output_dir='models/')
```

**Key Methods:**
- `fit_trend_model()` - Fit trend model (linear, polynomial, exponential)
- `forecast_trend()` - Generate forecast with confidence intervals
- `apply_event_adjustments()` - Adjust forecast based on anticipated events
- `generate_scenarios()` - Create optimistic/base/pessimistic scenarios
- `forecast_with_uncertainty()` - Comprehensive forecast with multiple methods
- `get_forecast_summary()` - Summarize forecasts across methods
- `export_forecasts()` - Save forecast results to CSV files

**Supported Approaches:**
- **Trend Regression**: Linear, polynomial, exponential extrapolation
- **Event-Augmented**: Base trend + anticipated event impacts
- **Scenario Analysis**: Multiple growth rate assumptions
- **Uncertainty Quantification**: Confidence intervals using t-distribution

---

## Code Standards

- **Type Hints**: All functions use type hints
- **Docstrings**: Google-style docstrings for all classes and methods
- **Error Handling**: Specific exceptions with helpful messages
- **Testing**: Each module has corresponding test file in `tests/`
