"""Abstract base class for template-aware resume generation.

This module provides the BaseResume abstract class that all template-specific
resume implementations must inherit from. Each template has unique character
limits and optimization strategies.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from models.extracted_education import ExtractedEducation
from models.extracted_experience import ExtractedJobExperience
from models.extracted_project import ExtractedProject
from models.extracted_skills import ExtractedSkills
from models.resume_header import ResumeHeader


@dataclass
class BaseResume(ABC):
    """Abstract base class for template-aware resumes.

    Each template (bengt, deedy, etc.) must implement this interface to provide
    template-specific character limits, line calculations, and optimization logic.

    Attributes:
        header: Resume header with personal information
        experiences: List of job experiences (work, internships, competitions)
        education: List of education entries
        projects: List of projects
        skills: Skills section
    """

    header: ResumeHeader
    experiences: list[ExtractedJobExperience]
    education: list[ExtractedEducation]
    projects: list[ExtractedProject]
    skills: ExtractedSkills

    @property
    @abstractmethod
    def template_name(self) -> str:
        """Return the template identifier (e.g., 'bengt', 'deedy').

        Returns:
            Template name string used to locate template files
        """
        pass

    @property
    def template_schema_path(self) -> Path:
        """Get path to template schema JSON file.

        Returns:
            Path to template_schema.json for this template
        """
        return (
            Path(__file__).parent.parent
            / "templates"
            / "latex"
            / self.template_name
            / "template_schema.json"
        )

    @property
    def template_schema(self) -> dict[str, Any]:
        """Load and return the template schema.

        Returns:
            Dictionary containing template schema with metadata and examples

        Raises:
            FileNotFoundError: If template schema file doesn't exist
            json.JSONDecodeError: If schema file contains invalid JSON
        """
        with open(self.template_schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @property
    @abstractmethod
    def char_limits(self) -> dict[str, Any]:
        """Extract character limits from template schema metadata.

        Returns:
            Dictionary containing character limits for various sections
            (e.g., experience_bullets, skills, projects)
        """
        pass

    @property
    @abstractmethod
    def line_length(self) -> int:
        """Calculate current total line length for the resume.

        Returns:
            Total number of lines in the resume
        """
        pass

    @property
    @abstractmethod
    def permitted_line_length(self) -> int:
        """Get maximum permitted line length for this resume.

        Returns:
            Maximum allowed line count based on page limit
        """
        pass

    @abstractmethod
    def calculate_total_line_length(self) -> int:
        """Calculate total number of lines using template-specific rules.

        Different templates have different character limits per line, affecting
        how many lines each section occupies.

        Returns:
            Total line count for the entire resume
        """
        pass

    def fits_page_limit(self) -> bool:
        """Check if resume fits within permitted line length.

        Returns:
            True if resume fits, False if it exceeds the limit
        """
        return self.line_length <= self.permitted_line_length

    @abstractmethod
    def optimize_to_fit(self) -> None:
        """Optimize resume content to fit within permitted line length.

        Template-specific optimization strategy. Different templates may:
        - Trim in different priority orders
        - Have different constraints (e.g., two-column balancing)
        - Apply different trimming strategies

        Modifies resume components in place.
        """
        pass

    def to_dict(self) -> dict[str, Any]:
        """Convert resume to dictionary for JSON serialization.

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
                "template_name": self.template_name,
                "line_length": self.line_length,
                "permitted_line_length": self.permitted_line_length,
                "fits_page_limit": self.fits_page_limit(),
            },
        }
