"""Resume curator main entry point.

This module provides CLI functionality to generate page-constrained resumes
from candidate data and job descriptions.
"""

import argparse
import importlib.util
import sys
import json
from pathlib import Path

# Import local models
sys.path.insert(0, str(Path(__file__).parent))
from models.candidate_data import CandidateData
from models.extracted_education import ExtractedEducation
from models.extracted_experience import ExtractedJobExperience
from models.extracted_project import ExtractedProject
from models.extracted_skills import ExtractedSkills
from models.base_resume import BaseResume
from models.resume_header import ResumeHeader

# Import JobDescription from job-description-parser using direct file import
jd_path = Path(__file__).parent.parent / "job-description-parser" / "models" / "job_description.py"
spec = importlib.util.spec_from_file_location("job_description_module", jd_path)
jd_module = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(jd_module)  # type: ignore
JobDescription = jd_module.JobDescription


def extract_header(candidate_data: CandidateData) -> ResumeHeader:
    """Extract resume header from candidate metadata.

    Args:
        candidate_data: Loaded candidate data

    Returns:
        ResumeHeader instance
    """
    return ResumeHeader.from_metadata(candidate_data.metadata)


def _parse_end_date_for_sorting(end_date: str) -> int:
    """Parse end date string to integer for chronological sorting.

    Args:
        end_date: End date string (e.g., "2024", "Present", "2024 - 2025")

    Returns:
        Integer representing the date for sorting (higher = more recent)
        "Present" returns 9999 to always sort first
    """
    # Handle "Present" as the most recent
    if end_date.lower() in ["present", "current"]:
        return 9999

    # Extract year from string (handles formats like "2024" or "2024 - 2025")
    # Take the last year mentioned (for ranges)
    try:
        # Split on common separators and take the last part
        parts = end_date.replace("-", " ").replace("/", " ").split()
        # Find the last 4-digit number that looks like a year
        for part in reversed(parts):
            if part.isdigit() and len(part) == 4:
                return int(part)
        # Fallback: try to parse as integer
        return int(end_date)
    except (ValueError, AttributeError):
        # If parsing fails, return 0 (oldest)
        return 0


def extract_experiences(
    candidate_data: CandidateData, job_description: JobDescription, use_llm: bool = True
) -> list[ExtractedJobExperience]:
    """Extract all job experiences from candidate data, sorted chronologically.

    Args:
        candidate_data: Loaded candidate data
        job_description: Parsed job description with requirements
        use_llm: Whether to use LLM optimization for long bullets (default: True)

    Returns:
        List of ExtractedJobExperience instances sorted by end_date (descending - most recent first)
    """
    experiences = []

    # Add work experience
    for exp in candidate_data.experiences.get("work_experience", []):
        experiences.append(
            ExtractedJobExperience.from_experience_dict_with_score(exp, job_description)
        )

    # Add internship experience
    for exp in candidate_data.experiences.get("internship_experience", []):
        experiences.append(
            ExtractedJobExperience.from_experience_dict_with_score(exp, job_description)
        )

    # Add competitions
    for comp in candidate_data.experiences.get("competitions", []):
        experiences.append(
            ExtractedJobExperience.from_experience_dict_with_score(
                comp, job_description, is_competition=True
            )
        )

    # Sort by relevance score first (for filtering/selection during optimization)
    experiences.sort(key=lambda e: e.relevance_score, reverse=True)

    # Optimize bullets with LLM if enabled and needed
    if use_llm:
        for exp in experiences:
            if len(exp.description_bullets) > 1 or any(len(desc) > 100 for desc in exp.description_bullets):
                exp.optimize_bullets_with_llm(max_chars_per_bullet=100)

    return experiences


def extract_education(candidate_data: CandidateData) -> list[ExtractedEducation]:
    """Extract all education entries from candidate data.

    Args:
        candidate_data: Loaded candidate data

    Returns:
        List of ExtractedEducation instances
    """
    education = []

    # Add university education
    for edu in candidate_data.education.get("university_education", []):
        education.append(ExtractedEducation.from_education_dict(edu))

    # Add high school education
    for edu in candidate_data.education.get("high_school_education", []):
        education.append(ExtractedEducation.from_education_dict(edu))

    # Add other education
    for edu in candidate_data.education.get("other_education", []):
        education.append(ExtractedEducation.from_education_dict(edu))

    return education


def extract_projects(
    candidate_data: CandidateData, job_description: JobDescription, use_llm: bool = True
) -> list[ExtractedProject]:
    """Extract all projects from candidate data, ranked by relevance.

    Args:
        candidate_data: Loaded candidate data
        job_description: Parsed job description with requirements
        use_llm: Whether to use LLM optimization for long descriptions (default: True)

    Returns:
        List of ExtractedProject instances sorted by relevance_score (descending)
    """
    projects = []

    for proj in candidate_data.projects.get("projects", []):
        projects.append(
            ExtractedProject.from_project_dict_with_score(proj, job_description)
        )

    # Sort by relevance score (descending), maintaining relative order for same scores
    projects.sort(key=lambda p: p.relevance_score, reverse=True)

    # Optimize descriptions with LLM if enabled and needed
    if use_llm:
        for proj in projects:
            if len(proj.description) > 1 or any(len(desc) > 116 for desc in proj.description):
                proj.optimize_description_with_llm(max_chars=116)

    return projects


def extract_skills(
    candidate_data: CandidateData, job_description: JobDescription
) -> ExtractedSkills:
    """Extract skills relevant to job description.

    If job description doesn't specify skills, greedily takes first 3 items
    from each category found in candidate's experiences.

    Args:
        candidate_data: Loaded candidate data
        job_description: Parsed job description

    Returns:
        ExtractedSkills instance
    """
    # Get skills from job description
    languages = job_description.programming_languages or []
    frameworks = job_description.frameworks or []
    tools = job_description.tools or []

    # If job description has empty lists, greedily extract from candidate experiences
    if not languages or not frameworks or not tools:
        # Collect all skills from candidate's experiences
        all_languages = set()
        all_frameworks = set()
        all_tools = set()

        for exp in candidate_data.experiences.get("work_experience", []):
            all_languages.update(exp.get("languages", []))
            all_frameworks.update(exp.get("frameworks", []))
            all_tools.update(exp.get("tools", []))

        for exp in candidate_data.experiences.get("internship_experience", []):
            all_languages.update(exp.get("languages", []))
            all_frameworks.update(exp.get("frameworks", []))
            all_tools.update(exp.get("tools", []))

        # Take first 3 from each category if job description didn't specify
        if not languages:
            languages = list(all_languages)[:3]
        if not frameworks:
            frameworks = list(all_frameworks)[:3]
        if not tools:
            tools = list(all_tools)[:3]

    # Get spoken languages from metadata
    spoken_languages = candidate_data.metadata.get("spoken_languages", [])

    return ExtractedSkills.from_lists(languages, frameworks, tools, spoken_languages)


def create_resume_for_template(
    template_name: str,
    header: ResumeHeader,
    experiences: list[ExtractedJobExperience],
    education: list[ExtractedEducation],
    projects: list[ExtractedProject],
    skills: ExtractedSkills,
    page_limit: int,
) -> BaseResume:
    """Factory function to create template-specific resume instance.

    Args:
        template_name: Name of template ('bengt', 'deedy', etc.)
        header: Resume header with personal information
        experiences: List of job experiences
        education: List of education entries
        projects: List of projects
        skills: Skills section
        page_limit: Maximum number of pages allowed

    Returns:
        BaseResume subclass instance (BengtResume, DeedyResume, etc.)

    Raises:
        ValueError: If template_name is not recognized
    """
    if template_name == "bengt":
        from models.bengt_resume import BengtResume
        return BengtResume.with_page_limit(
            header=header,
            experiences=experiences,
            education=education,
            projects=projects,
            skills=skills,
            page_limit=page_limit,
        )
    elif template_name == "deedy":
        from models.deedy_resume import DeedyResume
        return DeedyResume.with_page_limit(
            header=header,
            experiences=experiences,
            education=education,
            projects=projects,
            skills=skills,
            page_limit=page_limit,
        )
    else:
        raise ValueError(f"Unknown template: {template_name}")


def generate_pending_resume(
    job_description: JobDescription,
    candidate_data: CandidateData,
    page_limit: int,
    template_name: str = "bengt",
    use_llm: bool = True,
) -> BaseResume:
    """Generate a page-constrained resume from candidate data and job description.

    Args:
        job_description: Parsed job description
        candidate_data: Loaded candidate data
        page_limit: Maximum number of pages
        template_name: Template to use ('bengt', 'deedy', etc.)
        use_llm: Whether to use LLM optimization for long bullets (default: True)

    Returns:
        BaseResume instance (template-specific) that fits within page limit
    """
    # Extract all components
    header = extract_header(candidate_data)
    experiences = extract_experiences(candidate_data, job_description, use_llm=use_llm)
    education = extract_education(candidate_data)
    projects = extract_projects(candidate_data, job_description, use_llm=use_llm)
    skills = extract_skills(candidate_data, job_description)

    # Create template-specific resume with page limit using factory
    resume = create_resume_for_template(
        template_name=template_name,
        header=header,
        experiences=experiences,
        education=education,
        projects=projects,
        skills=skills,
        page_limit=page_limit,
    )

    # Optimize to fit if needed
    if not resume.fits_page_limit():
        print(
            f"Resume exceeds {page_limit} page(s) ({resume.line_length} lines > {resume.permitted_line_length} lines)"
        )
        print("Optimizing to fit...")
        resume.optimize_to_fit()

        if resume.fits_page_limit():
            print(
                f"Successfully optimized to {resume.line_length} lines (fits {page_limit} page(s))"
            )
        else:
            print(
                f"Warning: Could not fit resume within {page_limit} page(s) "
                f"({resume.line_length} lines > {resume.permitted_line_length} lines)"
            )

    # Sort experiences chronologically (most recent first) for final display
    # This happens AFTER optimization so we keep the most relevant ones
    resume.experiences.sort(
        key=lambda e: _parse_end_date_for_sorting(e.end_date), reverse=True
    )

    return resume


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate page-constrained resumes from candidate data"
    )
    parser.add_argument(
        "--job-description",
        required=True,
        help="Path to parsed job description JSON file",
    )
    parser.add_argument(
        "--candidate-data",
        default="../candidate_data",
        help="Path to candidate data directory (default: ../candidate_data)",
    )
    parser.add_argument(
        "--page-limit",
        type=int,
        default=1,
        help="Maximum number of pages (default: 1)",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "latex", "markdown"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--template-name",
        choices=["bengt", "deedy"],
        default="bengt",
        help="LaTeX template name to use (default: bengt)",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM-based bullet point optimization (for offline use)",
    )

    args = parser.parse_args()

    # Load job description
    try:
        job_description = JobDescription.from_json_file(args.job_description)
        print(f"Loaded job description: {job_description.job_title}")

        # Extract job description filename (without extension) for output naming
        job_desc_filename = Path(args.job_description).stem
    except Exception as e:
        print(f"Error loading job description: {e}", file=sys.stderr)
        sys.exit(1)

    # Load candidate data
    try:
        candidate_data = CandidateData.load_from_directory(args.candidate_data)
        print(f"Loaded candidate data for: {candidate_data.metadata['name']}")
    except Exception as e:
        print(f"Error loading candidate data: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate resume
    use_llm = not args.no_llm
    if not use_llm:
        print("LLM optimization disabled (running in offline mode)")

    try:
        resume = generate_pending_resume(
            job_description, candidate_data, args.page_limit, args.template_name, use_llm=use_llm
        )

        print(f"\nResume Summary:")
        print(f"  Header: {resume.header.line_length} lines")
        print(f"  Experiences: {len(resume.experiences)} entries, {sum(e.line_length for e in resume.experiences)} lines")
        print(f"  Education: {len(resume.education)} entries, {sum(e.line_length for e in resume.education)} lines")
        print(f"  Projects: {len(resume.projects)} entries, {sum(p.line_length for p in resume.projects)} lines")
        print(f"  Skills: {resume.skills.line_length} lines")
        print(f"  Total: {resume.line_length} / {resume.permitted_line_length} lines")
        print(f"  Fits {args.page_limit} page(s): {resume.fits_page_limit()}")

        # Output formatting
        if args.output_format == "json":
            # Make dir resumes/json if it doesn't exist
            Path("resumes/json").mkdir(parents=True, exist_ok=True)
            output_path = Path(f"resumes/json/{job_desc_filename}.json")
            with open(output_path, "w") as f:
                json.dump(resume.to_dict(), f, indent=4)
            print(f"Resume saved to: {output_path.resolve()}")

        elif args.output_format == "latex":
            # Import LaTeX generator
            from utils.latex_generator import generate_latex_resume

            # Create output directory
            output_dir = Path("resumes/latex")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{job_desc_filename}.tex"

            try:
                # Resume already knows its template name, no need to pass it
                generate_latex_resume(resume, output_path)
                print(f"LaTeX resume saved to: {output_path.resolve()} (template: {resume.template_name})")
            except ValueError as e:
                print(f"Error: Invalid resume data: {e}", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Error generating LaTeX: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()
                sys.exit(1)

        else:
            # Markdown or other formats (future)
            print(f"\nNote: {args.output_format} formatting not yet implemented")
            print("Resume data structure is complete and ready for formatting")

    except Exception as e:
        print(f"Error generating resume: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()