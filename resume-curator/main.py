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
from models.pending_resume import PendingResume
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


def extract_experiences(candidate_data: CandidateData) -> list[ExtractedJobExperience]:
    """Extract all job experiences from candidate data.

    Args:
        candidate_data: Loaded candidate data

    Returns:
        List of ExtractedJobExperience instances
    """
    experiences = []

    # Add work experience
    for exp in candidate_data.experiences.get("work_experience", []):
        experiences.append(ExtractedJobExperience.from_experience_dict(exp))

    # Add internship experience
    for exp in candidate_data.experiences.get("internship_experience", []):
        experiences.append(ExtractedJobExperience.from_experience_dict(exp))

    # Add competitions
    for comp in candidate_data.experiences.get("competitions", []):
        experiences.append(
            ExtractedJobExperience.from_experience_dict(comp, is_competition=True)
        )

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


def extract_projects(candidate_data: CandidateData) -> list[ExtractedProject]:
    """Extract all projects from candidate data.

    Args:
        candidate_data: Loaded candidate data

    Returns:
        List of ExtractedProject instances
    """
    projects = []

    for proj in candidate_data.projects.get("projects", []):
        projects.append(ExtractedProject.from_project_dict(proj))

    return projects


def extract_skills(
    candidate_data: CandidateData, job_description: JobDescription
) -> ExtractedSkills:
    """Extract skills relevant to job description.

    For now, returns all skills from job description. Future enhancement:
    filter to only skills the candidate has mentioned in their data.

    Args:
        candidate_data: Loaded candidate data
        job_description: Parsed job description

    Returns:
        ExtractedSkills instance
    """
    # For now, just use skills from job description
    # Future: match against candidate's actual skills from experiences/projects
    return ExtractedSkills.from_lists(
        job_description.programming_languages,
        job_description.frameworks,
        job_description.tools,
    )


def generate_pending_resume(
    job_description: JobDescription,
    candidate_data: CandidateData,
    page_limit: int,
) -> PendingResume:
    """Generate a page-constrained resume from candidate data and job description.

    Args:
        job_description: Parsed job description
        candidate_data: Loaded candidate data
        page_limit: Maximum number of pages

    Returns:
        PendingResume instance that fits within page limit
    """
    # Extract all components
    header = extract_header(candidate_data)
    experiences = extract_experiences(candidate_data)
    education = extract_education(candidate_data)
    projects = extract_projects(candidate_data)
    skills = extract_skills(candidate_data, job_description)

    # Create PendingResume with page limit
    resume = PendingResume.with_page_limit(
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

    args = parser.parse_args()

    # Load job description
    try:
        job_description = JobDescription.from_json_file(args.job_description)
        print(f"Loaded job description: {job_description.job_title}")
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
    try:
        resume = generate_pending_resume(
            job_description, candidate_data, args.page_limit
        )

        print(f"\nResume Summary:")
        print(f"  Header: {resume.header.line_length} lines")
        print(f"  Experiences: {len(resume.experiences)} entries, {sum(e.line_length for e in resume.experiences)} lines")
        print(f"  Education: {len(resume.education)} entries, {sum(e.line_length for e in resume.education)} lines")
        print(f"  Projects: {len(resume.projects)} entries, {sum(p.line_length for p in resume.projects)} lines")
        print(f"  Skills: {resume.skills.line_length} lines")
        print(f"  Total: {resume.line_length} / {resume.permitted_line_length} lines")
        print(f"  Fits {args.page_limit} page(s): {resume.fits_page_limit()}")

        # TODO: Output formatting (currently just prints summary)
        if args.output_format != "json":
            print(f"\nNote: {args.output_format} formatting not yet implemented")
            print("Resume data structure is complete and ready for formatting")
            # Dump resume for now
        else:
            # Make dir resumes/json if it doesn't exist
            Path("resumes/json").mkdir(parents=True, exist_ok=True)
            with open(f"resumes/json/{job_description.job_title}.json", "w") as f:
                json.dump(resume.to_dict(), f, indent=4)

    except Exception as e:
        print(f"Error generating resume: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()