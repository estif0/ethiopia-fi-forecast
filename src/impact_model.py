"""Impact Model for Event-Indicator Relationships.

This module provides functionality to analyze how events (policy changes, product launches,
infrastructure developments) impact financial inclusion indicators.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class ImpactModel:
    """Model event impacts on financial inclusion indicators.

    This class analyzes impact_link records to understand relationships between
    events and indicators, build association matrices, and estimate impact magnitudes.
    """

    def __init__(self, data: pd.DataFrame):
        """Initialize the ImpactModel.

        Args:
            data: Unified dataset containing observations, events, and impact_links.
        """
        self.data = data
        self.events = None
        self.observations = None
        self.impact_links = None
        self.matrix = None

    def load_impact_links(self) -> pd.DataFrame:
        """Load and parse impact relationship records.

        Returns:
            DataFrame containing impact_link records with event-indicator relationships.
        """
        try:
            # Filter for different record types
            self.events = self.data[self.data["record_type"] == "event"].copy()
            self.observations = self.data[
                self.data["record_type"] == "observation"
            ].copy()
            self.impact_links = self.data[
                self.data["record_type"] == "impact_link"
            ].copy()

            # Ensure parent_id is present in impact_links
            if "parent_id" not in self.impact_links.columns:
                raise ValueError("impact_link records must have parent_id column")

            return self.impact_links

        except Exception as e:
            raise RuntimeError(f"Error loading impact links: {str(e)}")

    def create_event_indicator_matrix(self) -> pd.DataFrame:
        """Build event-indicator association matrix.

        Creates a matrix showing which events impact which indicators, with
        impact direction and magnitude.

        Returns:
            DataFrame with events as rows, indicators as columns, and impact values.
        """
        if self.impact_links is None:
            self.load_impact_links()

        # Get unique events and indicators
        event_ids = self.events["record_id"].unique()
        indicator_codes = self.observations["indicator_code"].dropna().unique()

        # Create empty matrix
        matrix = pd.DataFrame(0.0, index=event_ids, columns=indicator_codes)

        # Fill matrix with impact values
        for _, link in self.impact_links.iterrows():
            parent_id = link["parent_id"]
            indicator = link.get("indicator_code")

            if pd.notna(parent_id) and pd.notna(indicator):
                if parent_id in matrix.index and indicator in matrix.columns:
                    # Combine direction and magnitude
                    direction = link.get("impact_direction", 0)
                    magnitude = link.get("impact_magnitude", 1.0)

                    # Convert direction to numeric if it's text
                    if direction == "positive":
                        direction = 1
                    elif direction == "negative":
                        direction = -1

                    matrix.loc[parent_id, indicator] = direction * magnitude

        # Add event metadata
        event_info = self.events.set_index("record_id")[
            ["description", "event_date", "category"]
        ]
        matrix = matrix.join(event_info, how="left")

        self.matrix = matrix
        return matrix

    def apply_lag_effects(
        self, observation_date: str, event_date: str, lag_months: int = 6
    ) -> float:
        """Model temporal lag between event and its impact.

        Args:
            observation_date: Date when indicator was measured.
            event_date: Date when event occurred.
            lag_months: Expected lag time in months for impact to materialize.

        Returns:
            Lag factor between 0 and 1 indicating timing relevance.
        """
        try:
            obs_dt = pd.to_datetime(observation_date)
            evt_dt = pd.to_datetime(event_date)

            # Calculate months difference
            months_diff = (obs_dt.year - evt_dt.year) * 12 + (
                obs_dt.month - evt_dt.month
            )

            if months_diff < 0:
                # Event hasn't happened yet
                return 0.0
            elif months_diff <= lag_months:
                # Impact is materializing (linear ramp-up)
                return months_diff / lag_months
            else:
                # Full impact realized
                return 1.0

        except Exception as e:
            print(f"Warning: Error calculating lag effect: {str(e)}")
            return 0.5

    def estimate_impact(
        self,
        event_id: str,
        indicator_code: str,
        baseline_value: float,
        observation_date: str,
    ) -> Dict:
        """Calculate impact magnitude for a specific event-indicator pair.

        Args:
            event_id: ID of the event.
            indicator_code: Code of the indicator being impacted.
            baseline_value: Baseline indicator value without event impact.
            observation_date: Date of observation for lag calculation.

        Returns:
            Dictionary with impact estimate, direction, and confidence.
        """
        if self.matrix is None:
            self.create_event_indicator_matrix()

        try:
            # Get impact from matrix
            if event_id not in self.matrix.index:
                return {"impact": 0.0, "direction": 0, "confidence": 0.0}

            event_row = self.matrix.loc[event_id]
            impact_value = event_row.get(indicator_code, 0.0)

            if impact_value == 0:
                return {"impact": 0.0, "direction": 0, "confidence": 0.0}

            # Apply lag effect
            event_date = event_row.get("event_date")
            lag_factor = self.apply_lag_effects(observation_date, event_date)

            # Calculate adjusted impact
            direction = np.sign(impact_value)
            magnitude = abs(impact_value)
            adjusted_impact = baseline_value * magnitude * lag_factor * direction

            return {
                "impact": adjusted_impact,
                "direction": int(direction),
                "magnitude": magnitude,
                "lag_factor": lag_factor,
                "confidence": 0.7 if lag_factor > 0.5 else 0.4,
            }

        except Exception as e:
            print(f"Warning: Error estimating impact: {str(e)}")
            return {"impact": 0.0, "direction": 0, "confidence": 0.0}

    def combine_multiple_events(
        self,
        event_ids: List[str],
        indicator_code: str,
        baseline_value: float,
        observation_date: str,
    ) -> Dict:
        """Aggregate impacts from multiple concurrent events.

        Args:
            event_ids: List of event IDs affecting the indicator.
            indicator_code: Code of the indicator.
            baseline_value: Baseline value.
            observation_date: Date of observation.

        Returns:
            Dictionary with combined impact estimate.
        """
        total_impact = 0.0
        event_impacts = []

        for event_id in event_ids:
            impact_dict = self.estimate_impact(
                event_id, indicator_code, baseline_value, observation_date
            )
            total_impact += impact_dict["impact"]
            event_impacts.append(
                {
                    "event_id": event_id,
                    "impact": impact_dict["impact"],
                    "confidence": impact_dict["confidence"],
                }
            )

        # Calculate weighted average confidence
        if event_impacts:
            avg_confidence = np.mean([e["confidence"] for e in event_impacts])
        else:
            avg_confidence = 0.0

        return {
            "combined_impact": total_impact,
            "individual_impacts": event_impacts,
            "confidence": avg_confidence,
        }

    def get_events_for_indicator(
        self, indicator_code: str, min_magnitude: float = 0.0
    ) -> pd.DataFrame:
        """Get all events that impact a specific indicator.

        Args:
            indicator_code: Code of the indicator.
            min_magnitude: Minimum impact magnitude threshold.

        Returns:
            DataFrame of events impacting the indicator.
        """
        if self.matrix is None:
            self.create_event_indicator_matrix()

        # Filter matrix for non-zero impacts on this indicator
        if indicator_code not in self.matrix.columns:
            return pd.DataFrame()

        impacts = self.matrix[indicator_code]
        relevant = impacts[abs(impacts) >= min_magnitude]

        # Get full event details
        result = self.matrix.loc[
            relevant.index, ["description", "event_date", "category", indicator_code]
        ]
        result = result.rename(columns={indicator_code: "impact_value"})

        return result.sort_values("event_date")

    def get_indicators_for_event(self, event_id: str) -> pd.DataFrame:
        """Get all indicators impacted by a specific event.

        Args:
            event_id: ID of the event.

        Returns:
            DataFrame of indicators impacted by the event.
        """
        if self.matrix is None:
            self.create_event_indicator_matrix()

        if event_id not in self.matrix.index:
            return pd.DataFrame()

        # Get non-zero impacts for this event
        event_row = self.matrix.loc[event_id]

        # Get indicator columns only (exclude metadata)
        indicator_cols = [
            col
            for col in self.matrix.columns
            if col not in ["description", "event_date", "category"]
        ]

        impacts = event_row[indicator_cols]
        non_zero = impacts[impacts != 0]

        result = pd.DataFrame(
            {"indicator_code": non_zero.index, "impact_value": non_zero.values}
        )

        return result.sort_values("impact_value", key=abs, ascending=False)
