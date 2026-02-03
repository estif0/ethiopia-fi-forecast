"""
Ethiopia Financial Inclusion Dashboard

Interactive dashboard for exploring financial inclusion data, forecasts, and scenarios.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import DataLoader

# Page configuration
st.set_page_config(
    page_title="Ethiopia Financial Inclusion Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .stMetric {
        background-color: #373737;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1f77b4;
    }
    h2 {
        color: #2c3e50;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    """Load all required data."""
    loader = DataLoader(data_dir="data/processed")
    df = loader.load_unified_data("ethiopia_fi_enriched.csv")
    observations = loader.get_records_by_type("observation")
    events = loader.get_records_by_type("event")
    targets = loader.get_records_by_type("target")
    return df, observations, events, targets


@st.cache_data
def load_forecasts():
    """Load forecast data."""
    forecasts = {}
    forecast_files = {
        "ACC_OWNERSHIP_trend": "models/ACC_OWNERSHIP_trend_forecast.csv",
        "ACC_OWNERSHIP_scenarios": "models/ACC_OWNERSHIP_scenarios.csv",
        "ACC_FAYDA_trend": "models/ACC_FAYDA_trend_forecast.csv",
        "ACC_FAYDA_scenarios": "models/ACC_FAYDA_scenarios.csv",
        "summary": "models/forecast_summary_2025_2027.csv",
    }

    for key, filepath in forecast_files.items():
        try:
            forecasts[key] = pd.read_csv(filepath)
        except FileNotFoundError:
            st.warning(f"Forecast file not found: {filepath}")
            forecasts[key] = pd.DataFrame()

    return forecasts


def main():
    """Main dashboard application."""

    # Title and description
    st.title("📊 Ethiopia Financial Inclusion Dashboard")
    st.markdown(
        """
    Explore Ethiopia's financial inclusion journey from 2011-2024 and forecasts through 2027.
    This dashboard provides interactive visualizations of account ownership, usage patterns, 
    and the impact of key events on financial inclusion indicators.
    """
    )

    # Load data
    with st.spinner("Loading data..."):
        df, observations, events, targets = load_data()
        forecasts = load_forecasts()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Section",
        ["📈 Overview", "📉 Historical Trends", "🔮 Forecasts", "🎯 Target Progress"],
    )

    # Render selected page
    if page == "📈 Overview":
        render_overview(observations, events, targets, forecasts)
    elif page == "📉 Historical Trends":
        render_trends(observations, events)
    elif page == "🔮 Forecasts":
        render_forecasts(observations, forecasts)
    elif page == "🎯 Target Progress":
        render_projections(observations, targets, forecasts)

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
    **Data Sources:**
    - Global Findex Database
    - National Bank of Ethiopia
    - EthSwitch
    
    **Project:** Selam Analytics Financial Inclusion Forecasting
    """
    )


def render_overview(observations, events, targets, forecasts):
    """Render overview section with key metrics."""
    st.header("Overview: Key Metrics")

    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    # Latest account ownership
    acc_data = observations[
        observations["indicator_code"] == "ACC_OWNERSHIP"
    ].sort_values("observation_date")
    if len(acc_data) > 0:
        latest_acc = acc_data.iloc[-1]
        prev_acc = acc_data.iloc[-2] if len(acc_data) > 1 else None

        with col1:
            delta = (
                latest_acc["value_numeric"] - prev_acc["value_numeric"]
                if prev_acc is not None
                else 0
            )
            st.metric(
                "Account Ownership",
                f"{latest_acc['value_numeric']:.1f}%",
                f"{delta:+.1f}pp since {prev_acc['observation_date'].year if prev_acc is not None else 'prior'}",
                help="Percentage of adults with a financial account",
            )

    # 2027 Forecast
    if not forecasts["ACC_OWNERSHIP_scenarios"].empty:
        forecast_2027 = forecasts["ACC_OWNERSHIP_scenarios"][
            (forecasts["ACC_OWNERSHIP_scenarios"]["year"] == 2027)
            & (forecasts["ACC_OWNERSHIP_scenarios"]["scenario"] == "base")
        ]
        if len(forecast_2027) > 0:
            with col2:
                st.metric(
                    "2027 Forecast (Base)",
                    f"{forecast_2027.iloc[0]['forecast']:.1f}%",
                    "Account Ownership",
                    help="Base scenario forecast for 2027",
                )

    # Number of events
    with col3:
        st.metric(
            "Key Events Tracked",
            f"{len(events)}",
            "2011-2024",
            help="Major policy changes, product launches, and milestones",
        )

    # Data coverage
    indicators = observations["indicator_code"].nunique()
    with col4:
        st.metric(
            "Indicators Monitored",
            f"{indicators}",
            "Access, Usage, Infrastructure",
            help="Financial inclusion indicators tracked",
        )

    st.markdown("---")

    # Timeline overview
    st.subheader("Financial Inclusion Timeline (2011-2024)")

    # Create timeline chart
    acc_timeline = observations[
        observations["indicator_code"] == "ACC_OWNERSHIP"
    ].copy()
    acc_timeline["observation_date"] = pd.to_datetime(acc_timeline["observation_date"])
    acc_timeline = acc_timeline.sort_values("observation_date")

    fig = go.Figure()

    # Add historical line
    fig.add_trace(
        go.Scatter(
            x=acc_timeline["observation_date"],
            y=acc_timeline["value_numeric"],
            mode="lines+markers",
            name="Account Ownership",
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=10),
        )
    )

    # Add event markers as shapes (more compatible with datetime)
    events_df = events.copy()
    events_df["event_date"] = pd.to_datetime(events_df["event_date"])

    shapes = []
    annotations = []
    for idx, event in events_df.iterrows():
        # Skip events with invalid dates
        if pd.isna(event["event_date"]):
            continue

        # Add vertical line shape
        shapes.append(
            dict(
                type="line",
                x0=event["event_date"],
                x1=event["event_date"],
                y0=0,
                y1=1,
                yref="paper",
                line=dict(color="gray", width=1, dash="dash"),
                opacity=0.5,
            )
        )

        # Add annotation
        event_title = (
            str(event["title"])[:20] + "..."
            if isinstance(event["title"], str) and len(event["title"]) > 20
            else str(event["title"]) if pd.notna(event["title"]) else "Event"
        )
        annotations.append(
            dict(
                x=event["event_date"],
                y=1,
                yref="paper",
                text=event_title,
                showarrow=False,
                textangle=-90,
                xanchor="left",
                yanchor="bottom",
                font=dict(size=8, color="gray"),
            )
        )

    fig.update_layout(
        title="Account Ownership Growth with Key Events",
        xaxis_title="Year",
        yaxis_title="Account Ownership (%)",
        hovermode="x unified",
        height=400,
        shapes=shapes,
        annotations=annotations,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Recent events summary
    st.subheader("Recent Major Events")
    recent_events = events.sort_values("event_date", ascending=False).head(5)

    for idx, event in recent_events.iterrows():
        event_date = pd.to_datetime(event["event_date"]).strftime("%B %Y")
        with st.expander(f"📅 {event_date}: {event['title']}"):
            st.write(f"**Category:** {event['category']}")
            st.write(event["description"])


def render_trends(observations, events):
    """Render historical trends section with interactive charts."""
    st.header("Historical Trends Analysis")

    # Interactive controls
    col1, col2 = st.columns([2, 1])

    with col1:
        # Indicator selector
        available_indicators = sorted(observations["indicator_code"].unique())
        selected_indicators = st.multiselect(
            "Select Indicators to Display",
            available_indicators,
            default=(
                ["ACC_OWNERSHIP"]
                if "ACC_OWNERSHIP" in available_indicators
                else available_indicators[:1]
            ),
            help="Choose one or more indicators to compare",
        )

    with col2:
        # Date range selector
        observations["observation_date"] = pd.to_datetime(
            observations["observation_date"]
        )
        min_date = observations["observation_date"].min()
        max_date = observations["observation_date"].max()

        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            help="Select time period to analyze",
        )

    if selected_indicators:
        # Filter data
        filtered_obs = observations[
            (observations["indicator_code"].isin(selected_indicators))
            & (observations["observation_date"] >= pd.to_datetime(date_range[0]))
            & (observations["observation_date"] <= pd.to_datetime(date_range[1]))
        ].copy()

        # Create interactive time series plot
        fig = go.Figure()

        for indicator in selected_indicators:
            indicator_data = filtered_obs[
                filtered_obs["indicator_code"] == indicator
            ].sort_values("observation_date")

            fig.add_trace(
                go.Scatter(
                    x=indicator_data["observation_date"],
                    y=indicator_data["value_numeric"],
                    mode="lines+markers",
                    name=indicator,
                    line=dict(width=2),
                    marker=dict(size=8),
                    hovertemplate="<b>%{fullData.name}</b><br>Date: %{x}<br>Value: %{y:.2f}%<extra></extra>",
                )
            )

        # Add event markers as shapes if in date range
        events_df = events.copy()
        events_df["event_date"] = pd.to_datetime(events_df["event_date"])
        events_in_range = events_df[
            (events_df["event_date"] >= pd.to_datetime(date_range[0]))
            & (events_df["event_date"] <= pd.to_datetime(date_range[1]))
        ]

        shapes = []
        annotations = []
        for idx, event in events_in_range.iterrows():
            # Skip events with invalid dates
            if pd.isna(event["event_date"]):
                continue

            event_title = str(event["title"]) if pd.notna(event["title"]) else "Event"
            event_title = (
                event_title[:15] + "..." if len(event_title) > 15 else event_title
            )

            shapes.append(
                dict(
                    type="line",
                    x0=event["event_date"],
                    x1=event["event_date"],
                    y0=0,
                    y1=1,
                    yref="paper",
                    line=dict(color="rgba(128,128,128,0.5)", width=1, dash="dash"),
                )
            )
            annotations.append(
                dict(
                    x=event["event_date"],
                    y=1,
                    yref="paper",
                    text=event_title,
                    showarrow=False,
                    textangle=-90,
                    xanchor="left",
                    yanchor="bottom",
                    font=dict(size=8, color="gray"),
                )
            )

        fig.update_layout(
            title="Financial Inclusion Indicators Over Time",
            xaxis_title="Date",
            yaxis_title="Value (%)",
            hovermode="x unified",
            height=500,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            shapes=shapes,
            annotations=annotations,
        )

        st.plotly_chart(fig, use_container_width=True)

        # Growth rates analysis
        st.subheader("Growth Analysis")

        growth_data = []
        for indicator in selected_indicators:
            indicator_data = filtered_obs[
                filtered_obs["indicator_code"] == indicator
            ].sort_values("observation_date")
            if len(indicator_data) >= 2:
                first_val = indicator_data.iloc[0]["value_numeric"]
                last_val = indicator_data.iloc[-1]["value_numeric"]
                absolute_change = last_val - first_val
                pct_change = (absolute_change / first_val * 100) if first_val > 0 else 0

                growth_data.append(
                    {
                        "Indicator": indicator,
                        "Start Value": f"{first_val:.2f}%",
                        "End Value": f"{last_val:.2f}%",
                        "Absolute Change": f"{absolute_change:+.2f}pp",
                        "Percentage Change": f"{pct_change:+.1f}%",
                    }
                )

        if growth_data:
            st.dataframe(pd.DataFrame(growth_data), use_container_width=True)

    else:
        st.info("Please select at least one indicator to display.")


def render_forecasts(observations, forecasts):
    """Render forecasts section with confidence intervals and scenarios."""
    st.header("Financial Inclusion Forecasts (2025-2027)")

    # Forecast selector
    forecast_indicator = st.selectbox(
        "Select Indicator to Forecast",
        ["Account Ownership (ACC_OWNERSHIP)", "Agent Network Coverage (ACC_FAYDA)"],
        help="Choose which indicator forecast to display",
    )

    indicator_code = (
        "ACC_OWNERSHIP" if "Ownership" in forecast_indicator else "ACC_FAYDA"
    )

    # Forecast approach selector
    st.subheader("Forecast Approach")
    approach = st.radio(
        "Select Forecasting Method",
        ["Trend Forecast with Confidence Intervals", "Scenario Analysis"],
        horizontal=True,
        help="Compare different forecasting approaches",
    )

    # Get historical data
    hist_data = observations[observations["indicator_code"] == indicator_code].copy()
    hist_data["observation_date"] = pd.to_datetime(hist_data["observation_date"])
    hist_data = hist_data.sort_values("observation_date")

    fig = go.Figure()

    # Add historical data
    fig.add_trace(
        go.Scatter(
            x=hist_data["observation_date"],
            y=hist_data["value_numeric"],
            mode="lines+markers",
            name="Historical",
            line=dict(color="black", width=3),
            marker=dict(size=10),
        )
    )

    if approach == "Trend Forecast with Confidence Intervals":
        # Load trend forecast
        trend_key = f"{indicator_code}_trend"
        if not forecasts[trend_key].empty:
            trend_forecast = forecasts[trend_key].copy()
            trend_forecast["date"] = pd.to_datetime(
                trend_forecast["year"].astype(str) + "-01-01"
            )

            # Add forecast line
            fig.add_trace(
                go.Scatter(
                    x=trend_forecast["date"],
                    y=trend_forecast["forecast"],
                    mode="lines+markers",
                    name="Trend Forecast",
                    line=dict(color="#1f77b4", width=2, dash="dash"),
                    marker=dict(size=8),
                )
            )

            # Add confidence interval
            fig.add_trace(
                go.Scatter(
                    x=trend_forecast["date"].tolist()
                    + trend_forecast["date"].tolist()[::-1],
                    y=trend_forecast["upper_bound"].tolist()
                    + trend_forecast["lower_bound"].tolist()[::-1],
                    fill="toself",
                    fillcolor="rgba(31, 119, 180, 0.2)",
                    line=dict(color="rgba(255,255,255,0)"),
                    name="95% Confidence Interval",
                    showlegend=True,
                    hoverinfo="skip",
                )
            )

            # Add boundary lines
            fig.add_trace(
                go.Scatter(
                    x=trend_forecast["date"],
                    y=trend_forecast["upper_bound"],
                    mode="lines",
                    name="Upper Bound",
                    line=dict(color="#1f77b4", width=1, dash="dot"),
                    showlegend=False,
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=trend_forecast["date"],
                    y=trend_forecast["lower_bound"],
                    mode="lines",
                    name="Lower Bound",
                    line=dict(color="#1f77b4", width=1, dash="dot"),
                    showlegend=False,
                )
            )

    else:  # Scenario Analysis
        scenarios_key = f"{indicator_code}_scenarios"
        if not forecasts[scenarios_key].empty:
            scenarios = forecasts[scenarios_key].copy()
            scenarios["date"] = pd.to_datetime(scenarios["year"].astype(str) + "-01-01")

            scenario_colors = {
                "optimistic": "#06A77D",
                "base": "#1f77b4",
                "pessimistic": "#D62246",
            }

            for scenario in ["optimistic", "base", "pessimistic"]:
                scenario_data = scenarios[scenarios["scenario"] == scenario]

                fig.add_trace(
                    go.Scatter(
                        x=scenario_data["date"],
                        y=scenario_data["forecast"],
                        mode="lines+markers",
                        name=f"{scenario.capitalize()} Scenario",
                        line=dict(color=scenario_colors[scenario], width=2, dash="dot"),
                        marker=dict(size=6),
                    )
                )

    # Add forecast line marker as shape
    shapes = []
    annotations = []
    if not hist_data.empty:
        last_hist_date = hist_data["observation_date"].max()
        shapes.append(
            dict(
                type="line",
                x0=last_hist_date,
                x1=last_hist_date,
                y0=0,
                y1=1,
                yref="paper",
                line=dict(color="gray", width=1, dash="dash"),
            )
        )
        annotations.append(
            dict(
                x=last_hist_date,
                y=0.95,
                yref="paper",
                text="Forecast →",
                showarrow=False,
                xanchor="left",
                font=dict(size=10, color="gray"),
            )
        )

    fig.update_layout(
        title=f"{forecast_indicator} Forecast",
        xaxis_title="Year",
        yaxis_title="Value (%)",
        hovermode="x unified",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        shapes=shapes,
        annotations=annotations,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Forecast table
    st.subheader("Forecast Values")

    if approach == "Trend Forecast with Confidence Intervals":
        trend_key = f"{indicator_code}_trend"
        if not forecasts[trend_key].empty:
            display_df = forecasts[trend_key][
                ["year", "forecast", "lower_bound", "upper_bound"]
            ].copy()
            display_df.columns = [
                "Year",
                "Forecast",
                "Lower Bound (95% CI)",
                "Upper Bound (95% CI)",
            ]
            display_df["Forecast"] = display_df["Forecast"].apply(lambda x: f"{x:.2f}%")
            display_df["Lower Bound (95% CI)"] = display_df[
                "Lower Bound (95% CI)"
            ].apply(lambda x: f"{x:.2f}%")
            display_df["Upper Bound (95% CI)"] = display_df[
                "Upper Bound (95% CI)"
            ].apply(lambda x: f"{x:.2f}%")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        scenarios_key = f"{indicator_code}_scenarios"
        if not forecasts[scenarios_key].empty:
            pivot_df = forecasts[scenarios_key].pivot_table(
                index="year", columns="scenario", values="forecast"
            )[["pessimistic", "base", "optimistic"]]
            pivot_df.columns = ["Pessimistic", "Base", "Optimistic"]
            pivot_df = pivot_df.applymap(lambda x: f"{x:.2f}%")
            pivot_df.index.name = "Year"
            st.dataframe(pivot_df, use_container_width=True)


def render_projections(observations, targets, forecasts):
    """Render target progress and projections."""
    st.header("Progress Toward National Targets")

    st.markdown(
        """
    Track Ethiopia's progress toward financial inclusion targets and explore different scenario outcomes.
    """
    )

    # Scenario selector for projections
    scenario = st.select_slider(
        "Select Scenario for 2027 Projections",
        options=["pessimistic", "base", "optimistic"],
        value="base",
        help="See how different scenarios affect target achievement",
    )

    # Account ownership progress
    st.subheader("Account Ownership Target Progress")

    # Get current value
    acc_data = observations[
        observations["indicator_code"] == "ACC_OWNERSHIP"
    ].sort_values("observation_date")
    current_value = acc_data.iloc[-1]["value_numeric"] if len(acc_data) > 0 else 0

    # Get 2027 forecast based on scenario
    if not forecasts["ACC_OWNERSHIP_scenarios"].empty:
        forecast_2027 = forecasts["ACC_OWNERSHIP_scenarios"][
            (forecasts["ACC_OWNERSHIP_scenarios"]["year"] == 2027)
            & (forecasts["ACC_OWNERSHIP_scenarios"]["scenario"] == scenario)
        ]
        forecast_value = (
            forecast_2027.iloc[0]["forecast"]
            if len(forecast_2027) > 0
            else current_value
        )
    else:
        forecast_value = current_value

    # Assumed target (based on regional benchmarks)
    target_value = 70.0  # Example target

    # Create gauge chart
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=forecast_value,
            domain={"x": [0, 1], "y": [0, 1]},
            title={
                "text": f"2027 {scenario.capitalize()} Scenario Forecast",
                "font": {"size": 20},
            },
            delta={"reference": current_value, "suffix": "pp", "valueformat": ".1f"},
            number={"suffix": "%", "valueformat": ".1f"},
            gauge={
                "axis": {"range": [None, 100], "tickwidth": 1, "tickcolor": "darkblue"},
                "bar": {"color": "#1f77b4"},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "gray",
                "steps": [
                    {"range": [0, current_value], "color": "#e8f4f8"},
                    {"range": [current_value, target_value], "color": "#d0e8f0"},
                    {"range": [target_value, 100], "color": "#b8dce8"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": target_value,
                },
            },
        )
    )

    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

    # Progress metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Current (2024)", f"{current_value:.1f}%")

    with col2:
        st.metric(f"{scenario.capitalize()} (2027)", f"{forecast_value:.1f}%")

    with col3:
        st.metric("Target (2027)", f"{target_value:.1f}%")

    with col4:
        gap = target_value - forecast_value
        st.metric("Gap to Target", f"{gap:.1f}pp", delta_color="inverse")

    st.markdown("---")

    # Scenario comparison chart
    st.subheader("Scenario Comparison: All Forecasts")

    if not forecasts["ACC_OWNERSHIP_scenarios"].empty:
        scenarios_df = forecasts["ACC_OWNERSHIP_scenarios"].copy()

        fig = go.Figure()

        scenario_colors = {
            "optimistic": "#06A77D",
            "base": "#1f77b4",
            "pessimistic": "#D62246",
        }

        for scen in ["optimistic", "base", "pessimistic"]:
            scen_data = scenarios_df[scenarios_df["scenario"] == scen]

            fig.add_trace(
                go.Bar(
                    name=scen.capitalize(),
                    x=scen_data["year"],
                    y=scen_data["forecast"],
                    marker_color=scenario_colors[scen],
                    text=scen_data["forecast"].apply(lambda x: f"{x:.1f}%"),
                    textposition="outside",
                )
            )

        # Add target line
        fig.add_hline(
            y=target_value,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Target: {target_value}%",
            annotation_position="right",
        )

        fig.update_layout(
            title="Account Ownership Scenarios vs Target",
            xaxis_title="Year",
            yaxis_title="Account Ownership (%)",
            barmode="group",
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

    # Key insights
    with st.expander("📊 Key Insights"):
        st.markdown(
            f"""
        **Current Status (2024):** {current_value:.1f}%
        
        **2027 Projections:**
        - **Pessimistic:** {scenarios_df[scenarios_df['scenario']=='pessimistic']['forecast'].iloc[-1]:.1f}%
        - **Base:** {scenarios_df[scenarios_df['scenario']=='base']['forecast'].iloc[-1]:.1f}%
        - **Optimistic:** {scenarios_df[scenarios_df['scenario']=='optimistic']['forecast'].iloc[-1]:.1f}%
        
        **Target Achievement:**
        - Only the optimistic scenario approaches the 70% target by 2027
        - Base scenario shows steady progress but falls short of target
        - Accelerated interventions needed to reach ambitious goals
        
        **Key Drivers:**
        - Policy implementation success
        - Fintech competition and innovation
        - Infrastructure development (agent networks)
        - Economic stability
        """
        )


if __name__ == "__main__":
    main()
