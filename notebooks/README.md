# Analysis Notebooks

This directory contains Jupyter notebooks for exploratory analysis, modeling, and forecasting.

## Notebooks

### `01_task1_data_exploration_enrichment.ipynb`
**Task 1: Data Understanding & Enrichment** ✅ Complete

- **Part 1**: Dataset exploration
  - Unified schema structure (record_type, pillar, indicator_code)
  - Temporal coverage analysis (2011-2024)
  - Data quality assessment
  - Identification of gaps

- **Part 2**: Data enrichment
  - Added 11 new observations (mobile money, infrastructure, usage metrics)
  - Added 8 events (product launches, policy changes, milestones)
  - Added 12 impact links connecting events to indicators
  - All additions documented with sources and confidence levels

**Output**: `data/processed/ethiopia_fi_enriched.csv` with enrichment log

---

### `02_task2_exploratory_data_analysis.ipynb`
**Task 2: Exploratory Data Analysis** ✅ Complete

- **Part 1**: Dataset Overview
  - Record type distribution (observations, events, impact links, targets)
  - Pillar and source type analysis
  - Data quality assessment (confidence distribution, completeness)
  - Temporal coverage visualization

- **Part 2**: Financial Access Analysis
  - Account ownership trajectory (2011-2024): 28.9% → 36.1%
  - Growth rate calculations and visualization
  - **Key Finding**: 2021-2024 slowdown paradox (only +7.2pp despite 65M+ mobile money accounts)

- **Part 3**: Usage Analysis
  - Mobile money penetration trends (4.70% → 9.45%)
  - Digital payment adoption patterns
  - Active vs registered account gap (66% active rate)

- **Part 4**: Infrastructure & Events
  - 15 events cataloged across categories (policy, product_launch, infrastructure, milestone)
  - Events overlaid on indicator trends
  - Infrastructure indicators (4G coverage, mobile penetration, ATM density)

- **Part 5**: Key Insights & Limitations
  - 5 documented insights with supporting evidence
  - Comprehensive data limitations assessment
  - Implications for forecasting

**Key Insights:**
1. **Slowdown Paradox**: Despite massive mobile money growth (65M+ accounts), ownership increased only 3pp (2021-2024)
2. **Data Sparsity**: Only 5 Findex points over 13 years requires wide confidence intervals
3. **High Quality**: >90% observations have high confidence from Global Findex
4. **Event-Rich Period**: 2021-2023 saw major policy/product launches requiring event-based modeling
5. **Infrastructure Growth**: Enabling environment improving with 4G and mobile expansion

**Output**: 7 visualizations in `reports/figures/`

---

### `03_task3_impact_modeling.ipynb`
**Task 3: Event Impact Modeling** ✅ Complete

- **Part 1**: Impact Model Development
  - Event-indicator association matrix creation
  - Impact link analysis (direction, magnitude, lag effects)
  - Functional form definition for impact estimation

- **Part 2**: Historical Validation
  - Telebirr launch effect validation (2021-2024)
  - Mobile money growth validation
  - Residual analysis and model performance assessment

- **Part 3**: Methodology Documentation
  - Clear assumptions and limitations
  - Functional forms for impact estimation
  - Source references and confidence assessments
  - Lag effect modeling (0-12 months)

**Key Findings:**
- Telebirr had strong positive impact on mobile money accounts (+0.8 magnitude)
- Policy changes showed delayed effects (3-6 month lags)
- Infrastructure events had broad, sustained impacts

**Output**: 
- `models/event_indicator_matrix.csv` - Association matrix
- `models/impact_validation_results.csv` - Validation metrics
- 2 visualizations in `reports/figures/`

---

### `04_task4_forecasting.ipynb`
**Task 4: Time Series Forecasting** ✅ Complete

- **Part 1**: Trend Model Development
  - Linear trend fitting for ACC_OWNERSHIP (R²=0.89, RMSE=4.37pp)
  - Model selection and validation
  - Historical fit assessment (2011-2024)

- **Part 2**: Forecast Generation
  - 2025-2027 predictions with 95% confidence intervals
  - Uncertainty quantification using t-distribution
  - ACC_OWNERSHIP and ACC_FAYDA forecasts

- **Part 3**: Scenario Analysis
  - Optimistic scenario (1.3x growth multiplier)
  - Base scenario (historical trend continuation)
  - Pessimistic scenario (0.7x growth multiplier)

- **Part 4**: Written Interpretation
  - Base forecast: ACC_OWNERSHIP reaches 47.8% by 2027
  - Wide confidence intervals: [34.5%, 61.1%] reflecting data sparsity
  - Key uncertainties: Policy changes, technology adoption, economic factors
  - Highest-impact events: Mobile money expansion, digital payment policies

**Key Results:**
- **ACC_OWNERSHIP 2027**: 47.8% (base), [34.5%, 61.1%] 95% CI
- **ACC_FAYDA 2027**: 11.2% (base), [7.8%, 14.6%] 95% CI
- Scenarios show 20-30% variation around base case

**Output**: 
- 5 forecast CSV files in `models/`
- 3 forecast visualizations in `reports/figures/`

---

## Usage

### Running Notebooks

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Start Jupyter
jupyter notebook
```

### Notebook Conventions

- **Import from src/**: Always use modules from `src/` directory
- **Document insights**: Use markdown cells for interpretations
- **Clear sections**: Use headers to organize content
- **Save visualizations**: Export key figures to `reports/figures/`
- **Version control**: Include output for documentation, but can be cleared before commit if large

### Dependencies

All notebooks use:
- `DataLoader` - Load datasets
- `DataEnricher` - Add new records (Task 1)
- `DataProcessor` - Process and analyze data (Tasks 2-4)
- `FinancialInclusionVisualizer` - Create visualizations (Tasks 2-4)
- `ImpactModel` - Model event impacts (Task 3)
- `ImpactValidator` - Validate impact model (Task 3)
- `FinancialInclusionForecaster` - Generate forecasts (Task 4)

See `src/README.md` for detailed API documentation.

---

## Notebook Summary

All analysis notebooks completed and fully executed:

| Task       | Notebook                                   | Focus Area                      | Key Outputs                        |
| ---------- | ------------------------------------------ | ------------------------------- | ---------------------------------- |
| **Task 1** | 01_task1_data_exploration_enrichment.ipynb | Data understanding & enrichment | Enriched dataset (60 records)      |
| **Task 2** | 02_task2_exploratory_data_analysis.ipynb   | Comprehensive EDA               | 5+ insights, 7 visualizations      |
| **Task 3** | 03_task3_impact_modeling.ipynb             | Event impact quantification     | Event-indicator matrix, validation |
| **Task 4** | 04_task4_forecasting.ipynb                 | Time series forecasting         | 2025-2027 forecasts, scenarios     |
| **Task 5** | N/A (Dashboard)                            | Interactive visualization       | Streamlit web application          |

For detailed analysis methodology and results, see [reports/final_report.md](../reports/final_report.md)
