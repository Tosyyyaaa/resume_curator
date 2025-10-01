"""Unit tests for CandidateData loader class."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.candidate_data import CandidateData


class TestCandidateData:
    """Test suite for CandidateData class."""

    @pytest.fixture
    def sample_candidate_dir(self, tmp_path):
        """Create sample candidate data directory."""
        # Create experiences.json
        experiences = {
            "work_experience": [
                {
                    "company": "Meta",
                    "title": "Software Engineer",
                    "start_date": "2024",
                    "end_date": "2025",
                    "description": "Built distributed systems",
                }
            ],
            "internship_experience": [],
            "competitions": [],
        }
        (tmp_path / "experiences.json").write_text(json.dumps(experiences))

        # Create education.json
        education = {
            "university_education": [
                {
                    "school": "MIT",
                    "degree": "B.Sc. Computer Science",
                    "start_date": "2020",
                    "end_date": "2024",
                    "grade": "4.0/4.0",
                    "courses": ["AI", "ML"],
                }
            ],
            "high_school_education": [],
            "other_education": [],
        }
        (tmp_path / "education.json").write_text(json.dumps(education))

        # Create projects.json
        projects = {
            "projects": [
                {
                    "name": "Cool Project",
                    "description": "AI-powered tool",
                    "start_date": "2023",
                    "end_date": "2024",
                }
            ]
        }
        (tmp_path / "projects.json").write_text(json.dumps(projects))

        # Create metadata.json
        metadata = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "location": "Boston, MA",
            "linkedin": "https://linkedin.com/in/johndoe",
            "github": "https://github.com/johndoe",
            "website": "https://johndoe.com",
        }
        (tmp_path / "metadata.json").write_text(json.dumps(metadata))

        return tmp_path

    def test_load_from_directory_success(self, sample_candidate_dir):
        """Test successful loading of candidate data."""
        candidate_data = CandidateData.load_from_directory(str(sample_candidate_dir))

        assert candidate_data.experiences is not None
        assert candidate_data.education is not None
        assert candidate_data.projects is not None
        assert candidate_data.metadata is not None

    def test_load_experiences_data(self, sample_candidate_dir):
        """Test experiences data is loaded correctly."""
        candidate_data = CandidateData.load_from_directory(str(sample_candidate_dir))

        assert "work_experience" in candidate_data.experiences
        assert len(candidate_data.experiences["work_experience"]) == 1
        assert candidate_data.experiences["work_experience"][0]["company"] == "Meta"

    def test_load_education_data(self, sample_candidate_dir):
        """Test education data is loaded correctly."""
        candidate_data = CandidateData.load_from_directory(str(sample_candidate_dir))

        assert "university_education" in candidate_data.education
        assert len(candidate_data.education["university_education"]) == 1
        assert candidate_data.education["university_education"][0]["school"] == "MIT"

    def test_load_projects_data(self, sample_candidate_dir):
        """Test projects data is loaded correctly."""
        candidate_data = CandidateData.load_from_directory(str(sample_candidate_dir))

        assert "projects" in candidate_data.projects
        assert len(candidate_data.projects["projects"]) == 1
        assert candidate_data.projects["projects"][0]["name"] == "Cool Project"

    def test_load_metadata(self, sample_candidate_dir):
        """Test metadata is loaded correctly."""
        candidate_data = CandidateData.load_from_directory(str(sample_candidate_dir))

        assert candidate_data.metadata["name"] == "John Doe"
        assert candidate_data.metadata["email"] == "john@example.com"

    def test_missing_experiences_file(self, tmp_path):
        """Test error when experiences.json is missing."""
        # Create only metadata.json
        metadata = {"name": "John Doe"}
        (tmp_path / "metadata.json").write_text(json.dumps(metadata))

        with pytest.raises(FileNotFoundError, match="experiences.json"):
            CandidateData.load_from_directory(str(tmp_path))

    def test_missing_education_file(self, tmp_path):
        """Test error when education.json is missing."""
        # Create experiences.json but not education.json
        experiences = {"work_experience": []}
        (tmp_path / "experiences.json").write_text(json.dumps(experiences))

        with pytest.raises(FileNotFoundError, match="education.json"):
            CandidateData.load_from_directory(str(tmp_path))

    def test_missing_projects_file(self, tmp_path):
        """Test error when projects.json is missing."""
        experiences = {"work_experience": []}
        education = {"university_education": []}
        (tmp_path / "experiences.json").write_text(json.dumps(experiences))
        (tmp_path / "education.json").write_text(json.dumps(education))

        with pytest.raises(FileNotFoundError, match="projects.json"):
            CandidateData.load_from_directory(str(tmp_path))

    def test_missing_metadata_file(self, tmp_path):
        """Test error when metadata.json is missing."""
        experiences = {"work_experience": []}
        education = {"university_education": []}
        projects = {"projects": []}
        (tmp_path / "experiences.json").write_text(json.dumps(experiences))
        (tmp_path / "education.json").write_text(json.dumps(education))
        (tmp_path / "projects.json").write_text(json.dumps(projects))

        with pytest.raises(FileNotFoundError, match="metadata.json"):
            CandidateData.load_from_directory(str(tmp_path))

    def test_invalid_json_in_experiences(self, tmp_path):
        """Test error handling for invalid JSON."""
        # Create all required files, but make experiences.json invalid
        (tmp_path / "experiences.json").write_text("invalid json {")
        (tmp_path / "education.json").write_text('{"university_education": []}')
        (tmp_path / "projects.json").write_text('{"projects": []}')
        (tmp_path / "metadata.json").write_text('{"name": "Test"}')

        with pytest.raises(json.JSONDecodeError):
            CandidateData.load_from_directory(str(tmp_path))

    def test_nonexistent_directory(self):
        """Test error when directory doesn't exist."""
        with pytest.raises(FileNotFoundError):
            CandidateData.load_from_directory("/nonexistent/path")

    def test_load_real_candidate_data(self):
        """Test loading actual candidate data from repository."""
        # This test uses the real candidate_data directory
        candidate_dir = Path(__file__).parent.parent.parent / "candidate_data"

        if not candidate_dir.exists():
            pytest.skip("Real candidate_data directory not found")

        candidate_data = CandidateData.load_from_directory(str(candidate_dir))

        # Verify structure exists
        assert candidate_data.experiences is not None
        assert candidate_data.education is not None
        assert candidate_data.projects is not None
        assert candidate_data.metadata is not None

        # Verify real data matches expected structure
        assert "work_experience" in candidate_data.experiences
        assert "university_education" in candidate_data.education
        assert "projects" in candidate_data.projects
        assert "name" in candidate_data.metadata
