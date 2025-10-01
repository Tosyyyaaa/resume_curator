"""Extracted education data model with line length calculation.

This module provides the ExtractedEducation class for representing education
entries with line-length awareness for page fitting.
"""

from dataclasses import dataclass
from typing import Any

from models.line_metrics import LineMetrics


@dataclass
class ExtractedEducation:
    """Education entry with line length metadata.

    Attributes:
        school: Name of educational institution
        degree: Degree or qualification obtained
        start_date: Start year
        end_date: End year or "Present"
        grade: GPA, grade, or honors (optional)
        courses: List of relevant courses (optional)
        line_length: Number of lines this entry occupies
    """

    school: str
    degree: str
    start_date: str
    end_date: str
    grade: str | None = None
    courses: list[str] | None = None
    line_length: int = 0

    def __post_init__(self) -> None:
        """Calculate line length after initialization."""
        # Ensure courses is a list, not None
        if self.courses is None:
            self.courses = []

        self.line_length = self.calculate_line_length()

    def calculate_line_length(self) -> int:
        """Calculate number of lines needed for education entry.

        Education format:
            Line 1: School Name
            Line 2: Degree | Start - End | Grade (if present)
            Line 3+ (optional): Courses: Course1, Course2, ... (if courses present)

        Returns:
            Number of lines (2-3+ depending on courses)
        """
        lines = 2  # School + degree/dates always present

        # Add line(s) for courses if any are present
        if self.courses and len(self.courses) > 0:
            courses_text = "Courses: " + ", ".join(self.courses)
            course_lines = LineMetrics.calculate_text_lines(courses_text)
            lines += course_lines

        return lines

    def to_dict(self) -> dict[str, Any]:
        """Convert ExtractedEducation to dictionary.

        Returns:
            Dictionary representation with all fields
        """
        return {
            "school": self.school,
            "degree": self.degree,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "grade": self.grade,
            "courses": self.courses,
            "line_length": self.line_length,
        }

    @classmethod
    def from_education_dict(cls, data: dict[str, Any]) -> "ExtractedEducation":
        """Create ExtractedEducation from education dictionary.

        Args:
            data: Dictionary containing education information

        Returns:
            ExtractedEducation instance

        Raises:
            KeyError: If required fields (school, degree, start_date, end_date) are missing
        """
        return cls(
            school=data["school"],
            degree=data["degree"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            grade=data.get("grade"),
            courses=data.get("courses", []),
        )
