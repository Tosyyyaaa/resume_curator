"""Job description parser using Google's Gemini API.

This module parses raw job description text files and extracts structured
information into JSON format using Google's Gemini LLM. The parser validates
extracted data to prevent hallucinations and ensures all information exists
in the source text.

Usage:
    python3 job_description_parser.py --raw-file "path/to/job.txt"
    python3 job_description_parser.py --raw-file "path/to/job.txt" --output-dir "custom/dir"
"""

import argparse
import sys
from pathlib import Path
from typing import Any

from models.job_description import JobDescription
from utils.gemini_client import GeminiClient


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments with raw_file and optional output_dir

    Raises:
        SystemExit: If required arguments are missing
    """
    parser = argparse.ArgumentParser(
        description="Parse raw job descriptions into structured JSON using Gemini API"
    )

    parser.add_argument(
        "--raw-file",
        type=str,
        required=True,
        help="Path to raw job description text file",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="job_descriptions/parsed",
        help="Output directory for parsed JSON (default: job_descriptions/parsed)",
    )

    return parser.parse_args()


def read_raw_file(filepath: Path | str) -> str:
    """Read raw job description text file.

    Args:
        filepath: Path to text file

    Returns:
        Content of the file as string

    Raises:
        FileNotFoundError: If file does not exist
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def derive_output_filename(input_path: Path, output_dir: Path | str) -> Path:
    """Derive output filename from input filename.

    Args:
        input_path: Path to input text file
        output_dir: Directory for output files

    Returns:
        Path for output JSON file with same stem as input
    """
    output_dir = Path(output_dir)
    return output_dir / f"{input_path.stem}.json"


def create_extraction_prompt(raw_text: str) -> str:
    """Create prompt for Gemini API to extract job description fields.

    Args:
        raw_text: Raw job description text

    Returns:
        Formatted prompt string
    """
    return f"""Extract job posting information from the following text and return ONLY valid JSON matching this exact structure:

{{
  "job_description": "full description text",
  "job_title": "title",
  "job_location": "location",
  "job_salary": "salary or 'N/A'",
  "job_requirements": ["req1", "req2"],
  "programming_languages": ["lang1", "lang2"],
  "frameworks": ["framework1"],
  "tools": ["tool1"]
}}

CRITICAL INSTRUCTIONS:
1. Only extract information explicitly stated in the text
2. Do not infer, assume, or add information not present in the source
3. Use empty lists [] if no items are found in a category
4. Use "N/A" for job_salary if not specified
5. For job_description, include the full text or a comprehensive summary
6. Extract only concrete requirements, not vague statements

CATEGORIZATION GUIDELINES:
- programming_languages: Core programming languages (e.g., Python, Java, JavaScript, C++, Go, Rust, TypeScript, SQL)
- frameworks: Software frameworks and libraries built on top of languages (e.g., React, Django, Flask, TensorFlow, PyTorch, Spring, Angular, Vue.js, FastAPI, Express.js, Scikit-learn)
- tools: Development tools, platforms, and infrastructure (e.g., Git, Docker, Kubernetes, AWS, Azure, Jenkins, PostgreSQL, MongoDB, Redis, Terraform, Linux)

Job posting text:
{raw_text}"""


def parse_job_description_text(
    raw_text: str, gemini_client: GeminiClient | None = None
) -> JobDescription:
    """Parse raw job description text using Gemini API.

    Args:
        raw_text: Raw job description text to parse
        gemini_client: Optional GeminiClient instance (creates new one if None)

    Returns:
        JobDescription instance with extracted data

    Raises:
        Exception: If API request fails or response is invalid
    """
    if gemini_client is None:
        gemini_client = GeminiClient()

    prompt: str = create_extraction_prompt(raw_text)

    # Generate structured JSON response
    response_data: dict[str, Any] = gemini_client.generate_structured_json(
        prompt=prompt, temperature=0.1
    )

    # Create JobDescription from response
    job_description: JobDescription = JobDescription.from_dict(response_data)

    return job_description


def validate_extracted_data(source_text: str, job_desc: JobDescription) -> list[str]:
    """Validate that extracted data exists in source text.

    This function performs substring matching to detect potential hallucinations
    where the LLM may have generated information not present in the source.

    Args:
        source_text: Original job description text
        job_desc: Extracted JobDescription instance

    Returns:
        List of validation issues (empty if all data is valid)
    """
    issues: list[str] = []
    source_lower: str = source_text.lower()

    # Validate job title
    if job_desc.job_title and job_desc.job_title.lower() not in source_lower:
        issues.append(f"Job title '{job_desc.job_title}' not found in source text")

    # Validate location (skip if "N/A" or "Remote")
    if (
        job_desc.job_location
        and job_desc.job_location not in ["N/A", "Remote"]
        and job_desc.job_location.lower() not in source_lower
    ):
        issues.append(
            f"Job location '{job_desc.job_location}' not found in source text"
        )

    # Validate salary (skip if "N/A")
    if (
        job_desc.job_salary
        and job_desc.job_salary != "N/A"
        and job_desc.job_salary.lower() not in source_lower
    ):
        # Check without currency symbols and formatting
        salary_digits: str = "".join(filter(str.isdigit, job_desc.job_salary))
        source_digits: str = "".join(filter(str.isdigit, source_text))

        if salary_digits and salary_digits not in source_digits:
            issues.append(
                f"Job salary '{job_desc.job_salary}' not found in source text"
            )

    # Validate requirements (sample check - don't check every word)
    for req in job_desc.job_requirements[:5]:  # Check first 5 requirements
        # Check if at least some key words from requirement exist
        req_words: list[str] = req.lower().split()
        key_words: list[str] = [w for w in req_words if len(w) > 3]

        if key_words:
            found_words: int = sum(1 for word in key_words if word in source_lower)
            if found_words < len(key_words) * 0.5:  # At least 50% of words should match
                issues.append(f"Requirement '{req}' may not be in source text")

    # Validate programming languages
    for lang in job_desc.programming_languages:
        if lang.lower() not in source_lower:
            issues.append(f"Programming language '{lang}' not found in source text")

    # Validate frameworks
    for framework in job_desc.frameworks:
        if framework.lower() not in source_lower:
            issues.append(f"Framework '{framework}' not found in source text")

    # Validate tools
    for tool in job_desc.tools:
        if tool.lower() not in source_lower:
            issues.append(f"Tool '{tool}' not found in source text")

    return issues


def write_job_description(job_desc: JobDescription, output_path: Path | str) -> None:
    """Write JobDescription to JSON file.

    Args:
        job_desc: JobDescription instance to write
        output_path: Path for output JSON file
    """
    job_desc.to_json_file(output_path)


def process_job_description(
    raw_file: Path | str,
    output_dir: Path | str,
    gemini_client: GeminiClient | None = None,
) -> Path:
    """Process a raw job description file end-to-end.

    Args:
        raw_file: Path to raw text file
        output_dir: Directory for output JSON
        gemini_client: Optional GeminiClient instance

    Returns:
        Path to generated JSON file

    Raises:
        FileNotFoundError: If input file not found
        Exception: If parsing or validation fails
    """
    raw_file = Path(raw_file)
    output_dir = Path(output_dir)

    print(f"Reading raw job description from: {raw_file}")
    raw_text: str = read_raw_file(raw_file)

    print("Parsing job description using Gemini API...")
    job_description: JobDescription = parse_job_description_text(raw_text, gemini_client)

    print("Validating extracted data...")
    validation_issues: list[str] = validate_extracted_data(raw_text, job_description)

    if validation_issues:
        print(f"\n⚠️  WARNING: Found {len(validation_issues)} potential validation issues:")
        for issue in validation_issues[:10]:  # Show first 10 issues
            print(f"  - {issue}")

        if len(validation_issues) > 10:
            print(f"  ... and {len(validation_issues) - 10} more issues")

        response: str = input("\nProceed anyway? (y/n): ").lower().strip()
        if response != "y":
            print("Aborted by user")
            sys.exit(1)

    output_file: Path = derive_output_filename(raw_file, output_dir)

    print(f"Writing parsed job description to: {output_file}")
    write_job_description(job_description, output_file)

    print("✅ Successfully parsed job description!")
    return output_file


def main() -> None:
    """Main entry point for job description parser."""
    args = parse_args()

    try:
        gemini_client: GeminiClient = GeminiClient()

        output_file: Path = process_job_description(
            raw_file=args.raw_file,
            output_dir=args.output_dir,
            gemini_client=gemini_client,
        )

        print(f"\nOutput: {output_file}")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

    except ValueError as e:
        print(f"❌ Configuration Error: {e}", file=sys.stderr)
        print("Make sure GEMINI_API_KEY is set in .env file", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()