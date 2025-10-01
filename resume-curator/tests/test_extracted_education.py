"""Unit tests for ExtractedEducation class."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.extracted_education import ExtractedEducation


class TestExtractedEducation:
    """Test suite for ExtractedEducation class."""

    @pytest.fixture
    def sample_education(self):
        """Sample education dictionary."""
        return {
            "school": "University of California, Los Angeles",
            "degree": "B.Sc. in Computer Science",
            "start_date": "2020",
            "end_date": "2024",
            "grade": "3.8/4.0",
            "courses": [
                "Computational Linguistics",
                "Computer Vision",
                "Machine Learning",
            ],
        }

    def test_from_education_dict_success(self, sample_education):
        """Test successful creation from education dictionary."""
        edu = ExtractedEducation.from_education_dict(sample_education)

        assert edu.school == "University of California, Los Angeles"
        assert edu.degree == "B.Sc. in Computer Science"
        assert edu.start_date == "2020"
        assert edu.end_date == "2024"
        assert edu.grade == "3.8/4.0"
        assert len(edu.courses) == 3

    def test_line_length_with_courses(self, sample_education):
        """Test line length calculation with courses."""
        edu = ExtractedEducation.from_education_dict(sample_education)

        # Line 1: School name
        # Line 2: Degree | Start - End | Grade
        # Line 3: Courses: Course1, Course2, Course3
        assert edu.line_length == 3

    def test_line_length_without_courses(self):
        """Test line length calculation without courses."""
        education = {
            "school": "MIT",
            "degree": "M.Sc. in Machine Learning",
            "start_date": "2024",
            "end_date": "2025",
            "grade": "Distinction",
            "courses": [],
        }
        edu = ExtractedEducation.from_education_dict(education)

        # Line 1: School name
        # Line 2: Degree | Start - End | Grade
        # No course line
        assert edu.line_length == 2

    def test_line_length_without_grade(self):
        """Test line length calculation without grade."""
        education = {
            "school": "Stanford University",
            "degree": "Ph.D. in Computer Science",
            "start_date": "2025",
            "end_date": "Present",
        }
        edu = ExtractedEducation.from_education_dict(education)

        # Line 1: School
        # Line 2: Degree | Start - End
        assert edu.line_length == 2

    def test_from_education_dict_missing_required_field(self):
        """Test error when required field is missing."""
        education = {
            "degree": "B.Sc. in Computer Science",
            "start_date": "2020",
            "end_date": "2024",
        }

        with pytest.raises(KeyError, match="school"):
            ExtractedEducation.from_education_dict(education)

    def test_from_education_dict_with_optional_fields_missing(self):
        """Test creation with optional fields missing."""
        education = {
            "school": "Harvard University",
            "degree": "B.A. in Computer Science",
            "start_date": "2020",
            "end_date": "2024",
        }
        edu = ExtractedEducation.from_education_dict(education)

        assert edu.school == "Harvard University"
        assert edu.grade is None
        assert edu.courses == []
        assert edu.line_length == 2

    def test_line_length_with_many_courses(self):
        """Test line length with courses spanning multiple lines."""
        education = {
            "school": "UC Berkeley",
            "degree": "B.Sc. in EECS",
            "start_date": "2020",
            "end_date": "2024",
            "grade": "3.9/4.0",
            "courses": [
                "Intro to Computer Science",
                "Data Structures",
                "Algorithms",
                "Operating Systems",
                "Computer Networks",
                "Database Systems",
            ],
        }
        edu = ExtractedEducation.from_education_dict(education)

        # Course list may wrap to multiple lines (> 80 chars)
        # Line 1: School
        # Line 2: Degree | Dates | Grade
        # Line 3+: Courses line (may wrap)
        assert edu.line_length >= 3

    def test_calculate_line_length_idempotent(self, sample_education):
        """Test that calculating line length multiple times gives same result."""
        edu = ExtractedEducation.from_education_dict(sample_education)

        length1 = edu.calculate_line_length()
        length2 = edu.calculate_line_length()
        length3 = edu.line_length

        assert length1 == length2 == length3

    def test_high_school_education(self):
        """Test high school education entry."""
        education = {
            "school": "St. John's College",
            "degree": "A-Levels",
            "start_date": "2017",
            "end_date": "2019",
            "grade": "A*A*A*A*",
        }
        edu = ExtractedEducation.from_education_dict(education)

        assert edu.school == "St. John's College"
        assert edu.degree == "A-Levels"
        assert edu.line_length == 2

    def test_none_values_for_optional_fields(self):
        """Test explicit None values for optional fields."""
        education = {
            "school": "Cambridge",
            "degree": "M.Phil. in Computer Science",
            "start_date": "2024",
            "end_date": "2025",
            "grade": None,
            "courses": None,
        }
        edu = ExtractedEducation.from_education_dict(education)

        assert edu.grade is None
        assert edu.courses == []
        assert edu.line_length == 2
