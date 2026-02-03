# Data Directory

This directory contains raw and processed datasets for the Ethiopia Financial Inclusion Forecasting project.

## Directory Structure

```
data/
├── raw/                              # Original datasets (never modify)
│   ├── ethiopia_fi_unified_data.csv  # Base dataset (29 records)
│   └── reference_codes.csv           # Indicator and category codes
└── processed/                        # Enriched and processed data
    ├── ethiopia_fi_enriched.csv      # Enriched dataset (60 records)
    └── data_enrichment_log.md        # Documentation of additions
```

---

## Raw Data Files

### `ethiopia_fi_unified_data.csv`
**Original baseline dataset** provided by Selam Analytics.

- **Records**: 29 total
  - 18 observations (financial inclusion metrics)
  - 7 events (major policy/product launches)
  - 3 impact_link records (event-indicator relationships)
  - 1 target record (2027 goal)
- **Temporal Coverage**: 2011-2024
- **Source**: Global Findex Database, National Bank of Ethiopia
- **Note**: DO NOT MODIFY - This is the immutable baseline

### `reference_codes.csv`
**Lookup table** for indicator codes and categories.

- Indicator definitions (ACC_OWNERSHIP, USG_DIGITAL_PAYMENT, etc.)
- Event categories (policy, product_launch, infrastructure, milestone)
- Pillar classifications (Access, Usage, Infrastructure)
- Description and unit information

---

## Processed Data Files

### `ethiopia_fi_enriched.csv`
**Enriched dataset** created in Task 1 with additional research.

- **Records**: 60 total (+31 new records)
  - 36 observations (+18 new)
  - 15 events (+8 new)
  - 6 impact_link records (+3 new)
  - 3 target records (+2 new)
- **New Additions**:
  - Mobile money penetration data (2018, 2022)
  - Infrastructure metrics (4G coverage, mobile penetration, ATM density)
  - Active account rates and usage metrics
  - Major events (Telebirr launch, M-Pesa entry, policy changes)
  - Impact links connecting events to expected effects
- **Documentation**: All additions logged in `data_enrichment_log.md`
- **Quality**: All new records include confidence level and source URL

### `data_enrichment_log.md`
**Detailed log** of all data enrichment activities.

- Record-by-record documentation
- Source URLs for each addition
- Confidence level justifications
- Rationale for assumptions
- Quality assessment notes

---

## Data Schema

All datasets use a **unified schema** differentiated by `record_type` field:

### Common Fields (All Record Types)
```
- id: Unique identifier (e.g., OBS001, EVT001, IMP001)
- record_type: Type of record (observation, event, impact_link, target)
- title: Human-readable description
- source_type: Category of data source
- source_url: Reference URL (if available)
- confidence: Data quality (high, medium, low)
- notes: Additional context
```

### Record Type: `observation`
**Actual measurements** of financial inclusion indicators.

```
Specific Fields:
- indicator_code: Code identifying the metric (e.g., ACC_OWNERSHIP)
- pillar: Financial inclusion pillar (Access, Usage, Infrastructure)
- value_numeric: Numeric value (typically percentage or count)
- unit: Unit of measurement (percent, millions, per_100k_adults)
- observation_date: Date of measurement (YYYY-MM-DD)
- disaggregation: Breakdown dimension (gender, age, etc.) if applicable
- disaggregation_value: Specific segment (e.g., "female")

Example:
id: OBS001
record_type: observation
indicator_code: ACC_OWNERSHIP
pillar: Access
value_numeric: 36.1
unit: percent
observation_date: 2024-12-31
title: "Account ownership rate (% age 15+)"
source_type: Global Findex
confidence: high
```

### Record Type: `event`
**Major policy changes, product launches, and milestones** that may impact financial inclusion.

```
Specific Fields:
- category: Type of event (policy, product_launch, infrastructure, milestone)
- event_date: Date event occurred (YYYY-MM-DD)

Note: Events do NOT have a pillar field
Effects are captured via impact_link records

Example:
id: EVT001
record_type: event
category: product_launch
event_date: 2021-05-15
title: "Telebirr Launch (Ethio Telecom)"
source_type: Press Release
confidence: high
notes: "Mobile money platform launched with 15M registrations in 6 months"
```

### Record Type: `impact_link`
**Relationships** between events and indicators, defining expected impacts.

```
Specific Fields:
- parent_id: ID of the event causing impact (e.g., EVT001)
- related_indicator: Indicator code affected (e.g., ACC_MM_ACCOUNT)
- impact_direction: Expected direction (positive, negative, neutral)
- impact_magnitude: Strength of impact (0.0 to 1.0 scale)
- lag_months: Expected delay before effect appears (0-12 months)

Example:
id: IMP001
record_type: impact_link
parent_id: EVT001
related_indicator: ACC_MM_ACCOUNT
impact_direction: positive
impact_magnitude: 0.8
lag_months: 3
title: "Telebirr → Mobile Money Growth"
confidence: high
notes: "Expected to significantly increase mobile money adoption"
```

### Record Type: `target`
**Forecast targets** for financial inclusion goals (2025-2027).

```
Specific Fields:
- indicator_code: Code identifying the target metric
- target_year: Year of target (2025, 2026, 2027)
- target_value: Target value to achieve
- unit: Unit of measurement

Example:
id: TGT001
record_type: target
indicator_code: ACC_OWNERSHIP
target_year: 2027
target_value: 50.0
unit: percent
title: "Account ownership target for 2027"
source_type: NBE Strategy
confidence: medium
```

---

## Key Indicators

### Access Pillar (Account Ownership)
- **ACC_OWNERSHIP**: Overall account ownership rate (% age 15+)
- **ACC_MM_ACCOUNT**: Mobile money account ownership (% age 15+)
- **ACC_FI_ACCOUNT**: Formal financial institution account (% age 15+)
- **ACC_FAYDA**: Fayda agent network coverage (agents per 10k adults)

### Usage Pillar (Transaction Activity)
- **USG_DIGITAL_PAYMENT**: Digital payment usage (% age 15+)
- **USG_ACTIVE_RATE**: Active account rate (% of accounts used in 90 days)

### Infrastructure Pillar (Enabling Environment)
- **ACC_4G_COV**: 4G network coverage (% of population)
- **ACC_MOBILE_PEN**: Mobile phone penetration (% of population)
- **ACC_ATM_DENSITY**: ATM density (ATMs per 100k adults)

---

## Data Quality Notes

### Strengths
- **High Confidence**: >90% of observations from Global Findex (gold standard)
- **Consistent Schema**: Unified structure across all record types
- **Well Documented**: All enrichments logged with sources
- **Recent Data**: Includes 2024 Findex release

### Limitations
- **Temporal Sparsity**: Only 5 Findex survey points over 13 years (2011, 2014, 2017, 2021, 2024)
- **Limited Granularity**: National-level only, no regional breakdown
- **Gaps**: Some indicators have only 2-3 data points
- **Survey Timing**: Findex surveys conducted mid-year, may not capture recent changes

### Enrichment Quality
- **11 new observations**: All from reliable sources (NBE, GSMA, telecom reports)
- **8 new events**: Documented with press releases and official announcements
- **12 impact links**: Based on literature review and expert judgment
- **Confidence ratings**: Transparently assigned and justified

---

## Usage Guidelines

### Loading Data

```python
from src.data_loader import DataLoader

# Load enriched data (recommended)
loader = DataLoader("data/processed")
data = loader.load_unified_data("ethiopia_fi_enriched.csv")

# Load raw data (for comparison only)
raw_loader = DataLoader("data/raw")
raw_data = raw_loader.load_unified_data("ethiopia_fi_unified_data.csv")

# Load reference codes
ref_codes = loader.load_reference_codes()
```

### Filtering by Record Type

```python
from src.data_processor import DataProcessor

processor = DataProcessor(data, ref_codes)

# Get observations only
observations = processor.filter_by_record_type('observation')

# Get events only
events = processor.filter_by_record_type('event')

# Get impact links
impact_links = processor.filter_by_record_type('impact_link')
```

### Extracting Time Series

```python
# Get time series for specific indicator
acc_ownership = processor.get_time_series('ACC_OWNERSHIP')

# Returns DataFrame with:
# - observation_date
# - value_numeric
# - source_type
# - confidence
```

---

## Data Sources

### Primary Sources
- **Global Findex Database** (World Bank): Account ownership, digital payment usage
- **National Bank of Ethiopia (NBE)**: Regulatory data, mobile money statistics
- **GSMA Mobile Money Tracker**: Mobile money penetration data
- **Ethio Telecom / Safaricom**: Product launch announcements

### Secondary Sources
- NBE Annual Reports and Bulletins
- EthSwitch transaction statistics
- Ministry of Innovation & Technology reports
- World Bank Development Indicators

---

## Change Log

| Date       | Version | Changes                       | Task   |
| ---------- | ------- | ----------------------------- | ------ |
| 2026-01-30 | v1.0    | Initial raw dataset provided  | -      |
| 2026-01-31 | v2.0    | Data enrichment (+31 records) | Task 1 |

---

## Contact & Support

For questions about data provenance, enrichment methodology, or schema:
- See `data/processed/data_enrichment_log.md` for detailed enrichment documentation
- See `notebooks/01_task1_data_exploration_enrichment.ipynb` for analysis workflow
- See `src/README.md` for DataLoader API documentation
