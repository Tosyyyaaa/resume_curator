"""Extracted skills data model with line length calculation.

This module provides the ExtractedSkills class for representing technical skills
with line-length awareness for page fitting.
"""

from dataclasses import dataclass
from typing import Any

from models.line_metrics import LineMetrics


@dataclass
class ExtractedSkills:
    """Skills section with line length awareness.

    Attributes:
        programming_languages: List of programming languages
        frameworks: List of frameworks and libraries
        tools: List of tools and technologies
        line_length: Number of lines this section occupies
    """

    programming_languages: list[str]
    frameworks: list[str]
    tools: list[str]
    line_length: int = 0

    def __post_init__(self) -> None:
        """Calculate line length after initialization."""
        self.line_length = self.calculate_line_length()

    def calculate_line_length(self) -> int:
        """Calculate number of lines needed for skills section.

        Skills format:
            Line 1 (if present): Programming Languages: Lang1, Lang2, ...
            Line 2 (if present): Frameworks: Framework1, Framework2, ...
            Line 3 (if present): Tools: Tool1, Tool2, ...

        Each line may wrap to multiple lines if skill list is long.

        Returns:
            Number of lines needed for all skill categories
        """
        lines = 0

        # Programming languages line(s)
        if self.programming_languages:
            lang_text = "Programming Languages: " + ", ".join(
                self.programming_languages
            )
            lines += LineMetrics.calculate_text_lines(lang_text)

        # Frameworks line(s)
        if self.frameworks:
            framework_text = "Frameworks: " + ", ".join(self.frameworks)
            lines += LineMetrics.calculate_text_lines(framework_text)

        # Tools line(s)
        if self.tools:
            tools_text = "Tools: " + ", ".join(self.tools)
            lines += LineMetrics.calculate_text_lines(tools_text)

        return lines

    def to_dict(self) -> dict[str, Any]:
        """Convert ExtractedSkills to dictionary.

        Returns:
            Dictionary representation with all fields
        """
        return {
            "programming_languages": self.programming_languages,
            "frameworks": self.frameworks,
            "tools": self.tools,
            "line_length": self.line_length,
        }

    @classmethod
    def from_lists(
        cls,
        programming_languages: list[str] | None,
        frameworks: list[str] | None,
        tools: list[str] | None,
    ) -> "ExtractedSkills":
        """Create ExtractedSkills from skill lists.

        Args:
            programming_languages: List of programming languages (or None)
            frameworks: List of frameworks (or None)
            tools: List of tools (or None)

        Returns:
            ExtractedSkills instance with None values converted to empty lists
        """
        return cls(
            programming_languages=programming_languages or [],
            frameworks=frameworks or [],
            tools=tools or [],
        )
