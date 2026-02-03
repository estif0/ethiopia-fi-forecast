"""
Financial Inclusion Forecaster Module

This module provides forecasting capabilities for financial inclusion indicators
using multiple approaches: trend regression, event-augmented models, and scenario analysis.

Classes:
    FinancialInclusionForecaster: Main forecasting class with multiple methods
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from scipy import stats
from datetime import datetime
import warnings


class FinancialInclusionForecaster:
    """
    Forecaster for financial inclusion indicators using multiple methodologies.

    Supports:
    - Trend-based forecasting (linear, polynomial, exponential)
    - Event-augmented forecasting (incorporating impact estimates)
    - Scenario analysis (optimistic, base, pessimistic)
    - Uncertainty quantification with confidence intervals

    Attributes:
        data (pd.DataFrame): Historical observation data
        events_data (pd.DataFrame): Event data for impact modeling
        impact_estimates (pd.DataFrame): Pre-computed event impact estimates
        forecast_results (Dict): Storage for forecast outputs
    """

    def __init__(
        self,
        data: pd.DataFrame,
        events_data: Optional[pd.DataFrame] = None,
        impact_estimates: Optional[pd.DataFrame] = None,
    ):
        """
        Initialize forecaster with historical data.

        Args:
            data: Historical observations with indicator_code, observation_date, value_numeric
            events_data: Optional event data for event-augmented forecasting
            impact_estimates: Optional pre-computed impact estimates from ImpactModel
        """
        self.data = data.copy()
        self.events_data = events_data.copy() if events_data is not None else None
        self.impact_estimates = (
            impact_estimates.copy() if impact_estimates is not None else None
        )
        self.forecast_results = {}

        # Prepare data
        self._prepare_data()

    def _prepare_data(self) -> None:
        """Prepare data for forecasting: parse dates, sort, validate."""
        if "observation_date" in self.data.columns:
            self.data["observation_date"] = pd.to_datetime(
                self.data["observation_date"]
            )
            self.data = self.data.sort_values("observation_date")

        if self.events_data is not None and "event_date" in self.events_data.columns:
            self.events_data["event_date"] = pd.to_datetime(
                self.events_data["event_date"]
            )

    def fit_trend_model(
        self, indicator_code: str, trend_type: str = "linear", min_points: int = 3
    ) -> Dict:
        """
        Fit a trend model to historical data for a specific indicator.

        Args:
            indicator_code: Indicator to forecast (e.g., 'ACC_OWNERSHIP')
            trend_type: Type of trend ('linear', 'polynomial', 'exponential')
            min_points: Minimum data points required to fit model

        Returns:
            Dictionary with model parameters, statistics, and diagnostics

        Raises:
            ValueError: If insufficient data points or invalid trend type
        """
        # Filter data for indicator
        indicator_data = self.data[self.data["indicator_code"] == indicator_code].copy()

        if len(indicator_data) < min_points:
            raise ValueError(
                f"Insufficient data: {len(indicator_data)} points, need {min_points}"
            )

        # Prepare X (years) and y (values)
        indicator_data["year"] = indicator_data["observation_date"].dt.year
        X = indicator_data["year"].values
        y = indicator_data["value_numeric"].values

        # Normalize X to avoid numerical issues
        X_normalized = (X - X.min()) / (X.max() - X.min() + 1e-10)

        # Fit model based on trend type
        if trend_type == "linear":
            coeffs = np.polyfit(X_normalized, y, deg=1)
            fitted_values = np.polyval(coeffs, X_normalized)

        elif trend_type == "polynomial":
            # Use degree 2 for polynomial
            coeffs = np.polyfit(X_normalized, y, deg=2)
            fitted_values = np.polyval(coeffs, X_normalized)

        elif trend_type == "exponential":
            # Fit log-linear model for exponential trend
            # y = a * exp(b * x) -> log(y) = log(a) + b * x
            y_positive = np.maximum(y, 1e-10)  # Ensure positive
            log_y = np.log(y_positive)
            coeffs_log = np.polyfit(X_normalized, log_y, deg=1)
            fitted_values = np.exp(np.polyval(coeffs_log, X_normalized))
            # Store as (a, b) where y = a * exp(b * x)
            coeffs = (np.exp(coeffs_log[1]), coeffs_log[0])

        else:
            raise ValueError(f"Invalid trend_type: {trend_type}")

        # Calculate statistics
        residuals = y - fitted_values
        rmse = np.sqrt(np.mean(residuals**2))
        mae = np.mean(np.abs(residuals))
        r_squared = 1 - (np.sum(residuals**2) / np.sum((y - np.mean(y)) ** 2))

        # Calculate standard error of residuals for confidence intervals
        std_error = np.std(residuals, ddof=len(coeffs))

        model_info = {
            "indicator_code": indicator_code,
            "trend_type": trend_type,
            "coefficients": coeffs,
            "X_min": X.min(),
            "X_max": X.max(),
            "fitted_values": fitted_values,
            "residuals": residuals,
            "rmse": rmse,
            "mae": mae,
            "r_squared": r_squared,
            "std_error": std_error,
            "n_points": len(X),
            "historical_years": X.tolist(),
            "historical_values": y.tolist(),
        }

        return model_info

    def forecast_trend(
        self,
        model_info: Dict,
        forecast_years: List[int],
        confidence_level: float = 0.95,
    ) -> pd.DataFrame:
        """
        Generate forecasts using fitted trend model.

        Args:
            model_info: Model information from fit_trend_model()
            forecast_years: Years to forecast (e.g., [2025, 2026, 2027])
            confidence_level: Confidence level for intervals (default 0.95)

        Returns:
            DataFrame with forecast, lower_bound, upper_bound for each year
        """
        trend_type = model_info["trend_type"]
        coeffs = model_info["coefficients"]
        X_min = model_info["X_min"]
        X_max = model_info["X_max"]
        std_error = model_info["std_error"]
        n_points = model_info["n_points"]

        # Normalize forecast years
        forecast_years_array = np.array(forecast_years)
        X_normalized = (forecast_years_array - X_min) / (X_max - X_min + 1e-10)

        # Generate point forecasts
        if trend_type == "linear" or trend_type == "polynomial":
            point_forecast = np.polyval(coeffs, X_normalized)
        elif trend_type == "exponential":
            a, b = coeffs
            point_forecast = a * np.exp(b * X_normalized)

        # Calculate confidence intervals
        # Use t-distribution for small sample sizes
        t_value = stats.t.ppf((1 + confidence_level) / 2, df=n_points - len(coeffs))

        # Increase uncertainty for extrapolation (further from historical data)
        max_historical_year = X_max
        years_ahead = forecast_years_array - max_historical_year
        # Uncertainty grows with sqrt of time ahead (standard for time series)
        extrapolation_factor = np.sqrt(1 + years_ahead / n_points)

        margin_of_error = t_value * std_error * extrapolation_factor

        results = pd.DataFrame(
            {
                "year": forecast_years,
                "indicator_code": model_info["indicator_code"],
                "forecast": point_forecast,
                "lower_bound": point_forecast - margin_of_error,
                "upper_bound": point_forecast + margin_of_error,
                "trend_type": trend_type,
                "confidence_level": confidence_level,
            }
        )

        # Ensure bounds are within valid range [0, 100] for percentage indicators
        results["lower_bound"] = results["lower_bound"].clip(0, 100)
        results["upper_bound"] = results["upper_bound"].clip(0, 100)
        results["forecast"] = results["forecast"].clip(0, 100)

        return results

    def apply_event_adjustments(
        self,
        base_forecast: pd.DataFrame,
        future_events: pd.DataFrame,
        adjustment_method: str = "additive",
    ) -> pd.DataFrame:
        """
        Adjust base forecast using anticipated future event impacts.

        Args:
            base_forecast: Base forecast from trend model
            future_events: DataFrame with future events and their anticipated impacts
            adjustment_method: How to apply adjustments ('additive' or 'multiplicative')

        Returns:
            Adjusted forecast DataFrame
        """
        adjusted_forecast = base_forecast.copy()

        if future_events is None or len(future_events) == 0:
            warnings.warn("No future events provided, returning base forecast")
            return adjusted_forecast

        # Process each forecast point
        for idx, row in adjusted_forecast.iterrows():
            year = row["year"]
            indicator = row["indicator_code"]
            base_value = row["forecast"]

            # Find events affecting this indicator in this year or before
            relevant_events = future_events[
                (future_events["event_date"].dt.year <= year)
            ]

            total_adjustment = 0

            for _, event in relevant_events.iterrows():
                # Get impact magnitude for this indicator (if available)
                if self.impact_estimates is not None:
                    impact_rows = self.impact_estimates[
                        (self.impact_estimates["event_id"] == event.get("record_id"))
                        & (self.impact_estimates["indicator_code"] == indicator)
                    ]

                    if len(impact_rows) > 0:
                        impact_value = impact_rows.iloc[0]["estimated_impact"]
                        total_adjustment += impact_value
                else:
                    # Use a default impact based on event category if no estimates
                    event_category = event.get("category", "unknown")
                    if event_category == "product_launch":
                        total_adjustment += 2.0  # Default +2pp for product launch
                    elif event_category == "policy":
                        total_adjustment += 1.5  # Default +1.5pp for policy

            # Apply adjustment
            if adjustment_method == "additive":
                adjusted_forecast.at[idx, "forecast"] = base_value + total_adjustment
            elif adjustment_method == "multiplicative":
                adjusted_forecast.at[idx, "forecast"] = base_value * (
                    1 + total_adjustment / 100
                )

            # Recalculate bounds with increased uncertainty
            original_margin = (row["upper_bound"] - row["lower_bound"]) / 2
            # Event uncertainty adds to margin
            event_uncertainty = abs(total_adjustment) * 0.5
            new_margin = np.sqrt(original_margin**2 + event_uncertainty**2)

            adjusted_forecast.at[idx, "lower_bound"] = (
                adjusted_forecast.at[idx, "forecast"] - new_margin
            )
            adjusted_forecast.at[idx, "upper_bound"] = (
                adjusted_forecast.at[idx, "forecast"] + new_margin
            )

        # Ensure valid range
        adjusted_forecast["forecast"] = adjusted_forecast["forecast"].clip(0, 100)
        adjusted_forecast["lower_bound"] = adjusted_forecast["lower_bound"].clip(0, 100)
        adjusted_forecast["upper_bound"] = adjusted_forecast["upper_bound"].clip(0, 100)

        return adjusted_forecast

    def generate_scenarios(
        self,
        indicator_code: str,
        forecast_years: List[int],
        scenario_assumptions: Optional[Dict] = None,
    ) -> pd.DataFrame:
        """
        Generate optimistic, base, and pessimistic scenario forecasts.

        Args:
            indicator_code: Indicator to forecast
            forecast_years: Years to forecast
            scenario_assumptions: Optional dict with scenario parameters

        Returns:
            DataFrame with scenarios for each year
        """
        # Fit base model
        base_model = self.fit_trend_model(indicator_code, trend_type="linear")
        base_forecast = self.forecast_trend(base_model, forecast_years)

        # Default scenario assumptions
        if scenario_assumptions is None:
            scenario_assumptions = {
                "optimistic_multiplier": 1.3,  # 30% better growth
                "pessimistic_multiplier": 0.7,  # 30% slower growth
                "base_multiplier": 1.0,
            }

        # Calculate growth rate from base model
        coeffs = base_model["coefficients"]
        base_growth = coeffs[0] if len(coeffs) > 0 else 0

        # Generate scenarios by adjusting growth rate
        scenarios = []

        for scenario_name, multiplier in [
            ("optimistic", scenario_assumptions["optimistic_multiplier"]),
            ("base", scenario_assumptions["base_multiplier"]),
            ("pessimistic", scenario_assumptions["pessimistic_multiplier"]),
        ]:
            # Adjust coefficients
            adjusted_coeffs = coeffs.copy()
            adjusted_coeffs[0] = coeffs[0] * multiplier

            # Create adjusted model
            adjusted_model = base_model.copy()
            adjusted_model["coefficients"] = adjusted_coeffs

            # Generate forecast
            scenario_forecast = self.forecast_trend(adjusted_model, forecast_years)
            scenario_forecast["scenario"] = scenario_name

            scenarios.append(scenario_forecast)

        result = pd.concat(scenarios, ignore_index=True)

        return result

    def forecast_with_uncertainty(
        self,
        indicator_code: str,
        forecast_years: List[int],
        methods: Optional[List[str]] = None,
    ) -> Dict:
        """
        Generate comprehensive forecast with multiple methods and uncertainty quantification.

        Args:
            indicator_code: Indicator to forecast
            forecast_years: Years to forecast
            methods: List of methods to use ['trend', 'event_augmented', 'scenarios']

        Returns:
            Dictionary with forecasts from each method and combined results
        """
        if methods is None:
            methods = ["trend", "scenarios"]

        results = {
            "indicator_code": indicator_code,
            "forecast_years": forecast_years,
            "methods": {},
        }

        # Trend-based forecast
        if "trend" in methods:
            try:
                trend_model = self.fit_trend_model(indicator_code, trend_type="linear")
                trend_forecast = self.forecast_trend(trend_model, forecast_years)
                results["methods"]["trend"] = {
                    "model_info": trend_model,
                    "forecast": trend_forecast,
                }
            except Exception as e:
                warnings.warn(f"Trend forecast failed: {str(e)}")

        # Event-augmented forecast
        if "event_augmented" in methods and self.events_data is not None:
            try:
                base_model = self.fit_trend_model(indicator_code, trend_type="linear")
                base_forecast = self.forecast_trend(base_model, forecast_years)

                # Get future events
                future_events = self.events_data[
                    self.events_data["event_date"].dt.year >= forecast_years[0]
                ]

                event_forecast = self.apply_event_adjustments(
                    base_forecast, future_events
                )
                results["methods"]["event_augmented"] = {
                    "forecast": event_forecast,
                    "n_events": len(future_events),
                }
            except Exception as e:
                warnings.warn(f"Event-augmented forecast failed: {str(e)}")

        # Scenario analysis
        if "scenarios" in methods:
            try:
                scenario_forecast = self.generate_scenarios(
                    indicator_code, forecast_years
                )
                results["methods"]["scenarios"] = {"forecast": scenario_forecast}
            except Exception as e:
                warnings.warn(f"Scenario forecast failed: {str(e)}")

        # Store results
        self.forecast_results[indicator_code] = results

        return results

    def get_forecast_summary(self, indicator_code: str) -> Optional[pd.DataFrame]:
        """
        Get summary of forecasts for an indicator.

        Args:
            indicator_code: Indicator to summarize

        Returns:
            DataFrame with summary statistics across methods, or None if not forecasted
        """
        if indicator_code not in self.forecast_results:
            return None

        results = self.forecast_results[indicator_code]
        summaries = []

        for method_name, method_data in results["methods"].items():
            forecast_df = method_data["forecast"]

            if method_name == "scenarios":
                # Summarize scenarios
                for year in results["forecast_years"]:
                    year_data = forecast_df[forecast_df["year"] == year]
                    summary = {
                        "year": year,
                        "indicator_code": indicator_code,
                        "method": method_name,
                        "forecast_mean": year_data["forecast"].mean(),
                        "forecast_min": year_data["forecast"].min(),
                        "forecast_max": year_data["forecast"].max(),
                        "lower_bound": year_data["lower_bound"].mean(),
                        "upper_bound": year_data["upper_bound"].mean(),
                    }
                    summaries.append(summary)
            else:
                # Regular forecast
                for _, row in forecast_df.iterrows():
                    summary = {
                        "year": row["year"],
                        "indicator_code": indicator_code,
                        "method": method_name,
                        "forecast_mean": row["forecast"],
                        "forecast_min": row["lower_bound"],
                        "forecast_max": row["upper_bound"],
                        "lower_bound": row["lower_bound"],
                        "upper_bound": row["upper_bound"],
                    }
                    summaries.append(summary)

        return pd.DataFrame(summaries)

    def export_forecasts(self, output_dir: str = "models/") -> Dict[str, str]:
        """
        Export forecast results to CSV files.

        Args:
            output_dir: Directory to save forecast files

        Returns:
            Dictionary mapping indicator codes to output file paths
        """
        import os

        os.makedirs(output_dir, exist_ok=True)

        output_files = {}

        for indicator_code, results in self.forecast_results.items():
            # Export summary
            summary_df = self.get_forecast_summary(indicator_code)
            if summary_df is not None:
                filename = f"{indicator_code}_forecast_summary.csv"
                filepath = os.path.join(output_dir, filename)
                summary_df.to_csv(filepath, index=False)
                output_files[indicator_code] = filepath

            # Export detailed results for each method
            for method_name, method_data in results["methods"].items():
                forecast_df = method_data["forecast"]
                filename = f"{indicator_code}_{method_name}_forecast.csv"
                filepath = os.path.join(output_dir, filename)
                forecast_df.to_csv(filepath, index=False)

        return output_files
