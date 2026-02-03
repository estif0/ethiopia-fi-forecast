"""Impact Validation Module for Testing Event Impact Models.

This module provides functionality to validate impact models against historical data
and measure prediction accuracy.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class ImpactValidator:
    """Validate event impact models against historical observations.

    This class tests whether modeled event impacts match actual observed changes
    in indicators, helping to calibrate and improve impact estimates.
    """

    def __init__(
        self,
        observations: pd.DataFrame,
        events: pd.DataFrame,
        impact_links: pd.DataFrame,
    ):
        """Initialize the ImpactValidator.

        Args:
            observations: DataFrame of indicator observations.
            events: DataFrame of events.
            impact_links: DataFrame of impact relationships.
        """
        self.observations = observations.copy()
        self.events = events.copy()
        self.impact_links = impact_links.copy()
        self.validation_results = {}

    def validate_against_historical(
        self,
        event_id: str,
        indicator_code: str,
        pre_period_end: str,
        post_period_end: str,
    ) -> Dict:
        """Compare predicted vs actual impact for a specific event.

        Args:
            event_id: ID of the event to validate.
            indicator_code: Indicator affected by the event.
            pre_period_end: End date of pre-event period.
            post_period_end: End date of post-event period for measuring impact.

        Returns:
            Dictionary with validation results including predicted and actual changes.
        """
        try:
            # Get event date
            event_row = self.events[self.events["record_id"] == event_id]
            if event_row.empty:
                return {"error": "Event not found"}

            event_date = pd.to_datetime(event_row.iloc[0]["event_date"])

            # Get observations for this indicator
            indicator_obs = self.observations[
                self.observations["indicator_code"] == indicator_code
            ].copy()

            if indicator_obs.empty:
                return {"error": "No observations found for indicator"}

            indicator_obs["observation_date"] = pd.to_datetime(
                indicator_obs["observation_date"]
            )
            indicator_obs = indicator_obs.sort_values("observation_date")

            # Get pre-event baseline
            pre_obs = indicator_obs[
                indicator_obs["observation_date"] <= pd.to_datetime(pre_period_end)
            ]
            if pre_obs.empty:
                return {"error": "No pre-event observations found"}
            baseline_value = pre_obs.iloc[-1]["value_numeric"]

            # Get post-event value
            post_obs = indicator_obs[
                (indicator_obs["observation_date"] > event_date)
                & (indicator_obs["observation_date"] <= pd.to_datetime(post_period_end))
            ]
            if post_obs.empty:
                return {"error": "No post-event observations found"}
            post_value = post_obs.iloc[-1]["value_numeric"]

            # Calculate actual change
            actual_change = post_value - baseline_value
            actual_change_pct = (
                (actual_change / baseline_value * 100) if baseline_value != 0 else 0
            )

            # Get predicted impact from impact_links
            impact_link = self.impact_links[
                (self.impact_links["parent_id"] == event_id)
                & (self.impact_links["indicator_code"] == indicator_code)
            ]

            if impact_link.empty:
                predicted_direction = 0
                predicted_magnitude = 0
            else:
                link = impact_link.iloc[0]
                direction = link.get("impact_direction", 0)
                if direction == "positive":
                    predicted_direction = 1
                elif direction == "negative":
                    predicted_direction = -1
                else:
                    predicted_direction = direction

                predicted_magnitude = link.get("impact_magnitude", 0)

            # Calculate predicted change (simplified)
            predicted_change = (
                baseline_value * predicted_magnitude * predicted_direction
            )

            # Calculate residual
            residual = actual_change - predicted_change
            residual_pct = (
                abs(residual / baseline_value * 100) if baseline_value != 0 else 0
            )

            # Determine if direction was correct
            direction_correct = (
                np.sign(actual_change) == np.sign(predicted_change)
            ) or (predicted_change == 0)

            result = {
                "event_id": event_id,
                "indicator_code": indicator_code,
                "event_date": event_date.strftime("%Y-%m-%d"),
                "baseline_value": baseline_value,
                "post_value": post_value,
                "actual_change": actual_change,
                "actual_change_pct": actual_change_pct,
                "predicted_change": predicted_change,
                "predicted_direction": predicted_direction,
                "residual": residual,
                "residual_pct": residual_pct,
                "direction_correct": direction_correct,
                "pre_period_end": pre_period_end,
                "post_period_end": post_period_end,
            }

            # Store validation result
            self.validation_results[f"{event_id}_{indicator_code}"] = result

            return result

        except Exception as e:
            return {"error": f"Validation failed: {str(e)}"}

    def calculate_residuals(
        self, validation_results: Optional[List[Dict]] = None
    ) -> pd.DataFrame:
        """Measure prediction errors across multiple validations.

        Args:
            validation_results: List of validation result dictionaries.
                              If None, uses stored validation results.

        Returns:
            DataFrame summarizing residuals and errors.
        """
        if validation_results is None:
            if not self.validation_results:
                return pd.DataFrame()
            validation_results = list(self.validation_results.values())

        # Filter out error results
        valid_results = [r for r in validation_results if "error" not in r]

        if not valid_results:
            return pd.DataFrame()

        # Create residuals summary
        residuals_df = pd.DataFrame(valid_results)

        # Calculate summary statistics
        summary = {
            "mean_residual": residuals_df["residual"].mean(),
            "std_residual": residuals_df["residual"].std(),
            "mean_abs_residual": residuals_df["residual"].abs().mean(),
            "mean_residual_pct": residuals_df["residual_pct"].mean(),
            "direction_accuracy": residuals_df["direction_correct"].mean() * 100,
        }

        return residuals_df, summary

    def generate_validation_report(self) -> str:
        """Summarize validation results in a readable report.

        Returns:
            String containing formatted validation report.
        """
        if not self.validation_results:
            return "No validation results available. Run validate_against_historical() first."

        residuals_df, summary = self.calculate_residuals()

        if residuals_df.empty:
            return "No valid validation results to report."

        report = []
        report.append("=" * 70)
        report.append("EVENT IMPACT VALIDATION REPORT")
        report.append("=" * 70)
        report.append("")

        report.append(f"Total Validations: {len(residuals_df)}")
        report.append(f"Direction Accuracy: {summary['direction_accuracy']:.1f}%")
        report.append("")

        report.append("Residual Statistics:")
        report.append(f"  Mean Residual: {summary['mean_residual']:.4f}")
        report.append(f"  Mean Absolute Residual: {summary['mean_abs_residual']:.4f}")
        report.append(f"  Standard Deviation: {summary['std_residual']:.4f}")
        report.append(f"  Mean Residual %: {summary['mean_residual_pct']:.2f}%")
        report.append("")

        report.append("-" * 70)
        report.append("Individual Validation Results:")
        report.append("-" * 70)

        for _, row in residuals_df.iterrows():
            report.append(f"\nEvent: {row['event_id']}")
            report.append(f"Indicator: {row['indicator_code']}")
            report.append(f"Event Date: {row['event_date']}")
            report.append(
                f"Actual Change: {row['actual_change']:.4f} ({row['actual_change_pct']:.2f}%)"
            )
            report.append(f"Predicted Change: {row['predicted_change']:.4f}")
            report.append(
                f"Residual: {row['residual']:.4f} ({row['residual_pct']:.2f}%)"
            )
            report.append(
                f"Direction Correct: {'✓' if row['direction_correct'] else '✗'}"
            )

        report.append("")
        report.append("=" * 70)

        return "\n".join(report)

    def validate_event_batch(
        self, event_indicator_pairs: List[Tuple[str, str, str, str]]
    ) -> pd.DataFrame:
        """Validate multiple event-indicator pairs.

        Args:
            event_indicator_pairs: List of tuples (event_id, indicator_code,
                                  pre_period_end, post_period_end).

        Returns:
            DataFrame with validation results for all pairs.
        """
        results = []

        for event_id, indicator_code, pre_end, post_end in event_indicator_pairs:
            result = self.validate_against_historical(
                event_id, indicator_code, pre_end, post_end
            )
            if "error" not in result:
                results.append(result)

        return pd.DataFrame(results) if results else pd.DataFrame()

    def compare_predicted_actual_trends(
        self, indicator_code: str, start_date: str, end_date: str
    ) -> Dict:
        """Compare overall predicted vs actual trends for an indicator.

        Args:
            indicator_code: Indicator to analyze.
            start_date: Start of analysis period.
            end_date: End of analysis period.

        Returns:
            Dictionary with trend comparison data.
        """
        try:
            # Get observations in period
            indicator_obs = self.observations[
                self.observations["indicator_code"] == indicator_code
            ].copy()

            indicator_obs["observation_date"] = pd.to_datetime(
                indicator_obs["observation_date"]
            )

            period_obs = indicator_obs[
                (indicator_obs["observation_date"] >= pd.to_datetime(start_date))
                & (indicator_obs["observation_date"] <= pd.to_datetime(end_date))
            ].sort_values("observation_date")

            if period_obs.empty or len(period_obs) < 2:
                return {"error": "Insufficient observations for trend analysis"}

            # Calculate actual trend
            dates = period_obs["observation_date"].values
            values = period_obs["value_numeric"].values

            # Simple linear trend
            x = np.arange(len(dates))
            actual_slope = np.polyfit(x, values, 1)[0]

            # Get events in period
            self.events["event_date"] = pd.to_datetime(self.events["event_date"])
            period_events = self.events[
                (self.events["event_date"] >= pd.to_datetime(start_date))
                & (self.events["event_date"] <= pd.to_datetime(end_date))
            ]

            # Calculate predicted impact from events
            total_predicted_impact = 0
            for _, event in period_events.iterrows():
                impact_link = self.impact_links[
                    (self.impact_links["parent_id"] == event["record_id"])
                    & (self.impact_links["indicator_code"] == indicator_code)
                ]

                if not impact_link.empty:
                    link = impact_link.iloc[0]
                    direction = 1 if link.get("impact_direction") == "positive" else -1
                    magnitude = link.get("impact_magnitude", 0)
                    total_predicted_impact += direction * magnitude

            return {
                "indicator_code": indicator_code,
                "period": f"{start_date} to {end_date}",
                "actual_slope": actual_slope,
                "num_events": len(period_events),
                "total_predicted_impact": total_predicted_impact,
                "observations": len(period_obs),
            }

        except Exception as e:
            return {"error": f"Trend comparison failed: {str(e)}"}
