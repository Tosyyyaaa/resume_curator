"""Candidate data loader for resume curation.

This module provides functionality to load and aggregate candidate information
from multiple JSON files in the candidate_data directory.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CandidateData:
    """Container for all candidate information.

    Attributes:
        experiences: Dictionary containing work_experience, internship_experience,
                    and competitions arrays
        education: Dictionary containing university_education, high_school_education,
                  and other_education arrays
        projects: Dictionary containing projects array
        metadata: Dictionary containing personal information (name, email, etc.)
    """

    experiences: dict[str, Any]
    education: dict[str, Any]
    projects: dict[str, Any]
    metadata: dict[str, Any]

    @classmethod
    def load_from_directory(cls, directory_path: str | Path) -> "CandidateData":
        """Load candidate data from directory containing JSON files.

        Expected files:
            - experiences.json: Work experience, internships, competitions
            - education.json: University, high school, other education
            - projects.json: Personal and academic projects
            - metadata.json: Personal information and contact details

        Args:
            directory_path: Path to directory containing candidate JSON files

        Returns:
            CandidateData instance with all information loaded

        Raises:
            FileNotFoundError: If directory or required files don't exist
            json.JSONDecodeError: If any JSON file is malformed
        """
        directory = Path(directory_path)

        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not directory.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory}")

        # Load all required JSON files
        experiences_path = directory / "experiences.json"
        education_path = directory / "education.json"
        projects_path = directory / "projects.json"
        metadata_path = directory / "metadata.json"

        # Check all files exist
        if not experiences_path.exists():
            raise FileNotFoundError(
                f"Required file not found: experiences.json in {directory}"
            )
        if not education_path.exists():
            raise FileNotFoundError(
                f"Required file not found: education.json in {directory}"
            )
        if not projects_path.exists():
            raise FileNotFoundError(
                f"Required file not found: projects.json in {directory}"
            )
        if not metadata_path.exists():
            raise FileNotFoundError(
                f"Required file not found: metadata.json in {directory}"
            )

        # Load JSON data
        with open(experiences_path, "r", encoding="utf-8") as f:
            experiences: dict[str, Any] = json.load(f)

        with open(education_path, "r", encoding="utf-8") as f:
            education: dict[str, Any] = json.load(f)

        with open(projects_path, "r", encoding="utf-8") as f:
            projects: dict[str, Any] = json.load(f)

        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata: dict[str, Any] = json.load(f)

        return cls(
            experiences=experiences,
            education=education,
            projects=projects,
            metadata=metadata,
        )
