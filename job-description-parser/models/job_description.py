"""Data model for job descriptions.

This module provides the JobDescription class for representing parsed job
postings with structured fields including title, location, requirements,
and technical skills.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class JobDescription:
    """Structured representation of a job posting.

    Attributes:
        job_description: Full text description of the job posting
        job_title: Position title
        job_location: Job location (city, country, or 'Remote')
        job_salary: Salary range or 'N/A' if not specified
        job_requirements: List of job requirements and qualifications
        programming_languages: List of required programming languages
        frameworks: List of required frameworks and libraries
        tools: List of required tools and technologies
    """

    job_description: str
    job_title: str
    job_location: str
    job_salary: str
    job_requirements: list[str]
    programming_languages: list[str]
    frameworks: list[str]
    tools: list[str]

    def __post_init__(self) -> None:
        """Validate field types after initialization."""
        if not isinstance(self.job_description, str):
            raise TypeError("job_description must be a string")
        if not isinstance(self.job_title, str):
            raise TypeError("job_title must be a string")
        if not isinstance(self.job_location, str):
            raise TypeError("job_location must be a string")
        if not isinstance(self.job_salary, str):
            raise TypeError("job_salary must be a string")
        if not isinstance(self.job_requirements, list):
            raise TypeError("job_requirements must be a list")
        if not isinstance(self.programming_languages, list):
            raise TypeError("programming_languages must be a list")
        if not isinstance(self.frameworks, list):
            raise TypeError("frameworks must be a list")
        if not isinstance(self.tools, list):
            raise TypeError("tools must be a list")

    def to_dict(self) -> dict[str, Any]:
        """Convert JobDescription to dictionary.

        Returns:
            Dictionary representation with all fields
        """
        return {
            "job_description": self.job_description,
            "job_title": self.job_title,
            "job_location": self.job_location,
            "job_salary": self.job_salary,
            "job_requirements": self.job_requirements,
            "programming_languages": self.programming_languages,
            "frameworks": self.frameworks,
            "tools": self.tools,
        }

    def to_json_file(self, filepath: Path | str) -> None:
        """Write JobDescription to JSON file with proper formatting.

        Args:
            filepath: Path where JSON file will be written

        Note:
            JSON is formatted with 4-space indentation for readability
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JobDescription":
        """Create JobDescription from dictionary.

        Args:
            data: Dictionary containing job description fields

        Returns:
            New JobDescription instance

        Raises:
            KeyError: If required fields are missing
            TypeError: If field types are invalid
        """
        return cls(
            job_description=data["job_description"],
            job_title=data["job_title"],
            job_location=data["job_location"],
            job_salary=data["job_salary"],
            job_requirements=data["job_requirements"],
            programming_languages=data["programming_languages"],
            frameworks=data["frameworks"],
            tools=data["tools"],
        )

    @classmethod
    def from_json_file(cls, filepath: Path | str) -> "JobDescription":
        """Load JobDescription from JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            JobDescription instance loaded from file

        Raises:
            FileNotFoundError: If file does not exist
            json.JSONDecodeError: If file contains invalid JSON
            KeyError: If required fields are missing
        """
        filepath = Path(filepath)

        with open(filepath, "r", encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)

        return cls.from_dict(data)