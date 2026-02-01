# Ethiopia Financial Inclusion Forecasting

**Client**: Selam Analytics  
**Project Type**: Time Series Forecasting & Impact Modeling  
**Timeline**: January 30 - February 9, 2026

## Project Overview

This project develops a forecasting system to track Ethiopia's digital financial transformation. We predict key financial inclusion indicators (Account Ownership and Digital Payment Usage) for 2025-2027, incorporating the impact of major policy changes and product launches.

### Key Objectives

1. **Forecast Account Ownership Rate** (Access) for 2025-2027
2. **Forecast Digital Payment Usage** for 2025-2027
3. **Model event impacts** (policies, product launches) on financial inclusion indicators
4. **Build interactive dashboard** for stakeholder exploration of scenarios

### Target Audience

- Development finance institutions
- Mobile money operators
- National Bank of Ethiopia
- Policy makers and development partners

---

## Project Status

| Task       | Status     | Description                         |
| ---------- | ---------- | ----------------------------------- |
| **Task 1** | ✅ Complete | Data exploration & enrichment       |
| **Task 2** | ✅ Complete | Exploratory data analysis           |
| **Task 3** | 🔄 Planned  | Event impact modeling               |
| **Task 4** | 🔄 Planned  | Time series forecasting (2025-2027) |
| **Task 5** | 🔄 Planned  | Interactive Streamlit dashboard     |

**Interim Submission**: February 1, 2026 (Tasks 1 & 2 Complete)  
**Final Submission**: February 9, 2026

---

## Key Findings (Task 2 EDA)

### 1. The 2021-2024 Slowdown Paradox
**Finding**: Despite 65M+ mobile money accounts opened (including Telebirr launch in May 2021), account ownership grew by only 7.2 percentage points (28.9% → 36.1%).

**Implications**:
- Multiple accounts per person (low unique penetration)
- High inactive/dormant account rate
- Registered ≠ Active users (only 66% active rate)

### 2. Data Landscape
- **Historical Depth**: Only 5 Global Findex survey points (2011, 2014, 2017, 2021, 2024)
- **Data Quality**: >90% high confidence observations
- **Event Catalog**: 15 major events (2016-2024), concentrated in 2021-2023
- **Infrastructure**: Improving (4G coverage 70.8%, mobile penetration 61.4%)

### 3. Forecasting Implications
- **Wide confidence intervals** needed due to data sparsity
- **Event-based modeling** critical (2021-2023 policy/product launches)
- **Conservative baseline** reflecting recent slowdown
- **Focus on active usage** not just account registration

---

## Repository Structure

```
ethiopia-fi-forecast/
├── data/
│   ├── raw/                     # Original datasets (never modify)
│   │   ├── ethiopia_fi_unified_data.csv
│   │   └── reference_codes.csv
│   └── processed/               # Enriched data (Task 1 output)
│       ├── ethiopia_fi_enriched.csv
│       └── data_enrichment_log.md
│
├── src/                         # Modular Python modules
│   ├── data_loader.py          # DataLoader class
│   ├── data_enrichment.py      # DataEnricher class
│   ├── data_processor.py       # DataProcessor class (Task 2)
│   ├── visualizations.py       # FinancialInclusionVisualizer (Task 2)
│   └── README.md               # Module documentation
│
├── tests/                       # Unit tests (pytest)
│   ├── test_data_loader.py
│   ├── test_data_enrichment.py
│   ├── test_data_processor.py  # 23 tests
│   └── test_visualizations.py  # 20 tests
│
├── notebooks/                   # Analysis notebooks
│   ├── 01_task1_data_exploration_enrichment.ipynb
│   ├── 02_task2_exploratory_data_analysis.ipynb
│   └── README.md
│
├── reports/                     # Reports and visualizations
│   ├── figures/                # Generated plots (7 figures from Task 2)
│   └── README.md               # Key findings and figure descriptions
│
├── models/                      # Saved models and forecasts
├── dashboard/                   # Streamlit application (Task 5)
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- Git

### Setup Instructions

```bash
# Clone repository
git clone <repository-url>
cd ethiopia-fi-forecast

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

---

## Quick Start

### Load and Process Data

```python
from src.data_loader import DataLoader
from src.data_processor import DataProcessor
from src.visualizations import FinancialInclusionVisualizer

# Load enriched data
loader = DataLoader("data/processed")
data = loader.load_unified_data("ethiopia_fi_enriched.csv")
ref_codes = loader.load_reference_codes()

# Initialize processor and visualizer
processor = DataProcessor(data, ref_codes)
viz = FinancialInclusionVisualizer()

# Extract and visualize time series
acc_ts = processor.get_time_series('ACC_OWNERSHIP')
fig = viz.plot_indicator_trend(
    acc_ts,
    indicator_code='ACC_OWNERSHIP',
    indicator_name='Account Ownership Rate (%)'
)
```

### Run Analysis Notebooks

```bash
# Start Jupyter
jupyter notebook

# Open notebooks in order:
# 1. notebooks/01_task1_data_exploration_enrichment.ipynb
# 2. notebooks/02_task2_exploratory_data_analysis.ipynb
```

---

## Data Schema

All data uses a **unified schema** differentiated by `record_type`:

### Record Types

1. **observation** - Actual measurements
   - Fields: `indicator_code`, `value_numeric`, `observation_date`, `pillar`
   - Example: ACC_OWNERSHIP = 36.1% (2024-12-31)

2. **event** - Policy changes, product launches, milestones
   - Fields: `category`, `event_date`, `title`
   - Example: Telebirr Launch (2021-05-15)
   - **Note**: Events have NO pillar (effects captured via impact_links)

3. **impact_link** - Event-indicator relationships
   - Fields: `parent_id`, `related_indicator`, `impact_direction`, `impact_magnitude`, `lag_months`
   - Links events to their expected effects

4. **target** - Forecast targets for 2025-2027
   - Fields: `indicator_code`, `target_year`, `target_value`

### Key Indicators

**Access (Pillar)**
- `ACC_OWNERSHIP` - Account ownership rate (%)
- `ACC_MM_ACCOUNT` - Mobile money account penetration (%)
- `ACC_FI_ACCOUNT` - Formal financial institution account (%)

**Usage (Pillar)**
- `USG_DIGITAL_PAYMENT` - Digital payment usage (%)
- `USG_ACTIVE_RATE` - Active account rate (%)

**Infrastructure (Pillar)**
- `ACC_4G_COV` - 4G network coverage (%)
- `ACC_MOBILE_PEN` - Mobile penetration (%)
- `ACC_ATM_DENSITY` - ATMs per 100k adults

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_data_processor.py -v

# Run with coverage
pytest --cov=src tests/
```

**Current Test Coverage**: 66 tests, 100% passing
- DataLoader: 10 tests
- DataEnricher: 10 tests
- DataProcessor: 23 tests
- FinancialInclusionVisualizer: 20 tests

---

## Development Workflow

### Branch Strategy
- `main` - Stable releases
- `task-1` - Data exploration (merged)
- `task-2` - Exploratory data analysis (current)
- `task-3` - Event impact modeling (next)
- `task-4` - Forecasting
- `task-5` - Dashboard

### Code Standards
- **OOP Design**: Classes for all major functionality
- **Type Hints**: All function signatures
- **Docstrings**: Google-style for all classes/methods
- **Testing**: Unit tests for all modules
- **No Hardcoding**: Use config or parameters

---

## Key Visualizations

Generated in [reports/figures/](reports/figures/):

1. **acc_ownership_trend.png** - Ownership trajectory 2011-2024
2. **acc_ownership_with_events.png** - Trend with major events overlaid
3. **acc_ownership_growth.png** - Growth rate analysis
4. **mobile_money_trend.png** - Mobile money penetration
5. **data_quality_summary.png** - 4-panel quality assessment
6. **temporal_coverage.png** - Observation timeline by indicator
7. **pillar_comparison.png** - Observation counts by pillar

---

## Documentation

- **[src/README.md](src/README.md)** - Module API documentation
- **[notebooks/README.md](notebooks/README.md)** - Notebook summaries and key insights
- **[reports/README.md](reports/README.md)** - EDA findings and data limitations
- **[data/README.md](data/README.md)** - Data dictionary and sources
- **[docs/local/project-overview.md](docs/local/project-overview.md)** - Full project specification
- **[docs/local/steps.md](docs/local/steps.md)** - Incremental implementation steps

---

## Technology Stack

**Core Libraries**:
- `pandas` 2.3.3 - Data manipulation
- `numpy` 2.2.6 - Numerical computing
- `matplotlib` 3.10.8 - Static visualizations
- `seaborn` 0.13.2 - Statistical plots
- `plotly` 6.5.2 - Interactive visualizations

**Testing & Development**:
- `pytest` 9.0.2 - Testing framework
- `jupyter` 1.1.1 - Analysis notebooks

**Forecasting** (Task 4):
- `statsmodels` - Time series models
- `prophet` - Facebook's forecasting tool
- `scikit-learn` - Machine learning utilities

**Dashboard** (Task 5):
- `streamlit` - Interactive web application

---

## Data Sources

### Primary Sources
1. **Global Findex Database** (World Bank)
   - Survey years: 2011, 2014, 2017, 2021, 2024
   - Indicators: Account ownership, digital payment usage, gender gaps
   - URL: https://www.worldbank.org/en/publication/globalfindex

2. **National Bank of Ethiopia (NBE)**
   - Regulatory reports, payment system statistics
   - URL: https://nbe.gov.et/

3. **EthSwitch**
   - Interoperability platform data
   - URL: https://ethswitch.com/

4. **Shega Media / News Sources**
   - Event dates for product launches
   - URL: https://shega.co/

### Data Enrichment (Task 1)
Added 31 new records:
- 11 observations (mobile money, infrastructure, usage)
- 8 events (Telebirr, M-Pesa, policies)
- 12 impact links (event-indicator relationships)

All additions documented in [data/processed/data_enrichment_log.md](data/processed/data_enrichment_log.md)

---

## Contact & Attribution

**Project**: Ethiopia Financial Inclusion Forecasting  
**Organization**: Selam Analytics  
**Period**: January 30 - February 9, 2026

---

## License

This project is proprietary and developed for Selam Analytics.

---

## Next Steps

### Task 3: Event Impact Modeling (Feb 2-3)
- Build `ImpactModel` class
- Quantify event effects on indicators
- Validate against 2021-2024 data

### Task 4: Forecasting (Feb 4-6)
- Create `Forecaster` class
- Generate 2025-2027 projections
- Three scenarios: base, optimistic, pessimistic

### Task 5: Dashboard (Feb 7-8)
- Interactive Streamlit application
- Scenario comparison
- Downloadable forecasts
- Event impact explorer
