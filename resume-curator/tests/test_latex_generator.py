"""Tests for LaTeX resume generator (template-based).

Updated for template-based text replacement approach.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.latex_generator import (
    _escape_latex,
    _extract_profile_data,
    _build_education_section,
    _build_experience_section,
    _build_projects_section,
    _extract_skills_data,
    generate_latex_resume,
)


class TestCharacterEscaping:
    """Test character escaping for LaTeX special characters."""

    def test_escape_ampersand(self):
        """Test that ampersand is escaped correctly."""
        assert _escape_latex("AT&T") == "AT\\&T"

    def test_escape_percent(self):
        """Test that percent sign is escaped correctly."""
        assert _escape_latex("100% complete") == "100\\% complete"

    def test_escape_dollar(self):
        """Test that dollar sign is escaped correctly."""
        assert _escape_latex("Cost: $50") == "Cost: \\$50"

    def test_escape_hash(self):
        """Test that hash/pound sign is escaped correctly."""
        assert _escape_latex("Issue #42") == "Issue \\#42"

    def test_escape_underscore(self):
        """Test that underscore is escaped correctly."""
        assert _escape_latex("file_name") == "file\\_name"

    def test_escape_braces(self):
        """Test that curly braces are escaped correctly."""
        assert _escape_latex("func{arg}") == "func\\{arg\\}"

    def test_escape_tilde(self):
        """Test that tilde is escaped correctly."""
        assert _escape_latex("~username") == "\\~{}username"

    def test_escape_caret(self):
        """Test that caret is escaped correctly."""
        assert _escape_latex("x^2") == "x\\^{}2"

    def test_escape_backslash(self):
        """Test that backslash is escaped correctly."""
        assert _escape_latex("path\\to\\file") == "path\\textbackslash{}to\\textbackslash{}file"

    def test_escape_multiple_characters(self):
        """Test escaping string with multiple special characters."""
        text = "AT&T costs $100 (50% off!)"
        expected = "AT\\&T costs \\$100 (50\\% off!)"
        assert _escape_latex(text) == expected

    def test_escape_empty_string(self):
        """Test escaping empty string."""
        assert _escape_latex("") == ""

    def test_escape_no_special_chars(self):
        """Test string with no special characters."""
        assert _escape_latex("Hello World") == "Hello World"


class TestSectionBuilders:
    """Test individual section builder functions (template-based)."""

    def test_extract_profile_data(self):
        """Test profile data extraction from ResumeHeader."""
        from models.resume_header import ResumeHeader

        header = ResumeHeader(
            name='John Doe',
            email='john@example.com',
            phone='+1234567890',
            location='Boston, MA',
            github='https://github.com/johndoe',
            linkedin='https://www.linkedin.com/in/johndoe',
        )

        profile_data = _extract_profile_data(header)

        # Check placeholder mappings
        assert profile_data['{{NAME}}'] == 'John Doe'
        assert profile_data['{{EMAIL}}'] == 'john@example.com'
        assert profile_data['{{PHONE}}'] == '+1234567890'
        assert profile_data['{{GITHUB}}'] == 'johndoe'  # URL stripped
        assert profile_data['{{LINKEDIN}}'] == 'johndoe'  # URL stripped

    def test_build_education_section(self):
        """Test education section generation using typed ExtractedEducation."""
        from models.extracted_education import ExtractedEducation

        education = [
            ExtractedEducation(
                school='MIT',
                degree='B.S. Computer Science',
                start_date='2018',
                end_date='2022',
                location='Cambridge, MA',
                grade='3.9/4.0',
                courses=['AI', 'Machine Learning', 'Algorithms'],
            )
        ]

        edu_section = _build_education_section(education)

        # Check for educationHeading (no section header - template has it)
        assert '\\educationHeading{MIT}{B.S. Computer Science}{Cambridge, MA}{2018 - 2022}' in edu_section
        assert '\\modules{AI, Machine Learning, Algorithms}' in edu_section
        assert '\\textbf{3.9/4.0}' in edu_section

    def test_build_education_section_empty(self):
        """Test education section with no entries."""
        assert _build_education_section([]) == ""

    def test_build_experience_section(self):
        """Test experience section generation using typed ExtractedJobExperience."""
        from models.extracted_experience import ExtractedJobExperience

        experiences = [
            ExtractedJobExperience(
                company='Google',
                title='Software Engineer',
                location='Mountain View, CA',
                start_date='2022',
                end_date='2024',
                description_bullets=[
                    'Built scalable systems',
                    'Improved performance by 50%',
                ],
                relevance_score=5,
            )
        ]

        exp_section = _build_experience_section(experiences)

        # Check for resumeHeading (no section header - template has it)
        assert '\\resumeHeading{Google}{Software Engineer}{Mountain View, CA}{2022 - 2024}' in exp_section
        assert '\\begin{bullets}' in exp_section
        assert '\\item Built scalable systems' in exp_section
        assert '\\item Improved performance by 50\\%' in exp_section  # % should be escaped
        assert '\\end{bullets}' in exp_section

    def test_build_experience_section_empty(self):
        """Test experience section with no entries."""
        assert _build_experience_section([]) == ""

    def test_build_projects_section(self):
        """Test projects section generation using typed ExtractedProject."""
        from models.extracted_project import ExtractedProject

        projects = [
            ExtractedProject(
                name='Resume Generator',
                description='Automated resume generation tool',
                start_date='2023',
                end_date='2024',
                relevance_score=4,
            )
        ]

        proj_section = _build_projects_section(projects)

        # Check for projectHeading (no section header - template has it)
        assert '\\projectHeading{Resume Generator}' in proj_section
        assert 'Automated resume generation tool' in proj_section

    def test_build_projects_section_empty(self):
        """Test projects section with no entries."""
        assert _build_projects_section([]) == ""

    def test_extract_skills_data(self):
        """Test skills data extraction using typed ExtractedSkills."""
        from models.extracted_skills import ExtractedSkills

        skills = ExtractedSkills(
            programming_languages=['Python', 'JavaScript', 'C++'],
            frameworks=['React', 'Django', 'TensorFlow'],
            tools=['Git', 'Docker', 'AWS'],
        )

        skills_data = _extract_skills_data(skills)

        # Check placeholder mappings
        assert skills_data['{{SKILLS_ROW1_LEFT_LABEL}}'] == 'Languages:'
        assert skills_data['{{SKILLS_ROW1_LEFT_VALUE}}'] == 'Python, JavaScript, C++'
        assert skills_data['{{SKILLS_ROW1_RIGHT_LABEL}}'] == 'Frameworks:'
        assert skills_data['{{SKILLS_ROW1_RIGHT_VALUE}}'] == 'React, Django, TensorFlow'
        assert skills_data['{{SKILLS_ROW2_RIGHT_LABEL}}'] == 'Tools:'
        assert skills_data['{{SKILLS_ROW2_RIGHT_VALUE}}'] == 'Git, Docker, AWS'

    def test_special_characters_in_sections(self):
        """Test that special characters are escaped in section builders."""
        from models.extracted_experience import ExtractedJobExperience

        experiences = [
            ExtractedJobExperience(
                company='AT&T',
                title='Engineer',
                location='TX',
                start_date='2020',
                end_date='2022',
                description_bullets=['Increased revenue by 100%'],
                relevance_score=3,
            )
        ]

        exp_section = _build_experience_section(experiences)

        # Check that special characters are escaped
        assert 'AT\\&T' in exp_section
        assert '100\\%' in exp_section


class TestIntegration:
    """Integration tests for complete LaTeX generation."""

    def test_generate_latex_resume_complete(self, tmp_path):
        """Test end-to-end LaTeX generation with BengtResume."""
        from models.bengt_resume import BengtResume
        from models.resume_header import ResumeHeader
        from models.extracted_education import ExtractedEducation
        from models.extracted_experience import ExtractedJobExperience
        from models.extracted_project import ExtractedProject
        from models.extracted_skills import ExtractedSkills

        # Create test resume data
        header = ResumeHeader(
            name="Test User",
            email="test@example.com",
            phone="+1234567890",
            location="Test City, TC",
            linkedin="https://www.linkedin.com/in/testuser",
            github="https://github.com/testuser",
            website="https://testuser.com",
        )

        education = [
            ExtractedEducation(
                school="Test University",
                degree="B.S. Computer Science",
                start_date="2020",
                end_date="2024",
                location="Test City, TC",
                grade="3.8/4.0",
                courses=["Algorithms", "AI", "Databases"],
            )
        ]

        experiences = [
            ExtractedJobExperience(
                company="Test Corp",
                title="Software Engineer",
                start_date="2024",
                end_date="2025",
                location="Test City, TC",
                description_bullets=["Built test systems", "Improved performance"],
                relevance_score=5,
            )
        ]

        projects = [
            ExtractedProject(
                name="Test Project",
                description="A test project for testing",
                start_date="2023",
                end_date="2024",
                relevance_score=3,
            )
        ]

        skills = ExtractedSkills(
            programming_languages=["Python", "JavaScript"],
            frameworks=["React", "Django"],
            tools=["Git", "Docker"],
        )

        # Create BengtResume (template-specific)
        resume = BengtResume.with_page_limit(
            header=header,
            experiences=experiences,
            education=education,
            projects=projects,
            skills=skills,
            page_limit=1,
        )

        # Generate LaTeX (no template_name needed - resume knows it)
        output_path = tmp_path / "test_resume.tex"
        generate_latex_resume(resume, output_path)

        # Verify file was created
        assert output_path.exists()

        # Read generated content
        content = output_path.read_text(encoding='utf-8')

        # Verify key placeholders were replaced
        assert 'Test User' in content
        assert 'test@example.com' in content
        assert 'Test University' in content
        assert 'Test Corp' in content
        assert 'Test Project' in content
        assert 'Python, JavaScript' in content
        assert '\\end{document}' in content

    def test_generate_latex_resume_validates_name(self, tmp_path):
        """Test that generation fails with missing name."""
        from models.bengt_resume import BengtResume
        from models.resume_header import ResumeHeader
        from models.extracted_skills import ExtractedSkills
        import pytest

        # Create resume with empty name
        header = ResumeHeader(
            name="",  # Empty name
            email="test@example.com",
            phone="",
            location="",
            linkedin="",
            github="",
            website="",
        )

        skills = ExtractedSkills(
            programming_languages=[],
            frameworks=[],
            tools=[],
        )

        resume = BengtResume.with_page_limit(
            header=header,
            experiences=[],
            education=[],
            projects=[],
            skills=skills,
            page_limit=1,
        )

        output_path = tmp_path / "invalid_resume.tex"

        # Should raise ValueError for missing name
        with pytest.raises(ValueError, match="name"):
            generate_latex_resume(resume, output_path)
