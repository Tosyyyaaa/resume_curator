"""Extracted job experience data model with line length calculation.

This module provides the ExtractedJobExperience class for representing work
experiences, internships, and competitions with line-length awareness and
trimming capabilities for page fitting.
"""

from dataclasses import dataclass, field
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
        location: Location of the job (optional)
        description_bullets: List of achievement/responsibility bullet points
        line_length: Number of lines this entry occupies (1 + bullet lines)
        relevance_score: Score indicating relevance to job requirements (default 0)
    """

    company: str
    title: str
    start_date: str
    end_date: str
    location: str | None = None
    description_bullets: list[str] = field(default_factory=list)
    line_length: int = 0
    relevance_score: int = 0

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

    def has_long_bullets(self, max_chars_per_bullet: int = 80) -> bool:
        """Check if any bullets exceed the character limit.

        Args:
            max_chars_per_bullet: Maximum characters per bullet point

        Returns:
            True if any bullet exceeds the limit
        """
        return any(len(bullet) > max_chars_per_bullet for bullet in self.description_bullets)

    def optimize_bullets_with_llm(self, max_chars_per_bullet: int = 80) -> None:
        """Optimize bullets using LLM to compress and rank by importance.

        Uses Gemini to:
        - Compress long bullets to fit character limit
        - Split bullets if needed to preserve information
        - Rank bullets by importance

        Args:
            max_chars_per_bullet: Maximum characters per bullet point

        Note:
            This method modifies description_bullets in place
        """
        if not self.description_bullets:
            return

        # Only optimize if there are long bullets
        if not self.has_long_bullets(max_chars_per_bullet):
            return

        from utils.bullet_optimizer import optimize_experience_bullets

        try:
            print(f"  Optimizing {len(self.description_bullets)} bullets for {self.company}...")
            optimized = optimize_experience_bullets(
                self.description_bullets, max_chars_per_bullet
            )
            self.description_bullets = optimized
            self.line_length = self.calculate_line_length()
        except Exception as e:
            print(f"Warning: Failed to optimize bullets with LLM: {e}")
            # Keep original bullets on failure

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
            "location": self.location,
            "description_bullets": self.description_bullets,
            "line_length": self.line_length,
            "relevance_score": self.relevance_score,
        }

    @classmethod
    def from_experience_dict(
        cls,
        data: dict[str, Any],
        is_competition: bool = False,
        relevance_score: int = 0,
    ) -> "ExtractedJobExperience":
        """Create ExtractedJobExperience from experience dictionary.

        Args:
            data: Dictionary containing experience information
            is_competition: If True, uses "name" field for company and sets
                          title to "Competition"
            relevance_score: Relevance score for this experience (default 0)

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
        description = data.get("description", [])

        # Handle both list and string formats for backward compatibility
        if isinstance(description, str):
            # Legacy format: string with newlines
            bullets = [
                bullet.strip()
                for bullet in description.split("\n")
                if bullet.strip()
            ]
        elif isinstance(description, list):
            # New format: already a list of bullet points
            bullets = [bullet.strip() for bullet in description if bullet.strip()]
        else:
            bullets = []

        # Validate: must have at least one bullet point
        if not bullets:
            raise ValueError(
                f"Experience entry for '{company}' - '{title}' must have at least one description bullet point"
            )

        return cls(
            company=company,
            title=title,
            start_date=data["start_date"],
            end_date=data["end_date"],
            location=data.get("location"),
            description_bullets=bullets,
            relevance_score=relevance_score,
        )

    @classmethod
    def from_experience_dict_with_score(
        cls, data: dict[str, Any], job_description: Any, is_competition: bool = False
    ) -> "ExtractedJobExperience":
        """Create ExtractedJobExperience with calculated relevance score.

        Args:
            data: Dictionary containing experience information
            job_description: Job description object with requirements
            is_competition: If True, uses "name" field for company

        Returns:
            ExtractedJobExperience instance with calculated relevance_score
        """
        from models.relevance_scorer import calculate_experience_score

        score = calculate_experience_score(data, job_description)
        return cls.from_experience_dict(
            data, is_competition=is_competition, relevance_score=score
        )
