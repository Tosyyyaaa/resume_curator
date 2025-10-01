"""Unit tests for ExtractedProject class."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.extracted_project import ExtractedProject


class TestExtractedProject:
    """Test suite for ExtractedProject class."""

    @pytest.fixture
    def sample_project(self):
        """Sample project dictionary."""
        return {
            "name": "Image Captioning",
            "description": "Image captioning using a transformer model, 90% accuracy against HumanEval benchmark",
            "start_date": "2020",
            "end_date": "2021",
        }

    def test_from_project_dict_success(self, sample_project):
        """Test successful creation from project dictionary."""
        proj = ExtractedProject.from_project_dict(sample_project)

        assert proj.name == "Image Captioning"
        assert "transformer model" in proj.description
        assert proj.start_date == "2020"
        assert proj.end_date == "2021"

    def test_line_length_calculation(self, sample_project):
        """Test line length calculation."""
        proj = ExtractedProject.from_project_dict(sample_project)

        # Line 1: Project Name | 2020 - 2021
        # Line 2: Description (under 80 chars, so 2 lines total for ~95 char description)
        assert proj.line_length >= 2

    def test_line_length_with_long_description(self):
        """Test line length with description spanning multiple lines."""
        project = {
            "name": "Large Project",
            "description": "a" * 200,  # 200 chars = 3 lines at 80 chars/line
            "start_date": "2022",
            "end_date": "2023",
        }
        proj = ExtractedProject.from_project_dict(project)

        # Line 1: Name | Dates
        # Lines 2-4: Description (200 chars = 3 lines)
        assert proj.line_length == 4

    def test_trim_description_shortens_text(self, sample_project):
        """Test trimming description to fit character limit."""
        proj = ExtractedProject.from_project_dict(sample_project)

        original_desc = proj.description
        proj.trim_description(50)

        assert len(proj.description) <= 50
        assert proj.description != original_desc
        # Should append ellipsis
        assert proj.description.endswith("...")

    def test_trim_description_no_change_if_shorter(self):
        """Test trimming doesn't change short descriptions."""
        project = {
            "name": "Small Project",
            "description": "Short desc",
            "start_date": "2021",
            "end_date": "2022",
        }
        proj = ExtractedProject.from_project_dict(project)

        original_desc = proj.description
        proj.trim_description(100)

        assert proj.description == original_desc

    def test_trim_description_updates_line_length(self, sample_project):
        """Test that trimming updates line_length."""
        proj = ExtractedProject.from_project_dict(sample_project)

        original_length = proj.line_length
        proj.trim_description(30)

        # After trimming, should be shorter
        assert proj.line_length <= original_length

    def test_from_project_dict_missing_description(self):
        """Test handling of missing description."""
        project = {
            "name": "Minimal Project",
            "start_date": "2020",
            "end_date": "2021",
        }
        proj = ExtractedProject.from_project_dict(project)

        assert proj.description == ""
        # Line 1: Name | Dates
        # No description line
        assert proj.line_length == 1

    def test_from_project_dict_empty_description(self):
        """Test handling of empty description."""
        project = {
            "name": "Empty Desc Project",
            "description": "",
            "start_date": "2019",
            "end_date": "2020",
        }
        proj = ExtractedProject.from_project_dict(project)

        assert proj.description == ""
        assert proj.line_length == 1

    def test_from_project_dict_missing_required_field(self):
        """Test error when required field is missing."""
        project = {
            "description": "Some description",
            "start_date": "2020",
            "end_date": "2021",
        }

        with pytest.raises(KeyError, match="name"):
            ExtractedProject.from_project_dict(project)

    def test_trim_description_very_small_limit(self, sample_project):
        """Test trimming to very small character limit."""
        proj = ExtractedProject.from_project_dict(sample_project)

        proj.trim_description(10)

        # Should be at most 10 chars (including ellipsis)
        assert len(proj.description) <= 10
        assert proj.description.endswith("...")

    def test_calculate_line_length_idempotent(self, sample_project):
        """Test that calculating line length multiple times gives same result."""
        proj = ExtractedProject.from_project_dict(sample_project)

        length1 = proj.calculate_line_length()
        length2 = proj.calculate_line_length()
        length3 = proj.line_length

        assert length1 == length2 == length3

    def test_line_length_only_name_line_when_no_description(self):
        """Test line length is 1 when no description."""
        project = {
            "name": "Name Only Project",
            "start_date": "2023",
            "end_date": "2024",
        }
        proj = ExtractedProject.from_project_dict(project)

        assert proj.line_length == 1
        assert proj.description == ""
