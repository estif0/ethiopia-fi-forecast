# Analysis Notebooks

This directory contains Jupyter notebooks for exploratory analysis, modeling, and forecasting.

## Notebooks

### `01_task1_data_exploration_enrichment.ipynb`
**Task 1: Data Understanding & Enrichment**

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
**Task 2: Exploratory Data Analysis**

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
- `DataProcessor` - Process and analyze data (Task 2+)
- `FinancialInclusionVisualizer` - Create visualizations (Task 2+)

See `src/README.md` for detailed API documentation.
