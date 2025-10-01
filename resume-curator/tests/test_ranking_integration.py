"""Integration tests for experience and project ranking functionality.

Tests the end-to-end ranking system that scores and orders experiences
and projects based on relevance to job requirements.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.candidate_data import CandidateData
from main import extract_experiences, extract_projects


class MockJobDescription:
    """Mock job description for testing."""

    def __init__(self, languages=None, frameworks=None, tools=None):
        self.programming_languages = languages or []
        self.frameworks = frameworks or []
        self.tools = tools or []
        self.job_title = "Test Position"


def test_experiences_sorted_by_relevance():
    """Test that experiences are sorted by relevance score (highest first)."""

    # Create mock candidate data with multiple experiences
    candidate_data = CandidateData(
        experiences={
            "work_experience": [
                {
                    "company": "Company A",
                    "title": "Engineer",
                    "start_date": "2023",
                    "end_date": "2024",
                    "description": "Did some work",
                    "languages": ["Python", "Java"],  # 2 matches
                    "frameworks": ["Django"],  # 1 match
                    "tools": ["Git"],  # 1 match
                    # Expected score: 4
                },
                {
                    "company": "Company B",
                    "title": "Developer",
                    "start_date": "2022",
                    "end_date": "2023",
                    "description": "Did other work",
                    "languages": ["Rust"],  # 0 matches
                    "frameworks": ["Actix"],  # 0 matches
                    "tools": ["Git"],  # 1 match
                    # Expected score: 1
                },
                {
                    "company": "Company C",
                    "title": "Senior Engineer",
                    "start_date": "2024",
                    "end_date": "2025",
                    "description": "Lead projects",
                    "languages": ["Python", "JavaScript"],  # 2 matches
                    "frameworks": ["Django", "React"],  # 2 matches
                    "tools": ["Git", "Docker"],  # 2 matches
                    # Expected score: 6
                },
            ],
            "internship_experience": [],
            "competitions": [],
        },
        education={},
        projects={},
        metadata={"name": "Test Candidate"},
    )

    job_description = MockJobDescription(
        languages=["Python", "Java", "JavaScript"],
        frameworks=["Django", "React"],
        tools=["Git", "Docker"],
    )

    experiences = extract_experiences(candidate_data, job_description)

    # Verify we got all 3 experiences
    assert len(experiences) == 3

    # Verify they are sorted by relevance score (descending)
    assert experiences[0].company == "Company C"  # Score 6
    assert experiences[0].relevance_score == 6

    assert experiences[1].company == "Company A"  # Score 4
    assert experiences[1].relevance_score == 4

    assert experiences[2].company == "Company B"  # Score 1
    assert experiences[2].relevance_score == 1

    # Verify descending order
    for i in range(len(experiences) - 1):
        assert experiences[i].relevance_score >= experiences[i + 1].relevance_score


def test_projects_sorted_by_relevance():
    """Test that projects are sorted by relevance score (highest first)."""

    candidate_data = CandidateData(
        experiences={},
        education={},
        projects={
            "projects": [
                {
                    "name": "Project Alpha",
                    "description": "First project",
                    "start_date": "2020",
                    "end_date": "2021",
                    "languages": ["Python"],  # 1 match
                    "frameworks": ["PyTorch"],  # 1 match
                    "tools": [],  # 0 matches
                    # Expected score: 2
                },
                {
                    "name": "Project Beta",
                    "description": "Second project",
                    "start_date": "2021",
                    "end_date": "2022",
                    "languages": ["JavaScript"],  # 0 matches
                    "frameworks": ["React"],  # 0 matches
                    "tools": [],  # 0 matches
                    # Expected score: 0
                },
                {
                    "name": "Project Gamma",
                    "description": "Third project",
                    "start_date": "2022",
                    "end_date": "2023",
                    "languages": ["Python", "C++"],  # 2 matches
                    "frameworks": ["PyTorch", "TensorFlow"],  # 2 matches
                    "tools": ["Git", "Docker"],  # 2 matches
                    # Expected score: 6
                },
            ]
        },
        metadata={"name": "Test Candidate"},
    )

    job_description = MockJobDescription(
        languages=["Python", "Java", "C++"],
        frameworks=["PyTorch", "TensorFlow"],
        tools=["Git", "Docker"],
    )

    projects = extract_projects(candidate_data, job_description)

    # Verify we got all 3 projects
    assert len(projects) == 3

    # Verify they are sorted by relevance score (descending)
    assert projects[0].name == "Project Gamma"  # Score 6
    assert projects[0].relevance_score == 6

    assert projects[1].name == "Project Alpha"  # Score 2
    assert projects[1].relevance_score == 2

    assert projects[2].name == "Project Beta"  # Score 0
    assert projects[2].relevance_score == 0

    # Verify descending order
    for i in range(len(projects) - 1):
        assert projects[i].relevance_score >= projects[i + 1].relevance_score


def test_stable_sort_maintains_relative_order():
    """Test that items with the same score maintain their original order."""

    candidate_data = CandidateData(
        experiences={
            "work_experience": [
                {
                    "company": "First Company",
                    "title": "Engineer",
                    "start_date": "2020",
                    "end_date": "2021",
                    "description": "Work",
                    "languages": ["Python"],
                    "frameworks": [],
                    "tools": [],
                    # Expected score: 1
                },
                {
                    "company": "Second Company",
                    "title": "Developer",
                    "start_date": "2021",
                    "end_date": "2022",
                    "description": "Work",
                    "languages": ["Python"],
                    "frameworks": [],
                    "tools": [],
                    # Expected score: 1 (same as first)
                },
                {
                    "company": "Third Company",
                    "title": "Engineer",
                    "start_date": "2022",
                    "end_date": "2023",
                    "description": "Work",
                    "languages": ["Python"],
                    "frameworks": [],
                    "tools": [],
                    # Expected score: 1 (same as others)
                },
            ],
            "internship_experience": [],
            "competitions": [],
        },
        education={},
        projects={},
        metadata={"name": "Test Candidate"},
    )

    job_description = MockJobDescription(languages=["Python"])

    experiences = extract_experiences(candidate_data, job_description)

    # All should have same score
    assert all(exp.relevance_score == 1 for exp in experiences)

    # Verify relative order is maintained (Python's sort is stable)
    assert experiences[0].company == "First Company"
    assert experiences[1].company == "Second Company"
    assert experiences[2].company == "Third Company"


def test_mixed_experience_types_sorted_together():
    """Test that work, internship, and competition experiences are all ranked together."""

    candidate_data = CandidateData(
        experiences={
            "work_experience": [
                {
                    "company": "Work Company",
                    "title": "Engineer",
                    "start_date": "2023",
                    "end_date": "2024",
                    "description": "Work",
                    "languages": ["Python"],
                    "frameworks": [],
                    "tools": [],
                    # Score: 1
                }
            ],
            "internship_experience": [
                {
                    "company": "Internship Company",
                    "title": "Intern",
                    "start_date": "2022",
                    "end_date": "2023",
                    "description": "Intern work",
                    "languages": ["Python", "Java"],
                    "frameworks": ["Django"],
                    "tools": [],
                    # Score: 3
                }
            ],
            "competitions": [
                {
                    "name": "Hackathon",
                    "description": "Won competition",
                    "start_date": "2021",
                    "end_date": "2021",
                    "languages": ["Python", "Java"],
                    "frameworks": [],
                    "tools": [],
                    # Score: 2
                }
            ],
        },
        education={},
        projects={},
        metadata={"name": "Test Candidate"},
    )

    job_description = MockJobDescription(
        languages=["Python", "Java"], frameworks=["Django"]
    )

    experiences = extract_experiences(candidate_data, job_description)

    # Should be sorted by score across all types
    assert len(experiences) == 3
    assert experiences[0].company == "Internship Company"  # Score 3
    assert experiences[1].company == "Hackathon"  # Score 2 (competition)
    assert experiences[2].company == "Work Company"  # Score 1


def test_zero_score_items_still_included():
    """Test that experiences/projects with zero score are still included."""

    candidate_data = CandidateData(
        experiences={
            "work_experience": [
                {
                    "company": "No Match Company",
                    "title": "Engineer",
                    "start_date": "2023",
                    "end_date": "2024",
                    "description": "Work",
                    "languages": ["Rust"],
                    "frameworks": ["Actix"],
                    "tools": ["Cargo"],
                    # Score: 0 (no matches)
                }
            ],
            "internship_experience": [],
            "competitions": [],
        },
        education={},
        projects={},
        metadata={"name": "Test Candidate"},
    )

    job_description = MockJobDescription(
        languages=["Python"], frameworks=["Django"], tools=["Git"]
    )

    experiences = extract_experiences(candidate_data, job_description)

    # Should still include the experience
    assert len(experiences) == 1
    assert experiences[0].relevance_score == 0
    assert experiences[0].company == "No Match Company"


def test_missing_tech_fields_handled_gracefully():
    """Test that missing language/framework/tool fields don't cause errors."""

    candidate_data = CandidateData(
        experiences={
            "work_experience": [
                {
                    "company": "Minimal Data Company",
                    "title": "Engineer",
                    "start_date": "2023",
                    "end_date": "2024",
                    "description": "Work",
                    # No tech fields at all
                }
            ],
            "internship_experience": [],
            "competitions": [],
        },
        education={},
        projects={},
        metadata={"name": "Test Candidate"},
    )

    job_description = MockJobDescription(
        languages=["Python"], frameworks=["Django"], tools=["Git"]
    )

    # Should not raise an error
    experiences = extract_experiences(candidate_data, job_description)

    assert len(experiences) == 1
    assert experiences[0].relevance_score == 0
