"""Unit tests for PendingResume class."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.extracted_education import ExtractedEducation
from models.extracted_experience import ExtractedJobExperience
from models.extracted_project import ExtractedProject
from models.extracted_skills import ExtractedSkills
from models.pending_resume import PendingResume
from models.resume_header import ResumeHeader


class TestPendingResume:
    """Test suite for PendingResume class."""

    @pytest.fixture
    def sample_header(self):
        """Sample resume header."""
        return ResumeHeader(
            name="John Doe",
            email="john@example.com",
            phone="+1234567890",
            location="Boston, MA",
            linkedin="https://linkedin.com/in/johndoe",
            github="https://github.com/johndoe",
            website="https://johndoe.com",
        )

    @pytest.fixture
    def sample_experiences(self):
        """Sample job experiences."""
        return [
            ExtractedJobExperience(
                company="Meta",
                title="Software Engineer",
                start_date="2024",
                end_date="2025",
                description_bullets=["Built distributed systems", "Improved performance"],
            ),
            ExtractedJobExperience(
                company="Google",
                title="SWE Intern",
                start_date="2023",
                end_date="2024",
                description_bullets=["Developed features"],
            ),
        ]

    @pytest.fixture
    def sample_education(self):
        """Sample education entries."""
        return [
            ExtractedEducation(
                school="MIT",
                degree="B.Sc. Computer Science",
                start_date="2020",
                end_date="2024",
                grade="4.0/4.0",
                courses=["AI", "ML"],
            )
        ]

    @pytest.fixture
    def sample_projects(self):
        """Sample projects."""
        return [
            ExtractedProject(
                name="Cool AI Project",
                description="Built transformer model",
                start_date="2023",
                end_date="2024",
            )
        ]

    @pytest.fixture
    def sample_skills(self):
        """Sample skills."""
        return ExtractedSkills(
            programming_languages=["Python", "Java"],
            frameworks=["Django", "React"],
            tools=["Git", "Docker"],
        )

    def test_init_success(
        self,
        sample_header,
        sample_experiences,
        sample_education,
        sample_projects,
        sample_skills,
    ):
        """Test successful creation of PendingResume."""
        resume = PendingResume(
            header=sample_header,
            experiences=sample_experiences,
            education=sample_education,
            projects=sample_projects,
            skills=sample_skills,
            permitted_line_length=45,
        )

        assert resume.header == sample_header
        assert len(resume.experiences) == 2
        assert len(resume.education) == 1
        assert len(resume.projects) == 1
        assert resume.skills == sample_skills

    def test_calculate_total_line_length(
        self,
        sample_header,
        sample_experiences,
        sample_education,
        sample_projects,
        sample_skills,
    ):
        """Test total line length calculation."""
        resume = PendingResume(
            header=sample_header,
            experiences=sample_experiences,
            education=sample_education,
            projects=sample_projects,
            skills=sample_skills,
            permitted_line_length=45,
        )

        total = resume.calculate_total_line_length()

        # Header + sum of all experiences + education + projects + skills
        expected = (
            sample_header.line_length
            + sum(exp.line_length for exp in sample_experiences)
            + sum(edu.line_length for edu in sample_education)
            + sum(proj.line_length for proj in sample_projects)
            + sample_skills.line_length
        )
        assert total == expected
        assert resume.line_length == total

    def test_fits_page_limit_true(
        self,
        sample_header,
        sample_experiences,
        sample_education,
        sample_projects,
        sample_skills,
    ):
        """Test fits_page_limit returns True when within limit."""
        resume = PendingResume(
            header=sample_header,
            experiences=sample_experiences,
            education=sample_education,
            projects=sample_projects,
            skills=sample_skills,
            permitted_line_length=100,  # Large limit
        )

        assert resume.fits_page_limit() is True

    def test_fits_page_limit_false(
        self,
        sample_header,
        sample_experiences,
        sample_education,
        sample_projects,
        sample_skills,
    ):
        """Test fits_page_limit returns False when over limit."""
        resume = PendingResume(
            header=sample_header,
            experiences=sample_experiences,
            education=sample_education,
            projects=sample_projects,
            skills=sample_skills,
            permitted_line_length=5,  # Very small limit
        )

        assert resume.fits_page_limit() is False

    def test_empty_resume(self):
        """Test empty resume with minimal content."""
        header = ResumeHeader(
            name="Jane Doe",
            email="jane@example.com",
            phone="+1234567890",
            location="NYC",
        )

        resume = PendingResume(
            header=header,
            experiences=[],
            education=[],
            projects=[],
            skills=ExtractedSkills([], [], []),
            permitted_line_length=10,
        )

        # Should only have header length
        assert resume.line_length == header.line_length
        assert resume.fits_page_limit() is True

    def test_line_length_updates_after_modification(
        self, sample_header, sample_experiences
    ):
        """Test that line_length updates when components change."""
        resume = PendingResume(
            header=sample_header,
            experiences=sample_experiences,
            education=[],
            projects=[],
            skills=ExtractedSkills([], [], []),
            permitted_line_length=45,
        )

        original_length = resume.line_length

        # Trim one experience
        sample_experiences[0].trim_to_lines(2)

        # Recalculate
        new_length = resume.calculate_total_line_length()

        assert new_length < original_length

    def test_permitted_line_length_from_page_limit(
        self, sample_header, sample_experiences
    ):
        """Test conversion from page limit to line length."""
        resume = PendingResume.with_page_limit(
            header=sample_header,
            experiences=sample_experiences,
            education=[],
            projects=[],
            skills=ExtractedSkills([], [], []),
            page_limit=1,
        )

        # 1 page = 45 lines
        assert resume.permitted_line_length == 45

    def test_with_page_limit_multiple_pages(
        self, sample_header, sample_experiences
    ):
        """Test with_page_limit for multiple pages."""
        resume = PendingResume.with_page_limit(
            header=sample_header,
            experiences=sample_experiences,
            education=[],
            projects=[],
            skills=ExtractedSkills([], [], []),
            page_limit=2,
        )

        # 2 pages = 90 lines
        assert resume.permitted_line_length == 90

    def test_optimize_to_fit_already_fits(
        self,
        sample_header,
        sample_experiences,
        sample_education,
        sample_projects,
        sample_skills,
    ):
        """Test optimize_to_fit when resume already fits."""
        resume = PendingResume(
            header=sample_header,
            experiences=sample_experiences,
            education=sample_education,
            projects=sample_projects,
            skills=sample_skills,
            permitted_line_length=100,  # Large limit
        )

        original_length = resume.line_length
        resume.optimize_to_fit()

        # Should not change if already fits
        assert resume.line_length == original_length
        assert resume.fits_page_limit()

    def test_optimize_to_fit_trims_project_descriptions(
        self,
        sample_header,
        sample_experiences,
        sample_education,
        sample_skills,
    ):
        """Test optimize_to_fit trims project descriptions first."""
        # Create project with long description
        long_project = ExtractedProject(
            name="Long Project",
            description="a" * 200,  # Very long description
            start_date="2020",
            end_date="2021",
        )

        resume = PendingResume(
            header=sample_header,
            experiences=sample_experiences,
            education=sample_education,
            projects=[long_project],
            skills=sample_skills,
            permitted_line_length=10,  # Very tight limit
        )

        assert not resume.fits_page_limit()

        original_desc_length = len(long_project.description)
        resume.optimize_to_fit()

        # Project description should be trimmed
        assert len(long_project.description) < original_desc_length

    def test_optimize_to_fit_removes_projects_if_needed(
        self,
        sample_header,
        sample_experiences,
        sample_education,
        sample_skills,
    ):
        """Test optimize_to_fit removes projects if trimming isn't enough."""
        projects = [
            ExtractedProject(
                name=f"Project {i}",
                description="Description here",
                start_date="2020",
                end_date="2021",
            )
            for i in range(5)
        ]

        resume = PendingResume(
            header=sample_header,
            experiences=sample_experiences,
            education=sample_education,
            projects=projects,
            skills=sample_skills,
            permitted_line_length=15,  # Very tight limit
        )

        assert len(resume.projects) == 5
        resume.optimize_to_fit()

        # Some projects should be removed
        assert len(resume.projects) < 5

    def test_optimize_to_fit_trims_experience_bullets(
        self,
        sample_header,
        sample_education,
        sample_projects,
        sample_skills,
    ):
        """Test optimize_to_fit trims experience bullets after projects."""
        experiences = [
            ExtractedJobExperience(
                company="Company",
                title="Engineer",
                start_date="2020",
                end_date="2021",
                description_bullets=[f"Bullet {i}" for i in range(10)],
            )
        ]

        resume = PendingResume(
            header=sample_header,
            experiences=experiences,
            education=sample_education,
            projects=[],  # No projects to trim
            skills=sample_skills,
            permitted_line_length=10,
        )

        original_bullet_count = len(experiences[0].description_bullets)
        resume.optimize_to_fit()

        # Bullets should be reduced
        assert len(experiences[0].description_bullets) < original_bullet_count
