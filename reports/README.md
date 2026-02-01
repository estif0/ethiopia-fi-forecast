# Reports and Figures

This directory contains analysis reports, visualizations, and documentation.

## Directory Structure

```
reports/
├── figures/          # Generated visualizations
└── README.md         # This file
```

## Generated Figures

### Task 2: Exploratory Data Analysis

#### Dataset Overview
- **`pillar_comparison.png`** - Observation counts by pillar (Access, Usage, Infrastructure)
- **`data_quality_summary.png`** - 4-panel quality assessment (confidence, completeness, source types, temporal coverage)
- **`temporal_coverage.png`** - Timeline showing observation span by indicator

#### Financial Access Analysis
- **`acc_ownership_trend.png`** - Account ownership trajectory (2011-2024)
- **`acc_ownership_growth.png`** - Growth rates over time (percentage change)
- **`acc_ownership_with_events.png`** - Ownership trend with major events overlaid

#### Usage Analysis
- **`mobile_money_trend.png`** - Mobile money account penetration over time

---

## Key Findings from Task 2 EDA

### Account Ownership Trends
- **2011-2024 Growth**: 14.3% → 36.1% (+21.8 percentage points)
- **2021-2024 Period**: 28.9% → 36.1% (+7.2pp only)
- **Historical Average Growth**: ~59% per period
- **Recent Growth**: Only 36% (2021-2024)

### The 2021-2024 Slowdown Paradox
Despite 65M+ mobile money accounts opened (including Telebirr launch in May 2021), account ownership grew by only 3 percentage points. This suggests:
- **Multiple accounts per person**: Low unique penetration
- **High inactive rate**: Many registered but dormant accounts
- **Measurement issues**: Survey timing and methodology considerations

### Data Quality Assessment
- **High Confidence**: >90% of observations rated high confidence
- **Primary Source**: Global Findex surveys (5 points: 2011, 2014, 2017, 2021, 2024)
- **Data Sparsity**: Average ~3 observations per indicator
- **Coverage**: 13-year span but limited temporal resolution

### Event Landscape
- **Total Events**: 15 cataloged events
- **Categories**: 
  - Product launches: 6 (Telebirr, M-Pesa, EthSwitch services)
  - Policy changes: 4 (NBE regulations, financial inclusion strategy)
  - Infrastructure: 3 (network expansion, agent growth)
  - Milestones: 2 (market achievements)
- **Event-Rich Period**: 2021-2023 concentration

### Usage Patterns
- **Mobile Money Penetration**: 4.70% (2021) → 9.45% (2024)
- **Active Account Rate**: 66% as of 2024
- **Digital Payment Data**: Limited observations, requires more comprehensive tracking

### Infrastructure Development
- **4G Coverage**: Expanding (latest: 70.8%)
- **Mobile Penetration**: Growing (latest: 61.4%)
- **ATM Density**: Limited data available

---

## Data Limitations for Forecasting

### High Impact Limitations
1. **Temporal Sparsity**: Only 5 Findex survey points over 13 years
   - Limits trend identification
   - Increases forecast uncertainty
   - Requires wide confidence intervals

### Medium Impact Limitations
2. **Survey Dependency**: Primary data from 3-year survey cycles
   - Potential survey biases
   - Long gaps between measurements
   - Mitigation: Supplement with administrative data where available

3. **Event Attribution**: Limited impact_link records
   - Difficult to isolate event effects
   - Causality challenging to establish
   - Mitigation: Use synthetic control methods, expert judgment

### Low Impact Limitations
4. **Disaggregation Gaps**: Limited demographic breakdowns
   - Restricts sub-group analysis (gender, urban-rural, age)
   - Mitigation: Document in forecast assumptions

5. **Recency**: 2024 data is latest
   - No real-time tracking
   - Acceptable for 2025-2027 forecasting
   - Mitigation: Use 2024 as baseline

---

## Implications for Next Steps

### Task 3: Event Impact Modeling
- Focus on 2021-2024 events (Telebirr, M-Pesa, policy changes)
- Model lag effects and impact magnitude
- Validate against historical slowdown

### Task 4: Forecasting (2025-2027)
- **Base case**: Conservative growth reflecting recent slowdown
- **Optimistic case**: Assume infrastructure enables usage growth
- **Pessimistic case**: Continued stagnation despite account growth
- **Wide confidence intervals**: Given data sparsity (±5-10pp reasonable)

### Task 5: Dashboard
- Visualize scenarios interactively
- Show uncertainty ranges prominently
- Document data limitations transparently
- Provide event timeline context

---

## Figure Generation

All figures generated using:
- `matplotlib` (static publication-ready plots)
- `seaborn` (statistical visualizations)
- `plotly` (interactive dashboards)

Resolution: 300 DPI, bbox_inches='tight' for publication quality.

Color scheme follows pillar conventions:
- **Access**: Blue (#2E86AB)
- **Usage**: Purple (#A23B72)
- **Infrastructure**: Orange (#F18F01)

Event colors:
- **product_launch**: Green
- **policy**: Blue
- **infrastructure**: Orange
- **milestone**: Red
