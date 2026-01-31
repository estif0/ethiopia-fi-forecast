"""
Data Loader Module for Ethiopia Financial Inclusion Project.

This module provides the DataLoader class for loading and validating
the unified financial inclusion dataset and reference codes.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List


class DataLoader:
    """Load and validate Ethiopia financial inclusion data.

    This class handles loading the unified dataset and reference codes,
    with built-in schema validation to ensure data quality.

    Attributes:
        data_dir: Path to the data directory.
        unified_data: Loaded unified dataset (observations, events, impact_links, targets).
        reference_codes: Loaded reference codes for categorical fields.
    """

    def __init__(self, data_dir: str = "data/raw"):
        """Initialize DataLoader with data directory path.

        Args:
            data_dir: Path to directory containing raw data files.
        """
        self.data_dir = Path(data_dir)
        self.unified_data: Optional[pd.DataFrame] = None
        self.reference_codes: Optional[pd.DataFrame] = None

    def load_unified_data(
        self, filename: str = "ethiopia_fi_unified_data.csv"
    ) -> pd.DataFrame:
        """Load the unified financial inclusion dataset.

        The unified dataset contains observations, events, impact_links, and targets
        all in a single schema differentiated by the record_type field.

        Args:
            filename: Name of the unified data CSV file.

        Returns:
            DataFrame containing the unified dataset.

        Raises:
            FileNotFoundError: If the data file doesn't exist.
            ValueError: If required columns are missing.
        """
        filepath = self.data_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(
                f"Data file not found: {filepath}\n"
                f"Please ensure the file exists in {self.data_dir}"
            )

        # Load the data
        df = pd.read_csv(filepath)

        # Validate schema
        self._validate_unified_schema(df)

        # Convert date columns to datetime
        date_columns = ["observation_date", "event_date", "collection_date"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        self.unified_data = df
        print(f"✓ Loaded {len(df)} records from {filename}")
        print(f"  Record types: {df['record_type'].value_counts().to_dict()}")

        return df

    def load_reference_codes(
        self, filename: str = "reference_codes.csv"
    ) -> pd.DataFrame:
        """Load reference codes for categorical field validation.

        Args:
            filename: Name of the reference codes CSV file.

        Returns:
            DataFrame containing valid values for categorical fields.

        Raises:
            FileNotFoundError: If the reference codes file doesn't exist.
        """
        filepath = self.data_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(
                f"Reference codes file not found: {filepath}\n"
                f"Please ensure the file exists in {self.data_dir}"
            )

        df = pd.read_csv(filepath)
        self.reference_codes = df
        print(f"✓ Loaded {len(df)} reference codes from {filename}")

        return df

    def _validate_unified_schema(self, df: pd.DataFrame) -> None:
        """Validate that the unified dataset has required columns.

        Args:
            df: DataFrame to validate.

        Raises:
            ValueError: If required columns are missing.
        """
        # Core columns that must exist
        required_columns = ["record_id", "record_type"]

        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}\n"
                f"Available columns: {list(df.columns)}"
            )

        # Validate record_type values
        valid_record_types = ["observation", "event", "impact_link", "target"]
        invalid_types = set(df["record_type"].unique()) - set(valid_record_types)

        if invalid_types:
            raise ValueError(
                f"Invalid record_type values found: {invalid_types}\n"
                f"Valid types are: {valid_record_types}"
            )

    def validate_schema(self) -> Dict[str, any]:  # type: ignore
        """Perform comprehensive schema validation on loaded data.

        Returns:
            Dictionary containing validation results and statistics.

        Raises:
            RuntimeError: If data hasn't been loaded yet.
        """
        if self.unified_data is None:
            raise RuntimeError("No data loaded. Call load_unified_data() first.")

        df = self.unified_data
        validation_results = {
            "total_records": len(df),
            "record_type_counts": df["record_type"].value_counts().to_dict(),
            "columns": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "date_range": {},
        }

        # Check date ranges for each record type
        for record_type in df["record_type"].unique():
            subset = df[df["record_type"] == record_type]

            if record_type == "observation" and "observation_date" in df.columns:
                dates = subset["observation_date"].dropna()
                if len(dates) > 0:
                    validation_results["date_range"][record_type] = {
                        "min": dates.min(),
                        "max": dates.max(),
                        "count": len(dates),
                    }

            elif record_type == "event" and "event_date" in df.columns:
                dates = subset["event_date"].dropna()
                if len(dates) > 0:
                    validation_results["date_range"][record_type] = {
                        "min": dates.min(),
                        "max": dates.max(),
                        "count": len(dates),
                    }

        return validation_results

    def get_records_by_type(self, record_type: str) -> pd.DataFrame:
        """Filter unified data by record type.

        Args:
            record_type: Type of records to retrieve
                        ('observation', 'event', 'impact_link', 'target').

        Returns:
            DataFrame containing only records of the specified type.

        Raises:
            RuntimeError: If data hasn't been loaded yet.
            ValueError: If record_type is invalid.
        """
        if self.unified_data is None:
            raise RuntimeError("No data loaded. Call load_unified_data() first.")

        valid_types = ["observation", "event", "impact_link", "target"]
        if record_type not in valid_types:
            raise ValueError(
                f"Invalid record_type: {record_type}. "
                f"Valid types are: {valid_types}"
            )

        return self.unified_data[self.unified_data["record_type"] == record_type].copy()

    def get_indicators(self) -> List[str]:
        """Get list of unique indicators from observations.

        Returns:
            List of unique indicator codes.

        Raises:
            RuntimeError: If data hasn't been loaded yet.
        """
        if self.unified_data is None:
            raise RuntimeError("No data loaded. Call load_unified_data() first.")

        observations = self.get_records_by_type("observation")

        if "indicator_code" not in observations.columns:
            return []

        return sorted(observations["indicator_code"].dropna().unique().tolist())

    def summary(self) -> None:
        """Print a comprehensive summary of the loaded data."""
        if self.unified_data is None:
            print("No data loaded yet.")
            return

        print("\n" + "=" * 60)
        print("ETHIOPIA FINANCIAL INCLUSION DATASET SUMMARY")
        print("=" * 60)

        df = self.unified_data

        print(f"\nTotal Records: {len(df)}")
        print(f"\nRecord Type Distribution:")
        for record_type, count in df["record_type"].value_counts().items():
            print(f"  - {record_type}: {count}")

        # Observations summary
        obs = self.get_records_by_type("observation")
        if len(obs) > 0:
            print(f"\nObservations:")
            print(f"  - Count: {len(obs)}")
            if "indicator_code" in obs.columns:
                print(f"  - Unique Indicators: {obs['indicator_code'].nunique()}")
            if "observation_date" in obs.columns:
                dates = obs["observation_date"].dropna()
                if len(dates) > 0:
                    print(
                        f"  - Date Range: {dates.min().date()} to {dates.max().date()}"
                    )

        # Events summary
        events = self.get_records_by_type("event")
        if len(events) > 0:
            print(f"\nEvents:")
            print(f"  - Count: {len(events)}")
            if "category" in events.columns:
                print(f"  - Categories: {events['category'].value_counts().to_dict()}")

        # Impact links summary
        impact_links = self.get_records_by_type("impact_link")
        if len(impact_links) > 0:
            print(f"\nImpact Links:")
            print(f"  - Count: {len(impact_links)}")

        # Data quality
        print(f"\nData Quality:")
        if "confidence" in df.columns:
            print(f"  - Confidence Levels: {df['confidence'].value_counts().to_dict()}")

        print("\n" + "=" * 60)
