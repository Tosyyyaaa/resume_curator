"""Deedy template-specific resume implementation.

This module provides the DeedyResume class for the two-column deedy template
with unique character limits for left and right columns.
"""

from dataclasses import dataclass, field
from typing import Any

from models.base_resume import BaseResume
from models.line_metrics import LineMetrics


@dataclass
class DeedyResume(BaseResume):
    """Deedy template resume with two-column layout.

    Character limits for deedy template:
    - Left column (33% width): 40-45 chars per line
    - Right column (66% width): 95 chars per line (can wrap)

    Left column sections: Education, Links, Coursework, Skills
    Right column sections: Experience, Research, Awards, Publications

    Optimization strategy (two-column specific):
    1. Trim right column content (experience bullets, research descriptions)
    2. Remove projects/awards if present
    3. Balance column heights to avoid overflow

    Attributes:
        permitted_line_length: Maximum allowed line count for tallest column
        _line_length: Cached line length (height of tallest column)
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
            'deedy'
        """
        return "deedy"

    @property
    def char_limits(self) -> dict[str, Any]:
        """Extract character limits from deedy template schema.

        Returns:
            Dictionary with keys:
            - left_column: {width_percentage: 33, skills_per_line: 45, ...}
            - right_column: {width_percentage: 66, experience_bullets: {...}, ...}
            - skills: {can_wrap: true, chars_per_line: 45}
        """
        return self.template_schema["_metadata"]["character_limits"]

    @property
    def line_length(self) -> int:
        """Get current total line length.

        For two-column layout, this is the height of the tallest column.

        Returns:
            Maximum line count between left and right columns
        """
        return self._line_length

    def _calculate_left_column_lines(self) -> int:
        """Calculate line count for left column (Education, Links, Coursework, Skills).

        Returns:
            Total lines in left column
        """
        total = 0

        # Education section
        for edu in self.education:
            total += edu.line_length

        # Links, Coursework, Skills
        # For now, using basic line count
        # TODO: Implement proper left-column character limit calculations
        total += self.skills.line_length

        return total

    def _calculate_right_column_lines(self) -> int:
        """Calculate line count for right column (Experience, Research, Awards, Publications).

        Uses 95 chars/line limit for right column content.

        Returns:
            Total lines in right column
        """
        total = 0

        # Experience section (95 chars per line)
        for experience in self.experiences:
            total += experience.line_length

        # Projects can go in Research section
        for project in self.projects:
            total += project.line_length

        return total

    def calculate_total_line_length(self) -> int:
        """Calculate total number of lines for deedy template.

        For two-column layout, line length is the maximum height between columns.
        Also includes header which spans both columns.

        Returns:
            Header lines + max(left_column_lines, right_column_lines)
        """
        left_lines = self._calculate_left_column_lines()
        right_lines = self._calculate_right_column_lines()

        # Header spans both columns
        header_lines = self.header.line_length

        # Total is header + tallest column
        return header_lines + max(left_lines, right_lines)

    def optimize_to_fit(self) -> None:
        """Optimize resume to fit within permitted line length.

        Deedy-specific optimization strategy:
        1. Phase 1: Trim project descriptions (Research section)
        2. Phase 2: Remove projects from end
        3. Phase 3: Trim experience bullets in right column
        4. Phase 4: Balance columns if needed

        Modifies components in place and updates _line_length.
        """
        if self.fits_page_limit():
            return  # Already fits

        # Phase 1: Trim project descriptions (Research section)
        for project in self.projects:
            if self.fits_page_limit():
                break

            # Trim to 80 chars for right column (95 char limit)
            if len(project.description) > 80:
                project.trim_description(80)
                self._line_length = self.calculate_total_line_length()

        # Phase 2: Remove projects from end
        while self.projects and not self.fits_page_limit():
            self.projects.pop()
            self._line_length = self.calculate_total_line_length()

        # Phase 3: Trim experience bullets (right column)
        for experience in self.experiences:
            if self.fits_page_limit():
                break

            # Calculate lines over limit
            lines_over = self._line_length - self.permitted_line_length

            # Trim experience bullets to save lines
            target_lines = max(2, experience.line_length - lines_over)
            experience.trim_to_lines(target_lines)
            self._line_length = self.calculate_total_line_length()

        # Phase 4: Column balancing
        # If columns are severely imbalanced, may need to redistribute content
        # For now, rely on phases 1-3

    @classmethod
    def with_page_limit(
        cls,
        header,
        experiences,
        education,
        projects,
        skills,
        page_limit: int,
    ) -> "DeedyResume":
        """Create DeedyResume with page limit converted to line length.

        Args:
            header: Resume header
            experiences: List of job experiences
            education: List of education entries
            projects: List of projects (shown in Research section)
            skills: Skills section
            page_limit: Number of pages allowed

        Returns:
            DeedyResume instance with permitted_line_length set from page_limit
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
