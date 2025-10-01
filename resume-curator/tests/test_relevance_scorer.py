"""Tests for relevance scoring functionality.

This module tests the relevance scoring system that matches candidate
experiences and projects against job description requirements.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.relevance_scorer import calculate_experience_score, calculate_project_score


class MockJobDescription:
    """Mock job description for testing."""

    def __init__(self, languages=None, frameworks=None, tools=None):
        self.programming_languages = languages or []
        self.frameworks = frameworks or []
        self.tools = tools or []


def test_perfect_match_experience():
    """Test experience with all languages, frameworks, and tools matching."""
    job_desc = MockJobDescription(
        languages=["Python", "JavaScript"],
        frameworks=["React", "Django"],
        tools=["Git", "Docker"],
    )

    experience = {
        "languages": ["Python", "JavaScript"],
        "frameworks": ["React", "Django"],
        "tools": ["Git", "Docker"],
    }

    score = calculate_experience_score(experience, job_desc)
    assert score == 6, "Perfect match should score 6 points (2+2+2)"


def test_partial_match_experience():
    """Test experience with some overlap in requirements."""
    job_desc = MockJobDescription(
        languages=["Python", "JavaScript", "Java"],
        frameworks=["React", "Django", "Flask"],
        tools=["Git", "Docker", "Kubernetes"],
    )

    experience = {
        "languages": ["Python", "Rust"],
        "frameworks": ["React"],
        "tools": ["Git", "AWS"],
    }

    score = calculate_experience_score(experience, job_desc)
    assert score == 3, "Partial match should score 3 points (1+1+1)"


def test_no_match_experience():
    """Test experience with no overlap in requirements."""
    job_desc = MockJobDescription(
        languages=["Python", "JavaScript"],
        frameworks=["React", "Django"],
        tools=["Git", "Docker"],
    )

    experience = {
        "languages": ["Rust", "Go"],
        "frameworks": ["Tokio", "Gin"],
        "tools": ["Podman", "Jenkins"],
    }

    score = calculate_experience_score(experience, job_desc)
    assert score == 0, "No match should score 0 points"


def test_case_insensitive_matching():
    """Test that matching is case-insensitive."""
    job_desc = MockJobDescription(
        languages=["python", "javascript"],
        frameworks=["react", "django"],
        tools=["git", "docker"],
    )

    experience = {
        "languages": ["Python", "JavaScript"],
        "frameworks": ["React", "Django"],
        "tools": ["Git", "Docker"],
    }

    score = calculate_experience_score(experience, job_desc)
    assert score == 6, "Case-insensitive match should score 6 points"


def test_empty_arrays_experience():
    """Test handling of empty arrays in experience."""
    job_desc = MockJobDescription(
        languages=["Python"],
        frameworks=["Django"],
        tools=["Git"],
    )

    experience = {
        "languages": [],
        "frameworks": [],
        "tools": [],
    }

    score = calculate_experience_score(experience, job_desc)
    assert score == 0, "Empty arrays should score 0 points"


def test_empty_job_requirements():
    """Test handling of empty job requirements."""
    job_desc = MockJobDescription(
        languages=[],
        frameworks=[],
        tools=[],
    )

    experience = {
        "languages": ["Python"],
        "frameworks": ["Django"],
        "tools": ["Git"],
    }

    score = calculate_experience_score(experience, job_desc)
    assert score == 0, "Empty job requirements should score 0 points"


def test_missing_fields_experience():
    """Test handling of missing fields in experience dictionary."""
    job_desc = MockJobDescription(
        languages=["Python"],
        frameworks=["Django"],
        tools=["Git"],
    )

    # Experience missing frameworks field
    experience = {
        "languages": ["Python"],
        "tools": ["Git"],
    }

    score = calculate_experience_score(experience, job_desc)
    assert score == 2, "Missing field should be treated as empty and score 2 points"


def test_perfect_match_project():
    """Test project with all languages, frameworks, and tools matching."""
    job_desc = MockJobDescription(
        languages=["Python", "JavaScript"],
        frameworks=["React", "PyTorch"],
        tools=["Git", "Docker"],
    )

    project = {
        "languages": ["Python", "JavaScript"],
        "frameworks": ["React", "PyTorch"],
        "tools": ["Git", "Docker"],
    }

    score = calculate_project_score(project, job_desc)
    assert score == 6, "Perfect match should score 6 points"


def test_partial_match_project():
    """Test project with some overlap in requirements."""
    job_desc = MockJobDescription(
        languages=["Python", "JavaScript"],
        frameworks=["PyTorch", "TensorFlow"],
        tools=["Git", "Docker"],
    )

    project = {
        "languages": ["Python"],
        "frameworks": ["PyTorch", "Keras"],
        "tools": ["Git"],
    }

    score = calculate_project_score(project, job_desc)
    assert score == 3, "Partial match should score 3 points (1+1+1)"


def test_no_match_project():
    """Test project with no overlap in requirements."""
    job_desc = MockJobDescription(
        languages=["Python"],
        frameworks=["PyTorch"],
        tools=["Git"],
    )

    project = {
        "languages": ["JavaScript"],
        "frameworks": ["React"],
        "tools": ["NPM"],
    }

    score = calculate_project_score(project, job_desc)
    assert score == 0, "No match should score 0 points"


def test_duplicate_matches_counted_once():
    """Test that duplicate entries in candidate data only count once per match."""
    job_desc = MockJobDescription(
        languages=["Python"],
        frameworks=["Django"],
        tools=["Git"],
    )

    # Candidate has duplicates
    experience = {
        "languages": ["Python", "Python", "Python"],
        "frameworks": ["Django", "Django"],
        "tools": ["Git"],
    }

    score = calculate_experience_score(experience, job_desc)
    # Each requirement should only be counted once even if candidate lists it multiple times
    assert score == 3, "Duplicates should still only score once per unique job requirement match"


def test_whitespace_handling():
    """Test that whitespace in technology names is handled correctly."""
    job_desc = MockJobDescription(
        languages=["Python"],
        frameworks=["React Native"],
        tools=["Git"],
    )

    experience = {
        "languages": [" Python "],
        "frameworks": ["React Native"],
        "tools": [" Git"],
    }

    score = calculate_experience_score(experience, job_desc)
    assert score == 3, "Whitespace should be stripped and match correctly"
