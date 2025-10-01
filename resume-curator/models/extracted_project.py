"""Extracted project data model with line length calculation.

This module provides the ExtractedProject class for representing personal or
academic projects with line-length awareness and trimming capabilities.
"""

from dataclasses import dataclass
from typing import Any

from models.line_metrics import LineMetrics


@dataclass
class ExtractedProject:
    """Project entry with dynamic line length.

    Attributes:
        name: Project name
        description: Project description
        start_date: Start year or date
        end_date: End year, date, or "Present"
        line_length: Number of lines this entry occupies
    """

    name: str
    description: str
    start_date: str
    end_date: str
    line_length: int = 0

    def __post_init__(self) -> None:
        """Calculate line length after initialization."""
        self.line_length = self.calculate_line_length()

    def calculate_line_length(self) -> int:
        """Calculate number of lines needed for project entry.

        Project format:
            Line 1: Project Name | Start - End
            Lines 2+ (optional): Description text (if present)

        Returns:
            Number of lines (1 for name + description line count)
        """
        lines = 1  # Name and dates line

        # Add lines for description if present
        if self.description:
            description_lines = LineMetrics.calculate_text_lines(self.description)
            lines += description_lines

        return lines

    def trim_description(self, max_chars: int) -> None:
        """Trim project description to fit character limit.

        Truncates description and appends ellipsis (...) if needed.

        Args:
            max_chars: Maximum characters allowed for description

        Note:
            This method modifies description in place and recalculates line_length
        """
        if len(self.description) <= max_chars:
            return  # Already fits

        # Trim and add ellipsis
        if max_chars > 3:
            self.description = self.description[: max_chars - 3] + "..."
        else:
            self.description = "..."[:max_chars]

        # Recalculate line length
        self.line_length = self.calculate_line_length()

    def to_dict(self) -> dict[str, Any]:
        """Convert ExtractedProject to dictionary.

        Returns:
            Dictionary representation with all fields
        """
        return {
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "line_length": self.line_length,
        }

    @classmethod
    def from_project_dict(cls, data: dict[str, Any]) -> "ExtractedProject":
        """Create ExtractedProject from project dictionary.

        Args:
            data: Dictionary containing project information

        Returns:
            ExtractedProject instance

        Raises:
            KeyError: If required fields (name, start_date, end_date) are missing
        """
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            start_date=data["start_date"],
            end_date=data["end_date"],
        )
