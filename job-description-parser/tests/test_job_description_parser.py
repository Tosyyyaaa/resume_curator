"""Unit tests for job_description_parser module.

This module contains comprehensive tests for the job description parser,
including argument parsing, Gemini API integration, validation, and file operations.
"""

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

from models.job_description import JobDescription


class TestParserArgumentParsing:
    """Test command-line argument parsing."""

    @patch("sys.argv", ["main.py", "--raw-file", "test.txt"])
    def test_parse_args_with_required_argument(self) -> None:
        """Verify parser accepts required --raw-file argument."""
        from main import parse_args

        args = parse_args()
        assert args.raw_file == "test.txt"

    @patch(
        "sys.argv",
        [
            "main.py",
            "--raw-file",
            "test.txt",
            "--output-dir",
            "custom/path",
        ],
    )
    def test_parse_args_with_optional_output_dir(self) -> None:
        """Verify parser accepts optional --output-dir argument."""
        from main import parse_args

        args = parse_args()
        assert args.raw_file == "test.txt"
        assert args.output_dir == "custom/path"

    @patch("sys.argv", ["main.py"])
    def test_parse_args_missing_required_argument(self) -> None:
        """Verify parser raises error when required argument is missing."""
        from main import parse_args

        with pytest.raises(SystemExit):
            parse_args()


class TestParserCore:
    """Test core parsing functionality."""

    def test_parse_job_description_with_mock_api(self) -> None:
        """Verify parser processes text and creates JobDescription using mocked API."""
        from main import parse_job_description_text

        mock_gemini_response: dict[str, Any] = {
            "job_description": "Test job posting for software engineer",
            "job_title": "Software Engineer",
            "job_location": "San Francisco, CA",
            "job_salary": "$120,000 - $150,000",
            "job_requirements": ["3+ years experience", "Python expertise"],
            "programming_languages": ["Python", "JavaScript"],
            "frameworks": ["Django", "React"],
            "tools": ["Git", "Docker"],
        }

        raw_text: str = "Test job posting for software engineer"

        with patch("utils.gemini_client.GeminiClient") as MockClient:
            mock_client: Mock = MockClient.return_value
            mock_client.generate_structured_json.return_value = mock_gemini_response

            result: JobDescription = parse_job_description_text(raw_text, mock_client)

            assert result.job_title == "Software Engineer"
            assert result.job_location == "San Francisco, CA"
            assert len(result.programming_languages) == 2
            mock_client.generate_structured_json.assert_called_once()

    def test_parse_job_description_handles_api_errors(self) -> None:
        """Verify parser handles API errors gracefully."""
        from main import parse_job_description_text

        raw_text: str = "Test job description"

        with patch("utils.gemini_client.GeminiClient") as MockClient:
            mock_client: Mock = MockClient.return_value
            mock_client.generate_structured_json.side_effect = Exception(
                "API Error: Rate limit exceeded"
            )

            with pytest.raises(Exception) as exc_info:
                parse_job_description_text(raw_text, mock_client)

            assert "API Error" in str(exc_info.value)


class TestFileOperations:
    """Test file reading and writing operations."""

    def test_read_raw_file(self) -> None:
        """Verify parser can read raw text files."""
        from main import read_raw_file

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file: Path = Path(tmpdir) / "test_job.txt"
            test_content: str = "Software Engineer position at Meta"

            with open(test_file, "w", encoding="utf-8") as f:
                f.write(test_content)

            result: str = read_raw_file(test_file)
            assert result == test_content

    def test_read_raw_file_not_found(self) -> None:
        """Verify parser handles missing input files."""
        from main import read_raw_file

        with pytest.raises(FileNotFoundError):
            read_raw_file(Path("nonexistent_file.txt"))

    def test_derive_output_filename(self) -> None:
        """Verify output filename is correctly derived from input filename."""
        from main import derive_output_filename

        input_path: Path = Path("job_descriptions/raw/meta_engineer.txt")
        output_dir: Path = Path("job_descriptions/parsed")

        result: Path = derive_output_filename(input_path, output_dir)

        assert result == Path("job_descriptions/parsed/meta_engineer.json")
        assert result.suffix == ".json"
        assert result.stem == input_path.stem

    def test_write_output_creates_directory(self) -> None:
        """Verify output directory is created if it doesn't exist."""
        from main import write_job_description

        job_desc: JobDescription = JobDescription(
            job_description="Test",
            job_title="Engineer",
            job_location="Remote",
            job_salary="$100k",
            job_requirements=["Python"],
            programming_languages=["Python"],
            frameworks=["Django"],
            tools=["Git"],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path: Path = Path(tmpdir) / "nested" / "dir" / "output.json"

            write_job_description(job_desc, output_path)

            assert output_path.exists()
            assert output_path.parent.exists()


class TestValidation:
    """Test validation to prevent hallucinated data."""

    def test_validate_extracted_data_all_valid(self) -> None:
        """Verify validation passes when all extracted data exists in source."""
        from main import validate_extracted_data

        source_text: str = (
            "We are hiring a Senior Python Engineer in London. "
            "Salary £100k. Must know Django and PostgreSQL."
        )

        job_desc: JobDescription = JobDescription(
            job_description=source_text,
            job_title="Senior Python Engineer",
            job_location="London",
            job_salary="£100k",
            job_requirements=["Must know Django and PostgreSQL"],
            programming_languages=["Python"],
            frameworks=["Django"],
            tools=["PostgreSQL"],
        )

        # Should not raise any exceptions
        issues: list[str] = validate_extracted_data(source_text, job_desc)
        assert len(issues) == 0

    def test_validate_extracted_data_detects_hallucinations(self) -> None:
        """Verify validation detects data not present in source text."""
        from main import validate_extracted_data

        source_text: str = "We need a software engineer."

        job_desc: JobDescription = JobDescription(
            job_description=source_text,
            job_title="software engineer",
            job_location="Mars",  # Not in source!
            job_salary="$1 million",  # Not in source!
            job_requirements=["10 years Martian experience"],  # Not in source!
            programming_languages=["Python"],
            frameworks=["Django"],
            tools=["Git"],
        )

        issues: list[str] = validate_extracted_data(source_text, job_desc)

        # Should detect multiple hallucinations
        assert len(issues) > 0
        assert any("Mars" in issue for issue in issues)


class TestEndToEndWorkflow:
    """Test complete parsing workflow."""

    def test_main_workflow_with_mocked_api(self) -> None:
        """Verify complete workflow from raw file to parsed JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup test files
            raw_dir: Path = Path(tmpdir) / "raw"
            parsed_dir: Path = Path(tmpdir) / "parsed"
            raw_dir.mkdir()

            raw_file: Path = raw_dir / "test_job.txt"
            raw_content: str = (
                "Software Engineer position at Google in Mountain View. "
                "Salary $150k-$200k. Requirements: Python, Go, 5 years experience. "
                "Tech stack includes Kubernetes and TensorFlow."
            )

            with open(raw_file, "w", encoding="utf-8") as f:
                f.write(raw_content)

            mock_response: dict[str, Any] = {
                "job_description": raw_content,
                "job_title": "Software Engineer",
                "job_location": "Mountain View",
                "job_salary": "$150k-$200k",
                "job_requirements": ["5 years experience"],
                "programming_languages": ["Python", "Go"],
                "frameworks": ["TensorFlow"],
                "tools": ["Kubernetes"],
            }

            with patch("utils.gemini_client.GeminiClient") as MockClient:
                mock_client: Mock = MockClient.return_value
                mock_client.generate_structured_json.return_value = mock_response

                from main import process_job_description

                output_file: Path = process_job_description(
                    raw_file, parsed_dir, mock_client
                )

                # Verify output file was created
                assert output_file.exists()
                assert output_file.parent == parsed_dir
                assert output_file.suffix == ".json"

                # Verify content is correct
                loaded: JobDescription = JobDescription.from_json_file(output_file)
                assert loaded.job_title == "Software Engineer"
                assert "Python" in loaded.programming_languages