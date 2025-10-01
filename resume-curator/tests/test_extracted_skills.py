"""Unit tests for ExtractedSkills class."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.extracted_skills import ExtractedSkills


class TestExtractedSkills:
    """Test suite for ExtractedSkills class."""

    @pytest.fixture
    def sample_skills(self):
        """Sample skills data."""
        return {
            "programming_languages": ["Python", "Java", "C++", "JavaScript"],
            "frameworks": ["React", "Django", "TensorFlow"],
            "tools": ["Git", "Docker", "AWS"],
        }

    def test_init_success(self, sample_skills):
        """Test successful creation of ExtractedSkills."""
        skills = ExtractedSkills(**sample_skills)

        assert len(skills.programming_languages) == 4
        assert len(skills.frameworks) == 3
        assert len(skills.tools) == 3

    def test_line_length_calculation(self, sample_skills):
        """Test line length calculation."""
        skills = ExtractedSkills(**sample_skills)

        # Programming Languages: Python, Java, C++, JavaScript (< 80 chars)
        # Frameworks: React, Django, TensorFlow (< 80 chars)
        # Tools: Git, Docker, AWS (< 80 chars)
        # Total: 3 lines
        assert skills.line_length == 3

    def test_line_length_with_many_skills(self):
        """Test line length with skills that wrap to multiple lines."""
        skills_data = {
            "programming_languages": [
                "Python",
                "Java",
                "C++",
                "JavaScript",
                "TypeScript",
                "Go",
                "Rust",
                "Ruby",
                "PHP",
                "Swift",
            ],
            "frameworks": ["React", "Angular", "Vue", "Django", "Flask", "Express"],
            "tools": ["Git", "Docker", "Kubernetes", "AWS", "GCP", "Azure"],
        }
        skills = ExtractedSkills(**skills_data)

        # With many skills, each category may wrap to multiple lines
        assert skills.line_length >= 3

    def test_line_length_with_empty_categories(self):
        """Test line length with some empty categories."""
        skills = ExtractedSkills(
            programming_languages=["Python", "Java"],
            frameworks=[],
            tools=["Git"],
        )

        # Programming Languages: Python, Java
        # Tools: Git
        # (Frameworks line omitted if empty)
        assert skills.line_length == 2

    def test_line_length_all_empty(self):
        """Test line length when all categories are empty."""
        skills = ExtractedSkills(
            programming_languages=[],
            frameworks=[],
            tools=[],
        )

        assert skills.line_length == 0

    def test_calculate_line_length_idempotent(self, sample_skills):
        """Test that calculating line length multiple times gives same result."""
        skills = ExtractedSkills(**sample_skills)

        length1 = skills.calculate_line_length()
        length2 = skills.calculate_line_length()
        length3 = skills.line_length

        assert length1 == length2 == length3

    def test_from_lists_success(self, sample_skills):
        """Test creation from lists."""
        skills = ExtractedSkills.from_lists(
            sample_skills["programming_languages"],
            sample_skills["frameworks"],
            sample_skills["tools"],
        )

        assert skills.programming_languages == sample_skills["programming_languages"]
        assert skills.frameworks == sample_skills["frameworks"]
        assert skills.tools == sample_skills["tools"]

    def test_from_lists_with_none(self):
        """Test creation with None values."""
        skills = ExtractedSkills.from_lists(
            ["Python"],
            None,
            ["Git"],
        )

        assert skills.programming_languages == ["Python"]
        assert skills.frameworks == []
        assert skills.tools == ["Git"]

    def test_long_skill_names(self):
        """Test with very long skill names."""
        skills = ExtractedSkills(
            programming_languages=["a" * 50, "b" * 50],
            frameworks=[],
            tools=[],
        )

        # With 50-char skill names, line should wrap
        assert skills.line_length >= 2

    def test_single_skill_per_category(self):
        """Test with single skill in each category."""
        skills = ExtractedSkills(
            programming_languages=["Python"],
            frameworks=["Django"],
            tools=["Git"],
        )

        assert skills.line_length == 3
