"""Unit tests for ResumeHeader class."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.resume_header import ResumeHeader


class TestResumeHeader:
    """Test suite for ResumeHeader class."""

    @pytest.fixture
    def sample_metadata(self):
        """Sample metadata dictionary."""
        return {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "location": "London, UK",
            "linkedin": "https://www.linkedin.com/in/john-doe",
            "github": "https://github.com/john-doe",
            "website": "https://john-doe.com",
        }

    def test_from_metadata_success(self, sample_metadata):
        """Test successful creation from metadata."""
        header = ResumeHeader.from_metadata(sample_metadata)

        assert header.name == "John Doe"
        assert header.email == "john.doe@example.com"
        assert header.phone == "+1234567890"
        assert header.location == "London, UK"

    def test_line_length_calculation(self, sample_metadata):
        """Test line length is calculated correctly."""
        header = ResumeHeader.from_metadata(sample_metadata)

        # Header typically has:
        # Line 1: Name (centered, large)
        # Line 2: email | phone | location
        # Line 3: linkedin | github | website
        # Total: 3 lines
        assert header.line_length == 3

    def test_line_length_without_optional_fields(self):
        """Test line length with minimal metadata."""
        metadata = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "location": "Boston, MA",
        }
        header = ResumeHeader.from_metadata(metadata)

        # Line 1: Name
        # Line 2: email | phone | location
        # Total: 2 lines (no social links)
        assert header.line_length == 2

    def test_from_metadata_with_none_values(self):
        """Test handling of None values in optional fields."""
        metadata = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "location": "Boston, MA",
            "linkedin": None,
            "github": None,
            "website": None,
        }
        header = ResumeHeader.from_metadata(metadata)

        assert header.linkedin is None
        assert header.github is None
        assert header.website is None
        assert header.line_length == 2

    def test_from_metadata_with_missing_optional_fields(self):
        """Test handling of missing optional fields."""
        metadata = {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "phone": "+9876543210",
            "location": "New York, NY",
        }
        header = ResumeHeader.from_metadata(metadata)

        assert header.name == "Jane Smith"
        assert header.linkedin is None
        assert header.github is None
        assert header.website is None

    def test_from_metadata_missing_required_field(self):
        """Test error when required field is missing."""
        metadata = {
            "email": "john@example.com",
            "phone": "+1234567890",
        }

        with pytest.raises(KeyError, match="name"):
            ResumeHeader.from_metadata(metadata)

    def test_line_length_with_long_name(self):
        """Test line length with very long name."""
        metadata = {
            "name": "Dr. Jonathan Alexander Montgomery III, Ph.D.",
            "email": "jonathan@example.com",
            "phone": "+1234567890",
            "location": "Los Angeles, CA",
        }
        header = ResumeHeader.from_metadata(metadata)

        # Even with long name, it's still one line (may be large font)
        assert header.line_length == 2

    def test_line_length_with_all_social_links(self, sample_metadata):
        """Test line length with all social media links."""
        header = ResumeHeader.from_metadata(sample_metadata)

        # All fields present: name line + contact line + social line
        assert header.line_length == 3
        assert header.linkedin is not None
        assert header.github is not None
        assert header.website is not None

    def test_line_length_with_partial_social_links(self):
        """Test line length with only some social links."""
        metadata = {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "phone": "+1234567890",
            "location": "Seattle, WA",
            "github": "https://github.com/alice",
        }
        header = ResumeHeader.from_metadata(metadata)

        # Has social link, so should be 3 lines
        assert header.line_length == 3
        assert header.github == "https://github.com/alice"

    def test_calculate_line_length_idempotent(self, sample_metadata):
        """Test that calculating line length multiple times gives same result."""
        header = ResumeHeader.from_metadata(sample_metadata)

        length1 = header.calculate_line_length()
        length2 = header.calculate_line_length()
        length3 = header.line_length

        assert length1 == length2 == length3 == 3

    def test_empty_string_fields(self):
        """Test handling of empty string fields."""
        metadata = {
            "name": "Bob Smith",
            "email": "bob@example.com",
            "phone": "+1234567890",
            "location": "Chicago, IL",
            "linkedin": "",
            "github": "",
            "website": "",
        }
        header = ResumeHeader.from_metadata(metadata)

        # Empty strings treated as None
        assert header.line_length == 2
