"""Bengt template-specific resume implementation.

This module provides the BengtResume class for the single-column bengt template
with specific character limits and optimization strategies.
"""

from dataclasses import dataclass, field
from typing import Any

from models.base_resume import BaseResume
from models.line_metrics import LineMetrics


@dataclass
class BengtResume(BaseResume):
    """Bengt template resume with single-column layout.

    Character limits for bengt template:
    - Experience bullets: 116 chars/line (can wrap)
    - Projects: 116 chars/line (can wrap)
    - Skills: CANNOT wrap (Languages: 52, Frameworks: 50, Web Dev: 40, Tools: 48)

    Optimization strategy:
    1. Trim project descriptions
    2. Remove projects entirely if needed
    3. Trim experience bullets (keeping at least 1 per experience)

    Attributes:
        permitted_line_length: Maximum allowed line count
        _line_length: Cached line length (calculated on init and after modifications)
    """

    permitted_line_length: int = 0
    _line_length: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        """Calculate total line length after initialization."""
        self._line_length = self.calculate_total_line_length()

    @property
    def template_name(self) -> str:
        """Return template identifier.

        Returns:
            'bengt'
        """
        return "bengt"

    @property
    def char_limits(self) -> dict[str, Any]:
        """Extract character limits from bengt template schema.

        Returns:
            Dictionary with keys:
            - experience_bullets: {chars_per_line: 116, can_wrap: true}
            - projects_description: {chars_per_line: 116, can_wrap: true}
            - skills: {can_wrap: false, languages: 52, frameworks: 50, ...}
        """
        return self.template_schema["_metadata"]["character_limits"]

    @property
    def line_length(self) -> int:
        """Get current total line length.

        Returns:
            Total number of lines in the resume
        """
        return self._line_length

    def calculate_total_line_length(self) -> int:
        """Calculate total number of lines for bengt template.

        Uses bengt-specific character limits:
        - 116 chars/line for experiences and projects
        - Single-line skills (must fit in specified char limits)

        Returns:
            Total line count for the entire resume
        """
        total = self.header.line_length

        # Sum all experiences
        for experience in self.experiences:
            total += experience.line_length

        # Sum all education entries
        for edu in self.education:
            total += edu.line_length

        # Sum all projects
        for project in self.projects:
            total += project.line_length

        # Add skills (bengt uses 2 rows, each row is 1 line)
        total += self.skills.line_length

        return total

    def optimize_to_fit(self) -> None:
        """Optimize resume to fit within permitted line length.

        Bengt-specific optimization strategy:
        1. Phase 1: Trim project descriptions to 80 chars
        2. Phase 2: Remove projects from end (lowest relevance first)
        3. Phase 3: Trim experience bullets (keeping minimum 1 bullet)

        Education and header are never modified (static content).
        Modifies components in place and updates _line_length.
        """
        if self.fits_page_limit():
            return  # Already fits

        # Phase 1: Trim project descriptions
        for project in self.projects:
            if self.fits_page_limit():
                break

            # Try trimming description to 80 chars
            if len(project.description) > 80:
                project.trim_description(80)
                self._line_length = self.calculate_total_line_length()

        # Phase 2: Remove projects from end
        while self.projects and not self.fits_page_limit():
            self.projects.pop()
            self._line_length = self.calculate_total_line_length()

        # Phase 3: Trim experience bullets
        for experience in self.experiences:
            if self.fits_page_limit():
                break

            # Calculate how many lines we need to save
            lines_over = self._line_length - self.permitted_line_length

            # Try to trim this experience to save lines
            target_lines = max(2, experience.line_length - lines_over)
            experience.trim_to_lines(target_lines)
            self._line_length = self.calculate_total_line_length()

    @classmethod
    def with_page_limit(
        cls,
        header,
        experiences,
        education,
        projects,
        skills,
        page_limit: int,
    ) -> "BengtResume":
        """Create BengtResume with page limit converted to line length.

        Args:
            header: Resume header
            experiences: List of job experiences
            education: List of education entries
            projects: List of projects
            skills: Skills section
            page_limit: Number of pages allowed

        Returns:
            BengtResume instance with permitted_line_length set from page_limit
        """
        permitted_line_length = LineMetrics.page_to_lines(page_limit)

        return cls(
            header=header,
            experiences=experiences,
            education=education,
            projects=projects,
            skills=skills,
            permitted_line_length=permitted_line_length,
        )
