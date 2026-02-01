"""
Visualization Module for Ethiopia Financial Inclusion Forecasting

This module provides visualization classes for creating consistent,
publication-ready charts for the financial inclusion dataset.

Classes:
    FinancialInclusionVisualizer: Creates various plots and visualizations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Optional, Dict, Tuple
from pathlib import Path


class FinancialInclusionVisualizer:
    """
    Create visualizations for Ethiopia financial inclusion data.

    This class provides methods to create temporal coverage charts,
    indicator trends, event timelines, correlation heatmaps, and growth analysis.

    Attributes:
        style (str): Seaborn style to use for matplotlib plots.
        color_palette (str): Color palette name.
        figsize (Tuple[int, int]): Default figure size for plots.
    """

    # Color scheme for different pillars
    PILLAR_COLORS = {
        "access": "#2E86AB",  # Blue
        "usage": "#A23B72",  # Purple
        "infrastructure": "#F18F01",  # Orange
        "quality": "#C73E1D",  # Red
        "other": "#6C757D",  # Gray
    }

    # Event category colors
    EVENT_COLORS = {
        "product_launch": "#28A745",  # Green
        "policy": "#007BFF",  # Blue
        "infrastructure": "#FD7E14",  # Orange
        "market_entry": "#6F42C1",  # Purple
        "milestone": "#20C997",  # Teal
        "partnership": "#E83E8C",  # Pink
        "regulation": "#6C757D",  # Gray
        "economic": "#FFC107",  # Yellow
        "pricing": "#17A2B8",  # Cyan
    }

    def __init__(
        self,
        style: str = "whitegrid",
        color_palette: str = "husl",
        figsize: Tuple[int, int] = (12, 6),
    ):
        """
        Initialize the visualizer with style settings.

        Args:
            style: Seaborn style ('whitegrid', 'darkgrid', 'white', 'dark', 'ticks').
            color_palette: Seaborn color palette name.
            figsize: Default figure size (width, height) in inches.
        """
        self.style = style
        self.color_palette = color_palette
        self.figsize = figsize

        # Set seaborn style
        sns.set_style(style)
        sns.set_palette(color_palette)

    def plot_timeline(
        self,
        coverage_df: pd.DataFrame,
        save_path: Optional[Path] = None,
        title: str = "Temporal Coverage of Financial Inclusion Indicators",
    ) -> plt.Figure:
        """
        Create a timeline visualization showing temporal coverage by indicator.

        Args:
            coverage_df: DataFrame with columns: indicator_code, earliest_date,
                        latest_date, observation_count.
            save_path: Optional path to save the figure.
            title: Plot title.

        Returns:
            Matplotlib Figure object.
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # Sort by earliest date
        coverage_df = coverage_df.sort_values("earliest_date")

        # Create horizontal bars
        for idx, row in coverage_df.iterrows():
            start = row["earliest_date"]
            end = row["latest_date"]
            indicator = row["indicator_code"]
            count = row["observation_count"]

            # Draw line
            ax.plot([start, end], [idx, idx], "o-", linewidth=3, markersize=8)

            # Add observation count label
            ax.text(end, idx, f" n={count}", va="center", fontsize=9)

        # Formatting
        ax.set_yticks(range(len(coverage_df)))
        ax.set_yticklabels(coverage_df["indicator_code"])
        ax.set_xlabel("Year", fontsize=12)
        ax.set_ylabel("Indicator", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.grid(axis="x", alpha=0.3)

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig

    def plot_indicator_trend(
        self,
        ts_data: pd.DataFrame,
        indicator_code: str,
        indicator_name: Optional[str] = None,
        save_path: Optional[Path] = None,
        show_confidence: bool = True,
    ) -> plt.Figure:
        """
        Plot time series trend for a specific indicator.

        Args:
            ts_data: DataFrame with observation_date, value_numeric,
                    and optionally confidence columns.
            indicator_code: Indicator code for labeling.
            indicator_name: Human-readable indicator name.
            save_path: Optional path to save the figure.
            show_confidence: Whether to color points by confidence level.

        Returns:
            Matplotlib Figure object.
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # Sort by date
        ts_data = ts_data.sort_values("observation_date")

        # Plot line
        ax.plot(
            ts_data["observation_date"],
            ts_data["value_numeric"],
            marker="o",
            linewidth=2,
            markersize=8,
            color=self.PILLAR_COLORS["access"],
        )

        # Color by confidence if available
        if show_confidence and "confidence" in ts_data.columns:
            confidence_colors = {"high": "green", "medium": "orange", "low": "red"}
            for conf, color in confidence_colors.items():
                conf_data = ts_data[ts_data["confidence"] == conf]
                if not conf_data.empty:
                    ax.scatter(
                        conf_data["observation_date"],
                        conf_data["value_numeric"],
                        color=color,
                        s=100,
                        alpha=0.6,
                        label=f"{conf.capitalize()} confidence",
                        edgecolors="white",
                        linewidths=2,
                        zorder=5,
                    )

        # Formatting
        title = indicator_name or indicator_code
        ax.set_title(f"{title} Over Time", fontsize=14, fontweight="bold")
        ax.set_xlabel("Year", fontsize=12)
        ax.set_ylabel("Value (%)", fontsize=12)
        ax.grid(True, alpha=0.3)

        if show_confidence and "confidence" in ts_data.columns:
            ax.legend(loc="best")

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig

    def plot_events_overlay(
        self,
        ts_data: pd.DataFrame,
        events_data: pd.DataFrame,
        indicator_code: str,
        indicator_name: Optional[str] = None,
        save_path: Optional[Path] = None,
    ) -> plt.Figure:
        """
        Plot indicator trend with events overlaid.

        Args:
            ts_data: DataFrame with observation_date and value_numeric.
            events_data: DataFrame with event_date, title, category.
            indicator_code: Indicator code for labeling.
            indicator_name: Human-readable indicator name.
            save_path: Optional path to save the figure.

        Returns:
            Matplotlib Figure object.
        """
        fig, ax = plt.subplots(figsize=(14, 6))

        # Sort data
        ts_data = ts_data.sort_values("observation_date")

        # Plot trend line
        ax.plot(
            ts_data["observation_date"],
            ts_data["value_numeric"],
            marker="o",
            linewidth=2.5,
            markersize=10,
            color=self.PILLAR_COLORS["access"],
            label="Observed Value",
            zorder=3,
        )

        # Add events as vertical lines
        if events_data is not None and not events_data.empty:
            y_min, y_max = ax.get_ylim()

            for idx, event in events_data.iterrows():
                event_date = event["event_date"]
                category = event.get("category", "other")
                title = event.get("title", "Event")

                color = self.EVENT_COLORS.get(category, "#6C757D")

                # Vertical line for event
                ax.axvline(
                    event_date,
                    color=color,
                    linestyle="--",
                    linewidth=2,
                    alpha=0.7,
                    zorder=2,
                )

                # Event label (rotated)
                ax.text(
                    event_date,
                    y_max * 0.95,
                    title,
                    rotation=90,
                    verticalalignment="top",
                    horizontalalignment="right",
                    fontsize=9,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.3),
                )

        # Formatting
        title = indicator_name or indicator_code
        ax.set_title(f"{title} with Key Events", fontsize=14, fontweight="bold")
        ax.set_xlabel("Year", fontsize=12)
        ax.set_ylabel("Value (%)", fontsize=12)
        ax.grid(True, alpha=0.3, zorder=1)
        ax.legend(loc="best")

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig

    def plot_correlation_matrix(
        self,
        corr_matrix: pd.DataFrame,
        save_path: Optional[Path] = None,
        title: str = "Indicator Correlation Matrix",
    ) -> plt.Figure:
        """
        Create a correlation heatmap.

        Args:
            corr_matrix: Correlation matrix DataFrame.
            save_path: Optional path to save the figure.
            title: Plot title.

        Returns:
            Matplotlib Figure object.
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # Create heatmap
        sns.heatmap(
            corr_matrix,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            center=0,
            vmin=-1,
            vmax=1,
            square=True,
            linewidths=0.5,
            cbar_kws={"label": "Correlation Coefficient"},
            ax=ax,
        )

        # Formatting
        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)
        plt.xticks(rotation=45, ha="right")
        plt.yticks(rotation=0)

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig

    def plot_growth_rates(
        self,
        growth_data: pd.DataFrame,
        indicator_code: str,
        indicator_name: Optional[str] = None,
        growth_type: str = "percentage",
        save_path: Optional[Path] = None,
    ) -> plt.Figure:
        """
        Visualize growth rates over time.

        Args:
            growth_data: DataFrame with observation_date and growth columns.
            indicator_code: Indicator code for labeling.
            indicator_name: Human-readable indicator name.
            growth_type: Type of growth ('percentage', 'absolute', 'annualized').
            save_path: Optional path to save the figure.

        Returns:
            Matplotlib Figure object.
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # Determine growth column
        growth_col_map = {
            "percentage": "growth_percentage",
            "absolute": "growth_absolute",
            "annualized": "growth_annualized",
        }
        growth_col = growth_col_map.get(growth_type, "growth_percentage")

        if growth_col not in growth_data.columns:
            raise ValueError(f"Growth column '{growth_col}' not found in data")

        # Sort by date
        growth_data = growth_data.sort_values("observation_date")

        # Create bar colors based on positive/negative
        colors = ["green" if x >= 0 else "red" for x in growth_data[growth_col]]

        # Plot bars
        ax.bar(
            growth_data["observation_date"],
            growth_data[growth_col],
            color=colors,
            alpha=0.7,
            edgecolor="black",
            linewidth=1.5,
        )

        # Zero line
        ax.axhline(0, color="black", linewidth=1, linestyle="-", alpha=0.3)

        # Formatting
        title = indicator_name or indicator_code
        ylabel_map = {
            "percentage": "Growth Rate (%)",
            "absolute": "Absolute Change (pp)",
            "annualized": "Annualized Growth Rate (%)",
        }

        ax.set_title(
            f"{title} - {growth_type.capitalize()} Growth",
            fontsize=14,
            fontweight="bold",
        )
        ax.set_xlabel("Period", fontsize=12)
        ax.set_ylabel(ylabel_map.get(growth_type, "Growth"), fontsize=12)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig

    def plot_data_quality_summary(
        self, quality_summary: Dict[str, pd.DataFrame], save_path: Optional[Path] = None
    ) -> plt.Figure:
        """
        Create a multi-panel visualization of data quality metrics.

        Args:
            quality_summary: Dictionary with quality metrics from DataProcessor.
            save_path: Optional path to save the figure.

        Returns:
            Matplotlib Figure object.
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Data Quality Assessment", fontsize=16, fontweight="bold")

        # Plot 1: Record type distribution
        if "by_record_type" in quality_summary:
            data = quality_summary["by_record_type"]
            axes[0, 0].bar(data.index, data["count"], color=sns.color_palette("Set2"))
            axes[0, 0].set_title("Records by Type", fontsize=12, fontweight="bold")
            axes[0, 0].set_ylabel("Count")
            axes[0, 0].tick_params(axis="x", rotation=45)
            for i, v in enumerate(data["count"]):
                axes[0, 0].text(i, v, str(v), ha="center", va="bottom")

        # Plot 2: Confidence distribution
        if "by_confidence" in quality_summary:
            data = quality_summary["by_confidence"]
            colors = {"high": "green", "medium": "orange", "low": "red"}
            bar_colors = [colors.get(idx, "gray") for idx in data.index]
            axes[0, 1].bar(data.index, data["count"], color=bar_colors, alpha=0.7)
            axes[0, 1].set_title(
                "Observations by Confidence", fontsize=12, fontweight="bold"
            )
            axes[0, 1].set_ylabel("Count")
            for i, v in enumerate(data["count"]):
                axes[0, 1].text(i, v, str(v), ha="center", va="bottom")

        # Plot 3: Source type distribution
        if "by_source_type" in quality_summary:
            data = quality_summary["by_source_type"]
            axes[1, 0].barh(
                data.index, data["count"], color=sns.color_palette("Pastel1")
            )
            axes[1, 0].set_title(
                "Observations by Source Type", fontsize=12, fontweight="bold"
            )
            axes[1, 0].set_xlabel("Count")
            for i, v in enumerate(data["count"]):
                axes[1, 0].text(v, i, f" {v}", va="center")

        # Plot 4: Missing values
        if (
            "missing_values" in quality_summary
            and not quality_summary["missing_values"].empty
        ):
            data = quality_summary["missing_values"]
            axes[1, 1].barh(data.index, data["missing_count"], color="coral")
            axes[1, 1].set_title(
                "Missing Values by Column", fontsize=12, fontweight="bold"
            )
            axes[1, 1].set_xlabel("Missing Count")
            for i, v in enumerate(data["missing_count"]):
                axes[1, 1].text(v, i, f" {v}", va="center")
        else:
            axes[1, 1].text(
                0.5, 0.5, "No Missing Values", ha="center", va="center", fontsize=12
            )
            axes[1, 1].set_title("Missing Values", fontsize=12, fontweight="bold")
            axes[1, 1].axis("off")

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig

    def plot_pillar_comparison(
        self, disagg_data: pd.DataFrame, save_path: Optional[Path] = None
    ) -> plt.Figure:
        """
        Compare metrics across pillars.

        Args:
            disagg_data: DataFrame with pillar, total_records, unique_indicators.
            save_path: Optional path to save the figure.

        Returns:
            Matplotlib Figure object.
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Plot 1: Records per pillar
        colors = [self.PILLAR_COLORS.get(p, "#6C757D") for p in disagg_data["pillar"]]
        axes[0].bar(
            disagg_data["pillar"],
            disagg_data["total_records"],
            color=colors,
            alpha=0.7,
            edgecolor="black",
        )
        axes[0].set_title("Observations per Pillar", fontsize=12, fontweight="bold")
        axes[0].set_ylabel("Number of Observations")
        axes[0].tick_params(axis="x", rotation=45)
        for i, v in enumerate(disagg_data["total_records"]):
            axes[0].text(i, v, str(v), ha="center", va="bottom")

        # Plot 2: Unique indicators per pillar
        axes[1].bar(
            disagg_data["pillar"],
            disagg_data["unique_indicators"],
            color=colors,
            alpha=0.7,
            edgecolor="black",
        )
        axes[1].set_title(
            "Unique Indicators per Pillar", fontsize=12, fontweight="bold"
        )
        axes[1].set_ylabel("Number of Indicators")
        axes[1].tick_params(axis="x", rotation=45)
        for i, v in enumerate(disagg_data["unique_indicators"]):
            axes[1].text(i, v, str(v), ha="center", va="bottom")

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig

    def create_interactive_timeline(
        self,
        ts_data: pd.DataFrame,
        events_data: Optional[pd.DataFrame],
        indicator_code: str,
        indicator_name: Optional[str] = None,
    ) -> go.Figure:
        """
        Create an interactive timeline using Plotly.

        Args:
            ts_data: DataFrame with observation_date and value_numeric.
            events_data: Optional DataFrame with event_date, title, category.
            indicator_code: Indicator code.
            indicator_name: Human-readable name.

        Returns:
            Plotly Figure object.
        """
        fig = go.Figure()

        # Add main trend line
        fig.add_trace(
            go.Scatter(
                x=ts_data["observation_date"],
                y=ts_data["value_numeric"],
                mode="lines+markers",
                name="Observed Value",
                line=dict(color=self.PILLAR_COLORS["access"], width=3),
                marker=dict(size=10),
            )
        )

        # Add events if provided
        if events_data is not None and not events_data.empty:
            for idx, event in events_data.iterrows():
                # Convert timestamp to string for Plotly compatibility
                event_date = event["event_date"]
                event_date_str = (
                    event_date.strftime("%Y-%m-%d")
                    if hasattr(event_date, "strftime")
                    else str(event_date)
                )

                fig.add_vline(
                    x=event_date_str,
                    line_dash="dash",
                    line_color=self.EVENT_COLORS.get(
                        event.get("category", "other"), "gray"
                    ),
                    annotation_text=event.get("title", "Event"),
                    annotation_position="top",
                )

        # Layout
        title = indicator_name or indicator_code
        fig.update_layout(
            title=f"{title} Over Time",
            xaxis_title="Year",
            yaxis_title="Value (%)",
            hovermode="x unified",
            template="plotly_white",
        )

        return fig
