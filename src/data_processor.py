"""
Data Processor Module for Ethiopia Financial Inclusion Forecasting

This module provides the DataProcessor class for filtering, transforming,
and analyzing the unified financial inclusion dataset.

Classes:
    DataProcessor: Handles data filtering and time series extraction.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class DataProcessor:
    """
    Process and transform Ethiopia financial inclusion data.

    This class provides methods to filter records by type, extract time series,
    calculate growth rates, and prepare data for analysis and visualization.

    Attributes:
        data (pd.DataFrame): The unified financial inclusion dataset.
        reference_codes (pd.DataFrame): Reference codes for indicators.
    """

    def __init__(
        self, data: pd.DataFrame, reference_codes: Optional[pd.DataFrame] = None
    ):
        """
        Initialize DataProcessor with dataset.

        Args:
            data: Unified financial inclusion DataFrame.
            reference_codes: Optional DataFrame with indicator code definitions.

        Raises:
            ValueError: If data is empty or missing required columns.
        """
        if data is None or data.empty:
            raise ValueError("Data cannot be None or empty")

        required_cols = ["record_type", "record_id"]
        missing = [col for col in required_cols if col not in data.columns]
        if missing:
            raise ValueError(f"Data missing required columns: {missing}")

        self.data = data.copy()
        self.reference_codes = (
            reference_codes.copy() if reference_codes is not None else None
        )

        # Convert date columns to datetime if they exist
        date_cols = ["observation_date", "event_date", "target_date", "collection_date"]
        for col in date_cols:
            if col in self.data.columns:
                self.data[col] = pd.to_datetime(self.data[col], errors="coerce")

    def filter_by_record_type(
        self, record_types: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Filter dataset by record type(s).

        Args:
            record_types: List of record types to include.
                         Valid values: 'observation', 'event', 'impact_link', 'target'.
                         If None, returns all records.

        Returns:
            Filtered DataFrame.

        Raises:
            ValueError: If invalid record_type provided.
        """
        if record_types is None:
            return self.data.copy()

        valid_types = ["observation", "event", "impact_link", "target"]
        invalid = [rt for rt in record_types if rt not in valid_types]
        if invalid:
            raise ValueError(f"Invalid record types: {invalid}. Valid: {valid_types}")

        return self.data[self.data["record_type"].isin(record_types)].copy()

    def get_time_series(
        self, indicator_code: str, disaggregation: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Extract time series for a specific indicator.

        Args:
            indicator_code: Indicator code (e.g., 'ACC_OWNERSHIP').
            disaggregation: Optional disaggregation dimension
                           (e.g., 'gender', 'location', 'age').

        Returns:
            DataFrame with columns: observation_date, value_numeric,
                                   and disaggregation columns if specified.

        Raises:
            ValueError: If indicator_code not found in data.
        """
        obs = self.data[self.data["record_type"] == "observation"].copy()

        indicator_data = obs[obs["indicator_code"] == indicator_code]
        if indicator_data.empty:
            raise ValueError(f"No data found for indicator: {indicator_code}")

        # Select relevant columns
        cols = [
            "observation_date",
            "value_numeric",
            "pillar",
            "confidence",
            "source_type",
        ]

        if disaggregation:
            if disaggregation not in indicator_data.columns:
                raise ValueError(f"Disaggregation column '{disaggregation}' not found")
            cols.append(disaggregation)

        result = indicator_data[cols].copy()
        result = result.sort_values("observation_date")

        return result

    def calculate_growth_rates(
        self, indicator_code: str, period_type: str = "absolute"
    ) -> pd.DataFrame:
        """
        Calculate growth rates for an indicator over time.

        Args:
            indicator_code: Indicator code to analyze.
            period_type: Type of growth calculation:
                        - 'absolute': Absolute difference
                        - 'percentage': Percentage change
                        - 'annualized': Annualized growth rate (CAGR)

        Returns:
            DataFrame with observation_date, value_numeric, and growth metrics.

        Raises:
            ValueError: If indicator not found or period_type invalid.
        """
        valid_periods = ["absolute", "percentage", "annualized"]
        if period_type not in valid_periods:
            raise ValueError(
                f"Invalid period_type: {period_type}. Valid: {valid_periods}"
            )

        ts_data = self.get_time_series(indicator_code)

        if len(ts_data) < 2:
            raise ValueError(
                f"Insufficient data points for growth calculation: {len(ts_data)}"
            )

        ts_data = ts_data.sort_values("observation_date").copy()

        # Calculate different growth metrics
        ts_data["value_prev"] = ts_data["value_numeric"].shift(1)
        ts_data["date_prev"] = ts_data["observation_date"].shift(1)

        # Absolute growth
        ts_data["growth_absolute"] = ts_data["value_numeric"] - ts_data["value_prev"]

        # Percentage growth
        ts_data["growth_percentage"] = (
            (ts_data["value_numeric"] - ts_data["value_prev"])
            / ts_data["value_prev"]
            * 100
        )

        # Years between observations
        ts_data["years_elapsed"] = (
            ts_data["observation_date"] - ts_data["date_prev"]
        ).dt.days / 365.25

        # Annualized growth rate (CAGR)
        ts_data["growth_annualized"] = (
            (ts_data["value_numeric"] / ts_data["value_prev"])
            ** (1 / ts_data["years_elapsed"])
            - 1
        ) * 100

        # Select columns based on period_type
        cols = ["observation_date", "value_numeric", "pillar", "confidence"]

        if period_type == "absolute":
            cols.extend(["growth_absolute", "value_prev"])
        elif period_type == "percentage":
            cols.extend(["growth_percentage", "value_prev"])
        elif period_type == "annualized":
            cols.extend(["growth_annualized", "years_elapsed", "value_prev"])

        return ts_data[cols].dropna()

    def get_disaggregated_data(
        self, indicator_code: Optional[str] = None, dimension: str = "pillar"
    ) -> pd.DataFrame:
        """
        Get data disaggregated by a specific dimension.

        Args:
            indicator_code: Optional indicator to filter. If None, all observations.
            dimension: Dimension to disaggregate by (e.g., 'pillar', 'gender',
                      'location', 'confidence', 'source_type').

        Returns:
            DataFrame grouped by dimension with aggregated statistics.

        Raises:
            ValueError: If dimension column not found.
        """
        obs = self.data[self.data["record_type"] == "observation"].copy()

        if indicator_code:
            obs = obs[obs["indicator_code"] == indicator_code]

        if dimension not in obs.columns:
            raise ValueError(f"Dimension column '{dimension}' not found in data")

        # Group by dimension and provide summary stats
        grouped = (
            obs.groupby(dimension)
            .agg(
                {
                    "record_id": "count",
                    "value_numeric": ["mean", "min", "max", "count"],
                    "indicator_code": "nunique",
                }
            )
            .reset_index()
        )

        # Flatten column names
        grouped.columns = [
            dimension,
            "total_records",
            "mean_value",
            "min_value",
            "max_value",
            "value_count",
            "unique_indicators",
        ]

        return grouped

    def get_temporal_coverage(self) -> pd.DataFrame:
        """
        Analyze temporal coverage of observations by indicator.

        Returns:
            DataFrame with indicator_code, earliest_date, latest_date,
            observation_count, and year_span.
        """
        obs = self.data[self.data["record_type"] == "observation"].copy()

        coverage = (
            obs.groupby("indicator_code")
            .agg({"observation_date": ["min", "max", "count"]})
            .reset_index()
        )

        coverage.columns = [
            "indicator_code",
            "earliest_date",
            "latest_date",
            "observation_count",
        ]

        # Calculate year span
        coverage["year_span"] = (
            coverage["latest_date"] - coverage["earliest_date"]
        ).dt.days / 365.25

        return coverage.sort_values("observation_count", ascending=False)

    def get_data_quality_summary(self) -> Dict[str, pd.DataFrame]:
        """
        Generate comprehensive data quality assessment.

        Returns:
            Dictionary with quality metrics:
            - 'by_confidence': Distribution by confidence level
            - 'by_source_type': Distribution by source type
            - 'by_record_type': Distribution by record type
            - 'missing_values': Count of missing values per column
        """
        quality = {}

        # Confidence distribution (observations only)
        obs = self.data[self.data["record_type"] == "observation"]
        if "confidence" in obs.columns:
            quality["by_confidence"] = (
                obs["confidence"].value_counts().to_frame("count")
            )

        # Source type distribution
        if "source_type" in obs.columns:
            quality["by_source_type"] = (
                obs["source_type"].value_counts().to_frame("count")
            )

        # Record type distribution
        quality["by_record_type"] = (
            self.data["record_type"].value_counts().to_frame("count")
        )

        # Missing values analysis
        missing = self.data.isnull().sum()
        quality["missing_values"] = missing[missing > 0].to_frame("missing_count")

        return quality

    def get_correlation_matrix(
        self,
        indicator_codes: Optional[List[str]] = None,
        date_col: str = "observation_date",
    ) -> pd.DataFrame:
        """
        Create correlation matrix between indicators.

        Args:
            indicator_codes: List of indicator codes to include.
                           If None, uses all indicators.
            date_col: Date column to align time series.

        Returns:
            Correlation matrix DataFrame.
        """
        obs = self.data[self.data["record_type"] == "observation"].copy()

        if indicator_codes:
            obs = obs[obs["indicator_code"].isin(indicator_codes)]

        # Pivot to wide format
        pivot = obs.pivot_table(
            index=date_col,
            columns="indicator_code",
            values="value_numeric",
            aggfunc="mean",
        )

        # Calculate correlation
        corr_matrix = pivot.corr()

        return corr_matrix

    def get_event_summary(self) -> pd.DataFrame:
        """
        Get summary of events by category and year.

        Returns:
            DataFrame with event summaries.
        """
        events = self.data[self.data["record_type"] == "event"].copy()

        if events.empty:
            return pd.DataFrame()

        # Extract year from event_date
        events["event_year"] = events["event_date"].dt.year

        summary = (
            events.groupby(["category", "event_year"])
            .agg(
                {
                    "record_id": "count",
                    "title": lambda x: ", ".join(x[:3]),  # First 3 event titles
                }
            )
            .reset_index()
        )

        summary.columns = ["category", "year", "event_count", "sample_events"]

        return summary.sort_values(["year", "event_count"], ascending=[True, False])

    def prepare_indicator_for_plotting(
        self, indicator_code: str, include_events: bool = False
    ) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        """
        Prepare indicator data for visualization.

        Args:
            indicator_code: Indicator code to prepare.
            include_events: Whether to include event data aligned to the timeline.

        Returns:
            Tuple of (indicator_data, events_data).
            events_data is None if include_events is False.
        """
        # Get time series
        ts_data = self.get_time_series(indicator_code)

        events_data = None
        if include_events:
            events = self.data[self.data["record_type"] == "event"].copy()
            if not events.empty:
                # Filter events within the observation date range
                min_date = ts_data["observation_date"].min()
                max_date = ts_data["observation_date"].max()
                events_data = events[
                    (events["event_date"] >= min_date)
                    & (events["event_date"] <= max_date)
                ].copy()

        return ts_data, events_data
