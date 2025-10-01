"""Extracted job experience data model with line length calculation.

This module provides the ExtractedJobExperience class for representing work
experiences, internships, and competitions with line-length awareness and
trimming capabilities for page fitting.
"""

from dataclasses import dataclass
from typing import Any

from models.line_metrics import LineMetrics


@dataclass
class ExtractedJobExperience:
    """Job experience entry with dynamic line length.

    Attributes:
        company: Company or organization name
        title: Job title or position
        start_date: Start year or date
        end_date: End year, date, or "Present"
        description_bullets: List of achievement/responsibility bullet points
        line_length: Number of lines this entry occupies (1 + bullet lines)
    """

    company: str
    title: str
    start_date: str
    end_date: str
    description_bullets: list[str]
    line_length: int = 0

    def __post_init__(self) -> None:
        """Calculate line length after initialization."""
        self.line_length = self.calculate_line_length()

    def calculate_line_length(self) -> int:
        """Calculate number of lines needed for experience entry.

        Experience format:
            Line 1: Title at Company | Start - End
            Lines 2+: Bullet points (each bullet may span multiple lines)

        Returns:
            Number of lines (1 for title + sum of bullet line counts)
        """
        lines = 1  # Title line

        # Add lines for each bullet point
        for bullet in self.description_bullets:
            bullet_lines = LineMetrics.calculate_text_lines(bullet)
            lines += bullet_lines

        return lines

    def trim_to_lines(self, max_lines: int) -> None:
        """Trim description bullets to fit within line limit.

        Removes bullets from the end until the entry fits within max_lines.
        Always keeps at least the title line.

        Args:
            max_lines: Maximum number of lines allowed

        Note:
            This method modifies description_bullets in place
        """
        if self.line_length <= max_lines:
            return  # Already fits

        # Remove bullets from the end until we fit
        while len(self.description_bullets) > 0 and self.line_length > max_lines:
            self.description_bullets.pop()
            self.line_length = self.calculate_line_length()

    def to_dict(self) -> dict[str, Any]:
        """Convert ExtractedJobExperience to dictionary.

        Returns:
            Dictionary representation with all fields
        """
        return {
            "company": self.company,
            "title": self.title,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "description_bullets": self.description_bullets,
            "line_length": self.line_length,
        }

    @classmethod
    def from_experience_dict(
        cls, data: dict[str, Any], is_competition: bool = False
    ) -> "ExtractedJobExperience":
        """Create ExtractedJobExperience from experience dictionary.

        Args:
            data: Dictionary containing experience information
            is_competition: If True, uses "name" field for company and sets
                          title to "Competition"

        Returns:
            ExtractedJobExperience instance

        Raises:
            KeyError: If required fields are missing
        """
        # Handle competition vs regular experience
        if is_competition:
            company = data["name"]
            title = "Competition"
        else:
            company = data["company"]
            title = data["title"]

        # Parse description into bullet points
        description = data.get("description", "")
        if description:
            # Split by newlines to create bullet points
            bullets = [
                bullet.strip()
                for bullet in description.split("\n")
                if bullet.strip()
            ]
        else:
            bullets = []

        return cls(
            company=company,
            title=title,
            start_date=data["start_date"],
            end_date=data["end_date"],
            description_bullets=bullets,
        )
