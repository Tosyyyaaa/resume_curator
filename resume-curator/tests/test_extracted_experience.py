"""Unit tests for ExtractedJobExperience class."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.extracted_experience import ExtractedJobExperience


class TestExtractedJobExperience:
    """Test suite for ExtractedJobExperience class."""

    @pytest.fixture
    def sample_experience(self):
        """Sample job experience dictionary."""
        return {
            "company": "Meta",
            "title": "Software Engineer",
            "start_date": "2024",
            "end_date": "2025",
            "description": "Increased user engagement by 200% using reinforcement learning\nDecreased load time by 50% using distributed systems",
        }

    def test_from_experience_dict_success(self, sample_experience):
        """Test successful creation from experience dictionary."""
        exp = ExtractedJobExperience.from_experience_dict(sample_experience)

        assert exp.company == "Meta"
        assert exp.title == "Software Engineer"
        assert exp.start_date == "2024"
        assert exp.end_date == "2025"
        assert len(exp.description_bullets) == 2

    def test_line_length_calculation(self, sample_experience):
        """Test line length calculation."""
        exp = ExtractedJobExperience.from_experience_dict(sample_experience)

        # Line 1: Title line (Software Engineer at Meta | 2024 - 2025)
        # Line 2: Bullet 1
        # Line 3: Bullet 2
        assert exp.line_length == 3

    def test_from_competition_dict(self):
        """Test creation from competition dictionary."""
        competition = {
            "name": "Meta AI Challenge",
            "description": "Won first place using transformer model",
            "start_date": "2020",
            "end_date": "2021",
        }
        exp = ExtractedJobExperience.from_experience_dict(competition, is_competition=True)

        assert exp.company == "Meta AI Challenge"
        assert exp.title == "Competition"
        assert len(exp.description_bullets) == 1

    def test_single_line_description(self):
        """Test experience with single description."""
        experience = {
            "company": "Google",
            "title": "Senior Engineer",
            "start_date": "2023",
            "end_date": "Present",
            "description": "Led team of 10 engineers",
        }
        exp = ExtractedJobExperience.from_experience_dict(experience)

        # Line 1: Title
        # Line 2: Single bullet
        assert exp.line_length == 2
        assert len(exp.description_bullets) == 1

    def test_long_bullet_wraps_to_multiple_lines(self):
        """Test that long bullet points wrap correctly."""
        experience = {
            "company": "Amazon",
            "title": "Principal Engineer",
            "start_date": "2020",
            "end_date": "2023",
            "description": "a" * 150,  # 150 chars should wrap to 2 lines
        }
        exp = ExtractedJobExperience.from_experience_dict(experience)

        # Line 1: Title
        # Lines 2-3: Wrapped bullet (150 chars = 2 lines at 80 chars/line)
        assert exp.line_length == 3

    def test_trim_to_lines_removes_bullets(self, sample_experience):
        """Test trimming removes bullets to fit constraint."""
        exp = ExtractedJobExperience.from_experience_dict(sample_experience)

        original_length = exp.line_length
        assert original_length == 3

        # Trim to 2 lines (title + 1 bullet)
        exp.trim_to_lines(2)

        assert exp.line_length == 2
        assert len(exp.description_bullets) == 1

    def test_trim_to_lines_keeps_title(self, sample_experience):
        """Test trimming always keeps title line."""
        exp = ExtractedJobExperience.from_experience_dict(sample_experience)

        # Try to trim to just 1 line (title only)
        exp.trim_to_lines(1)

        # Should keep at least title + 1 bullet (minimum 2 lines)
        assert exp.line_length >= 1
        assert len(exp.description_bullets) >= 0

    def test_trim_to_lines_no_change_if_already_fits(self, sample_experience):
        """Test trimming doesn't change if already within limit."""
        exp = ExtractedJobExperience.from_experience_dict(sample_experience)

        original_bullets = exp.description_bullets.copy()

        # Trim to 10 lines (already fits in 3)
        exp.trim_to_lines(10)

        assert exp.description_bullets == original_bullets

    def test_from_experience_dict_missing_description(self):
        """Test handling of missing description field."""
        experience = {
            "company": "Tesla",
            "title": "Engineer",
            "start_date": "2022",
            "end_date": "2023",
        }
        exp = ExtractedJobExperience.from_experience_dict(experience)

        # Should have empty description bullets
        assert len(exp.description_bullets) == 0
        assert exp.line_length == 1  # Just title line

    def test_from_experience_dict_empty_description(self):
        """Test handling of empty description string."""
        experience = {
            "company": "Apple",
            "title": "Engineer",
            "start_date": "2021",
            "end_date": "2022",
            "description": "",
        }
        exp = ExtractedJobExperience.from_experience_dict(experience)

        assert len(exp.description_bullets) == 0
        assert exp.line_length == 1

    def test_description_splitting_preserves_content(self):
        """Test that splitting description preserves all content."""
        experience = {
            "company": "Microsoft",
            "title": "Dev",
            "start_date": "2020",
            "end_date": "2021",
            "description": "First achievement\nSecond achievement\nThird achievement",
        }
        exp = ExtractedJobExperience.from_experience_dict(experience)

        assert len(exp.description_bullets) == 3
        assert "First achievement" in exp.description_bullets
        assert "Second achievement" in exp.description_bullets
        assert "Third achievement" in exp.description_bullets

    def test_trim_to_lines_with_long_bullets(self):
        """Test trimming with bullets that span multiple lines."""
        experience = {
            "company": "Netflix",
            "title": "Engineer",
            "start_date": "2019",
            "end_date": "2020",
            "description": ("a" * 150) + "\n" + ("b" * 150) + "\n" + ("c" * 80),
        }
        exp = ExtractedJobExperience.from_experience_dict(experience)

        # Original: 1 (title) + 2 (first bullet) + 2 (second bullet) + 1 (third bullet) = 6 lines
        assert exp.line_length == 6

        # Trim to 4 lines (title + first bullet only)
        exp.trim_to_lines(4)

        assert exp.line_length <= 4
        assert len(exp.description_bullets) <= 2

    def test_calculate_line_length_idempotent(self, sample_experience):
        """Test that calculating line length multiple times gives same result."""
        exp = ExtractedJobExperience.from_experience_dict(sample_experience)

        length1 = exp.calculate_line_length()
        length2 = exp.calculate_line_length()
        length3 = exp.line_length

        assert length1 == length2 == length3

    def test_from_experience_dict_missing_required_field(self):
        """Test error when required field is missing."""
        experience = {
            "title": "Engineer",
            "start_date": "2020",
            "end_date": "2021",
        }

        with pytest.raises(KeyError, match="company"):
            ExtractedJobExperience.from_experience_dict(experience)

    def test_default_relevance_score_is_zero(self, sample_experience):
        """Test that default relevance score is 0."""
        exp = ExtractedJobExperience.from_experience_dict(sample_experience)
        assert exp.relevance_score == 0

    def test_relevance_score_can_be_set(self, sample_experience):
        """Test that relevance score can be provided."""
        exp = ExtractedJobExperience.from_experience_dict(
            sample_experience, relevance_score=5
        )
        assert exp.relevance_score == 5

    def test_to_dict_includes_relevance_score(self, sample_experience):
        """Test that to_dict includes relevance_score."""
        exp = ExtractedJobExperience.from_experience_dict(
            sample_experience, relevance_score=3
        )
        exp_dict = exp.to_dict()
        assert "relevance_score" in exp_dict
        assert exp_dict["relevance_score"] == 3

    def test_from_experience_dict_with_score(self, sample_experience):
        """Test creating experience with calculated score."""

        class MockJobDescription:
            programming_languages = ["Python", "Rust"]
            frameworks = ["React", "Django"]
            tools = ["Git", "Docker"]

        # Add tech fields to experience
        sample_experience["languages"] = ["Python", "JavaScript"]
        sample_experience["frameworks"] = ["React"]
        sample_experience["tools"] = ["Git"]

        job_desc = MockJobDescription()
        exp = ExtractedJobExperience.from_experience_dict_with_score(
            sample_experience, job_desc
        )

        # Should score: 1 (Python) + 1 (React) + 1 (Git) = 3
        assert exp.relevance_score == 3

    def test_description_as_list(self):
        """Test handling description as list format."""
        experience = {
            "company": "TechCo",
            "title": "Engineer",
            "start_date": "2020",
            "end_date": "2021",
            "description": [
                "Improved performance by 50%",
                "Led team of 5 engineers",
                "Deployed to production"
            ],
        }
        exp = ExtractedJobExperience.from_experience_dict(experience)

        assert len(exp.description_bullets) == 3
        assert "Improved performance by 50%" in exp.description_bullets
        assert "Led team of 5 engineers" in exp.description_bullets
        assert "Deployed to production" in exp.description_bullets

    def test_description_list_with_empty_strings(self):
        """Test that empty strings in list are filtered out."""
        experience = {
            "company": "TechCo",
            "title": "Engineer",
            "start_date": "2020",
            "end_date": "2021",
            "description": ["First bullet", "", "  ", "Second bullet"],
        }
        exp = ExtractedJobExperience.from_experience_dict(experience)

        assert len(exp.description_bullets) == 2
        assert "First bullet" in exp.description_bullets
        assert "Second bullet" in exp.description_bullets

    def test_backward_compatibility_string_description(self):
        """Test backward compatibility with string description format."""
        experience = {
            "company": "OldCo",
            "title": "Dev",
            "start_date": "2019",
            "end_date": "2020",
            "description": "Bullet one\nBullet two\nBullet three",
        }
        exp = ExtractedJobExperience.from_experience_dict(experience)

        assert len(exp.description_bullets) == 3
        assert "Bullet one" in exp.description_bullets
