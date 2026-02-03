# Dashboard

Interactive Streamlit dashboard for Ethiopia Financial Inclusion Forecasting.

## Features

### 📈 Overview Section
- **Key Metric Cards**: Display current account ownership, 2027 forecast, event count, and indicators monitored
- **Timeline Visualization**: Interactive timeline showing account ownership growth with key event markers
- **Recent Events Summary**: Expandable cards with details about major recent events

### 📉 Historical Trends Section  
- **Interactive Time Series**: Multi-indicator comparison with date range selector
- **Channel Comparison**: Compare different financial inclusion indicators side-by-side
- **Growth Analysis**: Automatic calculation of absolute and percentage changes

### 🔮 Forecasts Section
- **Forecast Visualizations**: Display trend forecasts with 95% confidence intervals
- **Scenario Comparison**: Compare optimistic, base, and pessimistic scenarios
- **Model Selection**: Toggle between trend-based and scenario analysis approaches
- **Forecast Tables**: Detailed numeric forecasts for all years

### 🎯 Target Progress Section
- **Progress Gauge**: Visual gauge showing progress toward 2027 targets
- **Scenario Selector**: Interactive slider to explore different scenario outcomes
- **Gap Analysis**: Calculate and display gap to target achievement
- **Scenario Comparison Chart**: Bar chart comparing all three scenarios against targets

## Running the Dashboard

### Prerequisites
```bash
# Ensure all dependencies are installed
pip install streamlit plotly pandas numpy
```

### Launch Dashboard
```bash
# From project root directory
streamlit run dashboard/app.py

# Or with custom port
streamlit run dashboard/app.py --server.port 8501
```

The dashboard will open automatically in your browser at `http://localhost:8501`.

## Dashboard Structure

```
dashboard/
├── app.py          # Main dashboard application
└── README.md       # This file
```

## Interactive Features

1. **Sidebar Navigation**: Switch between Overview, Trends, Forecasts, and Projections
2. **Multi-Indicator Selection**: Choose multiple indicators to compare in Trends section
3. **Date Range Filtering**: Select custom date ranges for analysis
4. **Forecast Method Toggle**: Compare different forecasting approaches
5. **Scenario Slider**: Explore optimistic/base/pessimistic outcomes
6. **Hover Tooltips**: Detailed information on hover for all charts
7. **Expandable Sections**: Event details and insights available on demand

## Data Requirements

The dashboard expects the following data files:
- `data/processed/ethiopia_fi_enriched.csv` - Main enriched dataset
- `models/ACC_OWNERSHIP_trend_forecast.csv` - Account ownership trend forecast
- `models/ACC_OWNERSHIP_scenarios.csv` - Account ownership scenarios
- `models/ACC_FAYDA_trend_forecast.csv` - Agent network forecast
- `models/ACC_FAYDA_scenarios.csv` - Agent network scenarios
- `models/forecast_summary_2025_2027.csv` - Forecast summary

## Dashboard Features

The application provides comprehensive analytical capabilities:
- **Overview section**: Key metric summary cards with current values and trends
- **Trends section**: Interactive time series with date range selection and channel comparisons
- **Forecasts section**: Visualizations with confidence intervals and model/scenario selection
- **Projections section**: Progress-toward-targets with scenario comparison (optimistic/base/pessimistic)
- **6 interactive visualizations**: Event timeline, trends chart, forecast plots, projections, gauge charts, and comparison panels

## Customization

To modify the dashboard:
- Edit `app.py` to add new sections or modify existing ones
- Update the CSS in the `st.markdown()` section for custom styling
- Add new forecast files and update the `load_forecasts()` function
- Modify target values in the `render_projections()` function
