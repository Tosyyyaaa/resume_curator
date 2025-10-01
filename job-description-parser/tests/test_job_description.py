"""Unit tests for JobDescription data model.

This module contains comprehensive tests for the JobDescription class,
ensuring proper serialization, deserialization, and validation.
"""

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from models.job_description import JobDescription


class TestJobDescriptionCreation:
    """Test JobDescription object instantiation."""

    def test_job_description_creation_with_valid_data(self) -> None:
        """Verify JobDescription can be instantiated with all valid fields."""
        job_desc: JobDescription = JobDescription(
            job_description="Test description",
            job_title="Software Engineer",
            job_location="London, UK",
            job_salary="£100,000 - £120,000 per year",
            job_requirements=["Python experience", "CS degree"],
            programming_languages=["Python", "Java"],
            frameworks=["Django", "Flask"],
            tools=["Git", "Docker"],
        )

        assert job_desc.job_description == "Test description"
        assert job_desc.job_title == "Software Engineer"
        assert job_desc.job_location == "London, UK"
        assert job_desc.job_salary == "£100,000 - £120,000 per year"
        assert len(job_desc.job_requirements) == 2
        assert len(job_desc.programming_languages) == 2
        assert len(job_desc.frameworks) == 2
        assert len(job_desc.tools) == 2

    def test_job_description_with_empty_lists(self) -> None:
        """Verify JobDescription handles empty lists for optional fields."""
        job_desc: JobDescription = JobDescription(
            job_description="Test",
            job_title="Engineer",
            job_location="Remote",
            job_salary="N/A",
            job_requirements=[],
            programming_languages=[],
            frameworks=[],
            tools=[],
        )

        assert job_desc.job_requirements == []
        assert job_desc.programming_languages == []
        assert job_desc.frameworks == []
        assert job_desc.tools == []


class TestJobDescriptionSerialization:
    """Test JSON serialization methods."""

    def test_to_dict(self) -> None:
        """Verify to_dict returns proper dictionary structure."""
        job_desc: JobDescription = JobDescription(
            job_description="Test description",
            job_title="Software Engineer",
            job_location="London",
            job_salary="£100k",
            job_requirements=["Requirement 1"],
            programming_languages=["Python"],
            frameworks=["Django"],
            tools=["Git"],
        )

        result: dict[str, Any] = job_desc.to_dict()

        assert isinstance(result, dict)
        assert result["job_title"] == "Software Engineer"
        assert result["job_location"] == "London"
        assert isinstance(result["job_requirements"], list)
        assert isinstance(result["programming_languages"], list)

    def test_to_json_file(self) -> None:
        """Verify to_json_file writes properly formatted JSON to file."""
        job_desc: JobDescription = JobDescription(
            job_description="Test description",
            job_title="Engineer",
            job_location="London",
            job_salary="£100k",
            job_requirements=["Req1"],
            programming_languages=["Python"],
            frameworks=["Django"],
            tools=["Git"],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath: Path = Path(tmpdir) / "test_job.json"
            job_desc.to_json_file(filepath)

            assert filepath.exists()

            # Verify JSON is properly formatted with 4-space indentation
            with open(filepath, "r", encoding="utf-8") as f:
                content: str = f.read()
                data: dict[str, Any] = json.loads(content)

            assert data["job_title"] == "Engineer"
            assert "    " in content  # Check for 4-space indentation


class TestJobDescriptionDeserialization:
    """Test JSON deserialization methods."""

    def test_from_dict(self) -> None:
        """Verify from_dict creates JobDescription from dictionary."""
        data: dict[str, Any] = {
            "job_description": "Test description",
            "job_title": "Software Engineer",
            "job_location": "London, UK",
            "job_salary": "£100k",
            "job_requirements": ["Python", "CS degree"],
            "programming_languages": ["Python", "Java"],
            "frameworks": ["Django"],
            "tools": ["Git", "Docker"],
        }

        job_desc: JobDescription = JobDescription.from_dict(data)

        assert job_desc.job_title == "Software Engineer"
        assert job_desc.job_location == "London, UK"
        assert len(job_desc.job_requirements) == 2
        assert len(job_desc.programming_languages) == 2

    def test_from_json_file(self) -> None:
        """Verify from_json_file loads JobDescription from JSON file."""
        data: dict[str, Any] = {
            "job_description": "Test description",
            "job_title": "ML Engineer",
            "job_location": "London",
            "job_salary": "£100k-£120k",
            "job_requirements": ["ML experience"],
            "programming_languages": ["Python"],
            "frameworks": ["TensorFlow", "PyTorch"],
            "tools": ["Git"],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath: Path = Path(tmpdir) / "test_job.json"

            # Write test JSON file
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f)

            # Load from file
            job_desc: JobDescription = JobDescription.from_json_file(filepath)

            assert job_desc.job_title == "ML Engineer"
            assert len(job_desc.frameworks) == 2
            assert "TensorFlow" in job_desc.frameworks

    def test_from_json_file_with_actual_meta_engineer_json(self) -> None:
        """Verify from_json_file works with actual meta_engineer.json file."""
        filepath: Path = Path("job_descriptions/parsed/meta_engineer.json")

        if not filepath.exists():
            pytest.skip("meta_engineer.json not found")

        job_desc: JobDescription = JobDescription.from_json_file(filepath)

        assert job_desc.job_title == "Software Engineer, Machine Learning"
        assert job_desc.job_location == "London, UK"
        assert len(job_desc.programming_languages) > 0
        assert "Python" in job_desc.programming_languages


class TestJobDescriptionValidation:
    """Test validation logic for JobDescription."""

    def test_missing_required_field_raises_error(self) -> None:
        """Verify missing required fields raise appropriate errors."""
        with pytest.raises((TypeError, ValueError)):
            JobDescription(  # type: ignore[call-arg]
                job_description="Test",
                job_title="Engineer",
                # Missing job_location
                job_salary="£100k",
                job_requirements=[],
                programming_languages=[],
                frameworks=[],
                tools=[],
            )

    def test_invalid_type_for_list_field_raises_error(self) -> None:
        """Verify invalid types for list fields raise errors."""
        with pytest.raises((TypeError, ValueError)):
            JobDescription(
                job_description="Test",
                job_title="Engineer",
                job_location="London",
                job_salary="£100k",
                job_requirements="not a list",  # type: ignore[arg-type]
                programming_languages=[],
                frameworks=[],
                tools=[],
            )


class TestRoundTripSerialization:
    """Test that serialization and deserialization are symmetric."""

    def test_roundtrip_via_dict(self) -> None:
        """Verify object -> dict -> object produces identical result."""
        original: JobDescription = JobDescription(
            job_description="Full job description text",
            job_title="Senior Software Engineer",
            job_location="London, UK",
            job_salary="£100,000 - £120,000",
            job_requirements=["5+ years experience", "CS degree"],
            programming_languages=["Python", "Java", "C++"],
            frameworks=["Django", "FastAPI"],
            tools=["Git", "Docker", "Kubernetes"],
        )

        # Serialize to dict and back
        data: dict[str, Any] = original.to_dict()
        restored: JobDescription = JobDescription.from_dict(data)

        assert restored.job_description == original.job_description
        assert restored.job_title == original.job_title
        assert restored.job_location == original.job_location
        assert restored.job_salary == original.job_salary
        assert restored.job_requirements == original.job_requirements
        assert restored.programming_languages == original.programming_languages
        assert restored.frameworks == original.frameworks
        assert restored.tools == original.tools

    def test_roundtrip_via_file(self) -> None:
        """Verify object -> file -> object produces identical result."""
        original: JobDescription = JobDescription(
            job_description="Test description",
            job_title="Engineer",
            job_location="Remote",
            job_salary="£80k",
            job_requirements=["Python"],
            programming_languages=["Python", "SQL"],
            frameworks=["Flask"],
            tools=["Git"],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath: Path = Path(tmpdir) / "test.json"

            # Write and read back
            original.to_json_file(filepath)
            restored: JobDescription = JobDescription.from_json_file(filepath)

            assert restored.job_title == original.job_title
            assert restored.job_requirements == original.job_requirements
            assert restored.programming_languages == original.programming_languages