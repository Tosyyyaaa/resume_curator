"""LaTeX resume generator using resume-openfont template format.

This module converts PendingResume data structures into LaTeX documents
using a template-based approach with text replacement.
"""

import sys
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from models.base_resume import BaseResume

# Template base directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "latex"


def get_template_path(template_name: str = "bengt") -> Path:
    """Get the path to the template file for the given template name.

    Args:
        template_name: Name of the template (e.g., "bengt", "deedy")

    Returns:
        Path to the template_with_placeholders.tex file

    Raises:
        ValueError: If template name is invalid or template file doesn't exist
    """
    template_path = TEMPLATES_DIR / template_name / "template_with_placeholders.tex"

    if not template_path.exists():
        raise ValueError(f"Template not found: {template_name} (looked in {template_path})")

    return template_path


def _escape_latex(text: str) -> str:
    r"""Escape special LaTeX characters in user data.

    Escapes the following characters to prevent LaTeX compilation errors:
    & % $ # _ { } ~ ^ \

    Args:
        text: Raw text string that may contain special LaTeX characters

    Returns:
        String with all special LaTeX characters properly escaped

    Examples:
        >>> _escape_latex("AT&T")
        'AT\\&T'
        >>> _escape_latex("100% complete")
        '100\\% complete'
        >>> _escape_latex("Cost: $50")
        'Cost: \\$50'
    """
    # Use a placeholder for backslash that won't conflict
    # Replace backslash first with a unique placeholder
    BACKSLASH_PLACEHOLDER = "<<<BACKSLASH>>>"
    result = text.replace('\\', BACKSLASH_PLACEHOLDER)

    # Replace other special characters
    replacements = [
        ('&', r'\&'),
        ('%', r'\%'),
        ('$', r'\$'),
        ('#', r'\#'),
        ('_', r'\_'),
        ('{', r'\{'),
        ('}', r'\}'),
        ('~', r'\~{}'),
        ('^', r'\^{}'),
    ]

    for char, escaped in replacements:
        result = result.replace(char, escaped)

    # Finally replace the placeholder with the backslash command
    result = result.replace(BACKSLASH_PLACEHOLDER, r'\textbackslash{}')

    return result


def _extract_profile_data(header: "ResumeHeader") -> dict[str, str]:
    """Extract profile data for template placeholders.

    Args:
        header: ResumeHeader instance with personal information

    Returns:
        Dictionary with profile placeholder values
    """
    from models.resume_header import ResumeHeader

    # Extract and escape profile data from typed header
    name = _escape_latex(header.name)
    email = _escape_latex(header.email)
    phone = _escape_latex(header.phone)

    # Extract username from URLs if full URLs provided
    github = header.github.replace('https://github.com/', '') if header.github else ''
    linkedin = header.linkedin.replace('https://www.linkedin.com/in/', '') if header.linkedin else ''

    return {
        '{{NAME}}': name,
        '{{EMAIL}}': email,
        '{{PHONE}}': phone,
        '{{GITHUB}}': github,
        '{{LINKEDIN}}': linkedin
    }


def _build_education_section(education: list["ExtractedEducation"]) -> str:
    """Build education section content using educationHeading commands.

    Generates education entries without section headers (template has those).

    Args:
        education: List of ExtractedEducation instances

    Returns:
        LaTeX string for education entries
    """
    from models.extracted_education import ExtractedEducation

    if not education:
        return ""

    edu_latex = ""

    for edu in education:
        school = _escape_latex(edu.school)
        degree = _escape_latex(edu.degree)
        start_date = _escape_latex(edu.start_date)
        end_date = _escape_latex(edu.end_date)
        grade = edu.grade
        courses = edu.courses
        location = _escape_latex(edu.location) if edu.location else ''

        dates = f"{start_date} - {end_date}" if start_date and end_date else ""

        # Add grade to degree title if available
        if grade:
            grade_escaped = _escape_latex(str(grade))
            degree_with_grade = f"{degree} ({grade_escaped})"
        else:
            degree_with_grade = degree

        # Build educationHeading: {degree}{school}{location}{dates}
        edu_latex += f"\\educationHeading{{{degree_with_grade}}}{{{school}}}{{{location}}}{{{dates}}}\n"

        # Add courses if available
        if courses:
            course_list = ", ".join([_escape_latex(c) for c in courses])
            edu_latex += f"\\modules{{{course_list}}} \\newline\n\n"

        edu_latex += "\\sectionsep\n\n"

    return edu_latex


def _build_experience_section(experiences: list["ExtractedJobExperience"]) -> str:
    """Build work experience section content using resumeHeading and bullets environment.

    Generates experience entries without section headers (template has those).
    Experiences are already sorted by relevance score.

    Args:
        experiences: List of ExtractedJobExperience instances

    Returns:
        LaTeX string for experience entries
    """
    from models.extracted_experience import ExtractedJobExperience

    if not experiences:
        return ""

    exp_latex = ""

    for exp in experiences:
        company = _escape_latex(exp.company)
        title = _escape_latex(exp.title)
        start_date = _escape_latex(exp.start_date)
        end_date = _escape_latex(exp.end_date)
        bullets = exp.description_bullets
        location = _escape_latex(exp.location) if exp.location else ''

        # Build date range
        dates = f"{start_date} - {end_date}" if start_date and end_date else ""

        # Build resumeHeading: {company}{title}{location}{dates}
        exp_latex += f"\\resumeHeading{{{company}}}{{{title}}}{{{location}}}{{{dates}}}\n"

        # Add bullet points if available
        if bullets:
            exp_latex += "\\begin{bullets}\n"
            for bullet in bullets:
                bullet_escaped = _escape_latex(bullet)
                exp_latex += f"    \\item {bullet_escaped}\n"
            exp_latex += "\\end{bullets}\n"

        exp_latex += "\\sectionsep\n"

    return exp_latex


def _build_projects_section(projects: list["ExtractedProject"]) -> str:
    """Build projects section content using projectHeading commands.

    Generates project entries without section headers (template has those).
    Projects are already sorted by relevance score.

    Args:
        projects: List of ExtractedProject instances

    Returns:
        LaTeX string for project entries
    """
    from models.extracted_project import ExtractedProject

    if not projects:
        return ""

    proj_latex = ""

    for proj in projects:
        name = _escape_latex(proj.name)
        description = _escape_latex(proj.description)

        # Generate a placeholder GitHub link (template expects a link)
        link = "https://github.com/user/project"

        # Use empty tech stack (template parameter - could extract from description)
        tech = ""

        # Build projectHeading: {name}{link}{tech}
        proj_latex += f"\\projectHeading{{{name}}}{{{link}}}{{{tech}}}\n"

        # Add description text
        if description:
            proj_latex += f"{description}\n"

        proj_latex += "\\sectionsep\n\n"

    return proj_latex


def _extract_skills_data(skills: "ExtractedSkills") -> dict[str, str]:
    """Extract skills data for template placeholders.

    Character limits (CANNOT wrap to multiple lines):
    - Languages: 52 chars
    - Frameworks: 50 chars
    - Web Development: 40 chars
    - Tools: 48 chars

    Args:
        skills: ExtractedSkills instance

    Returns:
        Dictionary with skills placeholder values
    """
    from models.extracted_skills import ExtractedSkills

    prog_langs = skills.programming_languages
    frameworks = skills.frameworks
    tools = skills.tools

    # Build comma-separated lists
    langs_str = ", ".join([_escape_latex(lang) for lang in prog_langs]) if prog_langs else ""
    frameworks_str = ", ".join([_escape_latex(fw) for fw in frameworks]) if frameworks else ""
    tools_str = ", ".join([_escape_latex(tool) for tool in tools]) if tools else ""

    return {
        '{{SKILLS_ROW1_LEFT_LABEL}}': 'Languages:',
        '{{SKILLS_ROW1_LEFT_VALUE}}': langs_str,
        '{{SKILLS_ROW1_RIGHT_LABEL}}': 'Frameworks:',
        '{{SKILLS_ROW1_RIGHT_VALUE}}': frameworks_str,
        '{{SKILLS_ROW2_LEFT_LABEL}}': 'Web Development:',
        '{{SKILLS_ROW2_LEFT_VALUE}}': '',  # Empty for now, can be populated from skills data
        '{{SKILLS_ROW2_RIGHT_LABEL}}': 'Tools:',
        '{{SKILLS_ROW2_RIGHT_VALUE}}': tools_str
    }


def generate_latex_resume(resume: "BaseResume", output_path: Path) -> None:
    """Generate LaTeX resume from BaseResume using template-based replacement.

    Reads template, replaces placeholders with resume data, and writes output.
    Template is determined by the resume's template_name property.

    Args:
        resume: BaseResume instance (BengtResume, DeedyResume, etc.) with optimized content
        output_path: Path to write .tex file (e.g., resumes/latex/job_title.tex)

    Raises:
        ValueError: If resume data is invalid or template not found
        IOError: If file reading/writing fails
    """
    # Validate required fields
    if not resume.header.name:
        raise ValueError("Resume header must contain a name")

    # Get template path from resume's template_name
    template_path = get_template_path(resume.template_name)

    # Read template file
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            latex_content = f.read()
    except IOError as e:
        raise IOError(f"Failed to read template file from {template_path}: {e}")

    # Build replacement dictionary using typed resume components
    replacements = {}

    # Add profile data from typed header
    replacements.update(_extract_profile_data(resume.header))

    # Add section content from typed components
    replacements['{{EDUCATION_SECTION}}'] = _build_education_section(resume.education)
    replacements['{{EXPERIENCE_SECTION}}'] = _build_experience_section(resume.experiences)
    replacements['{{PROJECTS_SECTION}}'] = _build_projects_section(resume.projects)

    # Add skills data from typed skills
    replacements.update(_extract_skills_data(resume.skills))

    # Replace all placeholders
    for placeholder, value in replacements.items():
        latex_content = latex_content.replace(placeholder, value)

    # Write to file
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
    except IOError as e:
        raise IOError(f"Failed to write LaTeX file to {output_path}: {e}")
