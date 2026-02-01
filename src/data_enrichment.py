"""
Data Enrichment Module for Ethiopia Financial Inclusion Project.

This module provides the DataEnricher class for systematically adding
new observations, events, and impact links to the unified dataset.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional, Any, List
from datetime import datetime


class DataEnricher:
    """Add and validate new records to the unified dataset.

    This class provides methods to systematically add observations, events,
    and impact links while maintaining schema compliance and documentation.

    Attributes:
        unified_data: The unified dataset being enriched.
        enrichment_log: List of all additions made with metadata.
    """

    def __init__(self, unified_data: pd.DataFrame):
        """Initialize DataEnricher with existing unified dataset.

        Args:
            unified_data: Existing unified dataset to be enriched.
        """
        self.unified_data = unified_data.copy()
        self.enrichment_log: List[Dict[str, Any]] = []

    def add_observation(
        self,
        record_id: str,
        pillar: str,
        indicator: str,
        indicator_code: str,
        value_numeric: float,
        observation_date: str,
        source_name: str,
        source_url: str,
        confidence: str,
        collected_by: str,
        original_text: Optional[str] = None,
        notes: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Add a new observation record to the dataset.

        Args:
            record_id: Unique identifier for the record.
            pillar: Financial inclusion pillar (access, usage, quality, barriers).
            indicator: Human-readable indicator name.
            indicator_code: Standard indicator code (e.g., ACC_OWNERSHIP).
            value_numeric: The measured value.
            observation_date: Date of observation (YYYY-MM-DD format).
            source_name: Name of the data source.
            source_url: URL or reference to source.
            confidence: Confidence level (high, medium, low).
            collected_by: Name of person who collected this data.
            original_text: Exact quote or text from source.
            notes: Explanation of why this data is useful.
            **kwargs: Additional fields to include in the record.

        Raises:
            ValueError: If required fields are invalid.
        """
        # Validate inputs
        self._validate_pillar(pillar)
        self._validate_confidence(confidence)
        self._validate_date(observation_date)

        # Create record
        record = {
            "record_id": record_id,
            "record_type": "observation",
            "pillar": pillar,
            "indicator": indicator,
            "indicator_code": indicator_code,
            "value_numeric": value_numeric,
            "observation_date": observation_date,
            "source_name": source_name,
            "source_url": source_url,
            "confidence": confidence,
            "collected_by": collected_by,
            "collection_date": datetime.now().strftime("%Y-%m-%d"),
            "original_text": original_text,
            "notes": notes,
            **kwargs,
        }

        # Add to dataset
        new_row = pd.DataFrame([record])
        self.unified_data = pd.concat([self.unified_data, new_row], ignore_index=True)

        # Log the addition
        self.enrichment_log.append(
            {
                "timestamp": datetime.now().isoformat(),
                "record_type": "observation",
                "record_id": record_id,
                "action": "added",
                "collected_by": collected_by,
            }
        )

        print(f"✓ Added observation: {record_id} - {indicator}")

    def add_event(
        self,
        record_id: str,
        title: str,
        category: str,
        event_date: str,
        source_name: str,
        source_url: str,
        confidence: str,
        collected_by: str,
        description: Optional[str] = None,
        original_text: Optional[str] = None,
        notes: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Add a new event record to the dataset.

        Events should NOT have pillar assigned - their effects on specific
        indicators are captured through impact_link records.

        Args:
            record_id: Unique identifier for the event.
            title: Short title of the event.
            category: Event category (policy, product_launch, infrastructure, milestone).
            event_date: Date of event (YYYY-MM-DD format).
            source_name: Name of the data source.
            source_url: URL or reference to source.
            confidence: Confidence level (high, medium, low).
            collected_by: Name of person who collected this data.
            description: Detailed description of the event.
            original_text: Exact quote or text from source.
            notes: Explanation of why this event is relevant.
            **kwargs: Additional fields to include in the record.

        Raises:
            ValueError: If required fields are invalid.
        """
        # Validate inputs
        self._validate_event_category(category)
        self._validate_confidence(confidence)
        self._validate_date(event_date)

        # Create record (note: pillar is intentionally None for events)
        record = {
            "record_id": record_id,
            "record_type": "event",
            "pillar": None,  # Events don't have pillar - effects captured via impact_links
            "title": title,
            "category": category,
            "event_date": event_date,
            "description": description,
            "source_name": source_name,
            "source_url": source_url,
            "confidence": confidence,
            "collected_by": collected_by,
            "collection_date": datetime.now().strftime("%Y-%m-%d"),
            "original_text": original_text,
            "notes": notes,
            **kwargs,
        }

        # Add to dataset
        new_row = pd.DataFrame([record])
        self.unified_data = pd.concat([self.unified_data, new_row], ignore_index=True)

        # Log the addition
        self.enrichment_log.append(
            {
                "timestamp": datetime.now().isoformat(),
                "record_type": "event",
                "record_id": record_id,
                "action": "added",
                "collected_by": collected_by,
            }
        )

        print(f"✓ Added event: {record_id} - {title}")

    def add_impact_link(
        self,
        record_id: str,
        parent_id: str,
        pillar: str,
        related_indicator: str,
        impact_direction: str,
        impact_magnitude: str,
        lag_months: Optional[int] = None,
        evidence_basis: Optional[str] = None,
        confidence: str = "medium",
        collected_by: str = "",
        notes: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Add a new impact link connecting an event to an indicator.

        Impact links capture the relationship between events and specific
        indicators, including direction, magnitude, and temporal lag.

        Args:
            record_id: Unique identifier for the impact link.
            parent_id: Record ID of the event this links to.
            pillar: Financial inclusion pillar affected.
            related_indicator: Indicator code that is affected.
            impact_direction: Direction of impact (positive, negative, neutral).
            impact_magnitude: Magnitude of impact (high, medium, low, minimal).
            lag_months: Time lag in months before impact is observed.
            evidence_basis: Source of impact estimate (comparable, estimated, observed).
            confidence: Confidence level (high, medium, low).
            collected_by: Name of person who created this link.
            notes: Explanation of the impact relationship.
            **kwargs: Additional fields to include in the record.

        Raises:
            ValueError: If required fields are invalid.
        """
        # Validate inputs
        self._validate_pillar(pillar)
        self._validate_impact_direction(impact_direction)
        self._validate_impact_magnitude(impact_magnitude)
        self._validate_confidence(confidence)

        # Create record
        record = {
            "record_id": record_id,
            "record_type": "impact_link",
            "parent_id": parent_id,
            "pillar": pillar,
            "related_indicator": related_indicator,
            "impact_direction": impact_direction,
            "impact_magnitude": impact_magnitude,
            "lag_months": lag_months,
            "evidence_basis": evidence_basis,
            "confidence": confidence,
            "collected_by": collected_by,
            "collection_date": datetime.now().strftime("%Y-%m-%d"),
            "notes": notes,
            **kwargs,
        }

        # Add to dataset
        new_row = pd.DataFrame([record])
        self.unified_data = pd.concat([self.unified_data, new_row], ignore_index=True)

        # Log the addition
        self.enrichment_log.append(
            {
                "timestamp": datetime.now().isoformat(),
                "record_type": "impact_link",
                "record_id": record_id,
                "parent_id": parent_id,
                "action": "added",
                "collected_by": collected_by,
            }
        )

        print(
            f"✓ Added impact link: {record_id} (Event {parent_id} → {related_indicator})"
        )

    def validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate a record against schema requirements.

        Args:
            record: Dictionary containing record data.

        Returns:
            True if record is valid.

        Raises:
            ValueError: If record is invalid.
        """
        if "record_id" not in record:
            raise ValueError("Record must have 'record_id'")

        if "record_type" not in record:
            raise ValueError("Record must have 'record_type'")

        valid_record_types = ["observation", "event", "impact_link", "target"]
        if record["record_type"] not in valid_record_types:
            raise ValueError(
                f"Invalid record_type: {record['record_type']}. "
                f"Must be one of: {valid_record_types}"
            )

        return True

    def export_enriched_data(self, filepath: str) -> None:
        """Export the enriched dataset to CSV.

        Args:
            filepath: Path where enriched data should be saved.
        """
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.unified_data.to_csv(output_path, index=False)
        print(f"✓ Exported enriched data to: {filepath}")
        print(f"  Total records: {len(self.unified_data)}")

    def export_enrichment_log(self, filepath: str) -> None:
        """Export the enrichment log to markdown file.

        Args:
            filepath: Path where log should be saved.
        """
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write("# Data Enrichment Log\n\n")
            f.write(f"Total additions: {len(self.enrichment_log)}\n\n")

            f.write("## Summary by Record Type\n\n")
            log_df = pd.DataFrame(self.enrichment_log)
            if len(log_df) > 0:
                summary = log_df["record_type"].value_counts()
                for record_type, count in summary.items():
                    f.write(f"- {record_type}: {count}\n")

            f.write("\n## Detailed Log\n\n")
            for entry in self.enrichment_log:
                f.write(f"### {entry['record_id']}\n")
                f.write(f"- **Type**: {entry['record_type']}\n")
                f.write(f"- **Action**: {entry['action']}\n")
                f.write(f"- **Collected by**: {entry['collected_by']}\n")
                f.write(f"- **Timestamp**: {entry['timestamp']}\n")
                if "parent_id" in entry:
                    f.write(f"- **Parent ID**: {entry['parent_id']}\n")
                f.write("\n")

        print(f"✓ Exported enrichment log to: {filepath}")

    def get_enriched_data(self) -> pd.DataFrame:
        """Get the current enriched dataset.

        Returns:
            DataFrame with all original and newly added records.
        """
        return self.unified_data.copy()

    def get_enrichment_summary(self) -> Dict[str, Any]:
        """Get summary statistics about enrichment activities.

        Returns:
            Dictionary with enrichment statistics.
        """
        log_df = (
            pd.DataFrame(self.enrichment_log) if self.enrichment_log else pd.DataFrame()
        )

        summary = {
            "total_additions": len(self.enrichment_log),
            "current_total_records": len(self.unified_data),
            "additions_by_type": (
                log_df["record_type"].value_counts().to_dict()
                if len(log_df) > 0
                else {}
            ),
            "contributors": (
                log_df["collected_by"].unique().tolist() if len(log_df) > 0 else []
            ),
        }

        return summary

    # Validation helper methods

    def _validate_pillar(self, pillar: str) -> None:
        """Validate pillar value."""
        valid_pillars = ["access", "usage", "quality", "barriers"]
        if pillar not in valid_pillars:
            raise ValueError(
                f"Invalid pillar: {pillar}. Must be one of: {valid_pillars}"
            )

    def _validate_confidence(self, confidence: str) -> None:
        """Validate confidence level."""
        valid_confidence = ["high", "medium", "low"]
        if confidence not in valid_confidence:
            raise ValueError(
                f"Invalid confidence: {confidence}. Must be one of: {valid_confidence}"
            )

    def _validate_date(self, date_str: str) -> None:
        """Validate date format."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Must be YYYY-MM-DD")

    def _validate_event_category(self, category: str) -> None:
        """Validate event category."""
        valid_categories = [
            "policy",
            "product_launch",
            "infrastructure",
            "milestone",
            "market_entry",
            "regulation",
            "partnership",
            "economic",
            "pricing",
        ]
        if category not in valid_categories:
            raise ValueError(
                f"Invalid category: {category}. Must be one of: {valid_categories}"
            )

    def _validate_impact_direction(self, direction: str) -> None:
        """Validate impact direction."""
        valid_directions = ["positive", "negative", "neutral"]
        if direction not in valid_directions:
            raise ValueError(
                f"Invalid impact_direction: {direction}. Must be one of: {valid_directions}"
            )

    def _validate_impact_magnitude(self, magnitude: str) -> None:
        """Validate impact magnitude."""
        valid_magnitudes = ["high", "medium", "low", "minimal"]
        if magnitude not in valid_magnitudes:
            raise ValueError(
                f"Invalid impact_magnitude: {magnitude}. Must be one of: {valid_magnitudes}"
            )
