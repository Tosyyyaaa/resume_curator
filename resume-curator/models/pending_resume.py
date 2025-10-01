"""PendingResume data model for page-constrained resume generation.

This module provides the PendingResume class which aggregates all resume
components and ensures the resume fits within specified page limits.
"""

from dataclasses import dataclass
from typing import Any

from models.extracted_education import ExtractedEducation
from models.extracted_experience import ExtractedJobExperience
from models.extracted_project import ExtractedProject
from models.extracted_skills import ExtractedSkills
from models.line_metrics import LineMetrics
from models.resume_header import ResumeHeader


@dataclass
class PendingResume:
    """Container for all resume components with page-fitting logic.

    Attributes:
        header: Resume header with personal information
        experiences: List of job experiences (work, internships, competitions)
        education: List of education entries
        projects: List of projects
        skills: Skills section
        line_length: Total number of lines in the resume
        permitted_line_length: Maximum allowed line length based on page limit
    """

    header: ResumeHeader
    experiences: list[ExtractedJobExperience]
    education: list[ExtractedEducation]
    projects: list[ExtractedProject]
    skills: ExtractedSkills
    permitted_line_length: int
    line_length: int = 0

    def __post_init__(self) -> None:
        """Calculate total line length after initialization."""
        self.line_length = self.calculate_total_line_length()

    def calculate_total_line_length(self) -> int:
        """Calculate total number of lines for entire resume.

        Sums line lengths of all components:
            - Header
            - All experiences
            - All education entries
            - All projects
            - Skills section

        Returns:
            Total line count for the resume
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

        # Add skills
        total += self.skills.line_length

        return total

    def fits_page_limit(self) -> bool:
        """Check if resume fits within permitted line length.

        Returns:
            True if resume fits, False if it exceeds the limit
        """
        return self.line_length <= self.permitted_line_length

    def optimize_to_fit(self) -> None:
        """Optimize resume content to fit within permitted line length.

        Applies trimming in priority order:
            1. Trim project descriptions (least critical)
            2. Remove projects entirely if needed
            3. Trim experience description bullets (more critical)

        Note:
            - Education and header are never modified (static content)
            - Always keeps at least 1 bullet per experience
            - Modifies components in place
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
                self.line_length = self.calculate_total_line_length()

        # Phase 2: Remove projects from end
        while self.projects and not self.fits_page_limit():
            self.projects.pop()
            self.line_length = self.calculate_total_line_length()

        # Phase 3: Trim experience bullets
        for experience in self.experiences:
            if self.fits_page_limit():
                break

            # Calculate how many lines we need to save
            lines_over = self.line_length - self.permitted_line_length

            # Try to trim this experience to save lines
            target_lines = max(2, experience.line_length - lines_over)
            experience.trim_to_lines(target_lines)
            self.line_length = self.calculate_total_line_length()

    def to_dict(self) -> dict[str, Any]:
        """Convert PendingResume to dictionary for JSON serialization.

        Returns:
            Dictionary representation with all resume components and metadata
        """
        return {
            "header": self.header.to_dict(),
            "experiences": [exp.to_dict() for exp in self.experiences],
            "education": [edu.to_dict() for edu in self.education],
            "projects": [proj.to_dict() for proj in self.projects],
            "skills": self.skills.to_dict(),
            "metadata": {
                "line_length": self.line_length,
                "permitted_line_length": self.permitted_line_length,
                "page_limit": self.permitted_line_length
                // LineMetrics.LINES_PER_PAGE,  # Calculate pages from lines
                "fits_page_limit": self.fits_page_limit(),
            },
        }

    @classmethod
    def with_page_limit(
        cls,
        header: ResumeHeader,
        experiences: list[ExtractedJobExperience],
        education: list[ExtractedEducation],
        projects: list[ExtractedProject],
        skills: ExtractedSkills,
        page_limit: int,
    ) -> "PendingResume":
        """Create PendingResume with page limit converted to line length.

        Args:
            header: Resume header
            experiences: List of job experiences
            education: List of education entries
            projects: List of projects
            skills: Skills section
            page_limit: Number of pages allowed

        Returns:
            PendingResume instance with permitted_line_length set from page_limit
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
