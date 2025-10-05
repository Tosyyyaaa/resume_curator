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
        relevance_score: Score indicating relevance to job requirements (default 0)
    """

    name: str
    description: str
    start_date: str
    end_date: str
    line_length: int = 0
    relevance_score: int = 0

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

    def has_long_description(self, max_chars: int = 80) -> bool:
        """Check if description exceeds the character limit.

        Args:
            max_chars: Maximum characters for description

        Returns:
            True if description exceeds the limit
        """
        return len(self.description) > max_chars

    def optimize_description_with_llm(self, max_chars: int = 80) -> None:
        """Optimize project description using LLM.

        Uses Gemini to compress the description to fit character limit while
        maintaining professionalism and key information.

        Args:
            max_chars: Maximum characters for description

        Note:
            This method modifies description in place and recalculates line_length
        """
        if not self.description or len(self.description) <= max_chars:
            return

        from utils.bullet_optimizer import BulletOptimizer

        try:
            print(f"  Optimizing description for {self.name}...")
            optimizer = BulletOptimizer()
            # Treat project description as a single bullet
            optimized = optimizer.optimize_bullets([self.description], max_chars)

            if optimized and optimized[0]:
                self.description = optimized[0]
                self.line_length = self.calculate_line_length()
        except Exception as e:
            print(f"Warning: Failed to optimize description with LLM: {e}")
            # Fall back to simple truncation
            self.trim_description(max_chars)

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
            "relevance_score": self.relevance_score,
        }

    @classmethod
    def from_project_dict(
        cls, data: dict[str, Any], relevance_score: int = 0
    ) -> "ExtractedProject":
        """Create ExtractedProject from project dictionary.

        Args:
            data: Dictionary containing project information
            relevance_score: Relevance score for this project (default 0)

        Returns:
            ExtractedProject instance

        Raises:
            KeyError: If required fields (name, start_date, end_date) are missing
        """
        # Parse description - handle both list and string formats
        description = data.get("description", "")

        if isinstance(description, list):
            # New format: list of description items, join into single string
            description = " ".join(desc.strip() for desc in description if desc.strip())
        elif isinstance(description, str):
            # Legacy format: already a string
            description = description.strip()
        else:
            description = ""

        # Validate: must have a description
        if not description:
            raise ValueError(
                f"Project '{data.get('name', 'Unknown')}' must have at least one line of description"
            )

        return cls(
            name=data["name"],
            description=description,
            start_date=data["start_date"],
            end_date=data["end_date"],
            relevance_score=relevance_score,
        )

    @classmethod
    def from_project_dict_with_score(
        cls, data: dict[str, Any], job_description: Any
    ) -> "ExtractedProject":
        """Create ExtractedProject with calculated relevance score.

        Args:
            data: Dictionary containing project information
            job_description: Job description object with requirements

        Returns:
            ExtractedProject instance with calculated relevance_score
        """
        from models.relevance_scorer import calculate_project_score

        score = calculate_project_score(data, job_description)
        return cls.from_project_dict(data, relevance_score=score)
