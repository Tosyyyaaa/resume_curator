"""Relevance scoring for experiences and projects against job descriptions.

This module provides functions to calculate how well a candidate's experiences
and projects match job description requirements based on programming languages,
frameworks, and tools.
"""

from typing import Any


def calculate_experience_score(
    experience: dict[str, Any], job_description: Any
) -> int:
    """Calculate relevance score for an experience against job requirements.

    Scoring algorithm:
        - +1 point for each matching programming language
        - +1 point for each matching framework
        - +1 point for each matching tool

    Matching is case-insensitive and whitespace is stripped.

    Args:
        experience: Dictionary containing experience data with optional
                   'languages', 'frameworks', and 'tools' fields
        job_description: Object with programming_languages, frameworks,
                        and tools attributes

    Returns:
        Integer score representing match quality (0 = no match)
    """
    return _calculate_score(
        candidate_languages=experience.get("languages", []),
        candidate_frameworks=experience.get("frameworks", []),
        candidate_tools=experience.get("tools", []),
        job_languages=job_description.programming_languages,
        job_frameworks=job_description.frameworks,
        job_tools=job_description.tools,
    )


def calculate_project_score(project: dict[str, Any], job_description: Any) -> int:
    """Calculate relevance score for a project against job requirements.

    Scoring algorithm:
        - +1 point for each matching programming language
        - +1 point for each matching framework
        - +1 point for each matching tool

    Matching is case-insensitive and whitespace is stripped.

    Args:
        project: Dictionary containing project data with optional
                'languages', 'frameworks', and 'tools' fields
        job_description: Object with programming_languages, frameworks,
                        and tools attributes

    Returns:
        Integer score representing match quality (0 = no match)
    """
    return _calculate_score(
        candidate_languages=project.get("languages", []),
        candidate_frameworks=project.get("frameworks", []),
        candidate_tools=project.get("tools", []),
        job_languages=job_description.programming_languages,
        job_frameworks=job_description.frameworks,
        job_tools=job_description.tools,
    )


def _calculate_score(
    candidate_languages: list[str],
    candidate_frameworks: list[str],
    candidate_tools: list[str],
    job_languages: list[str],
    job_frameworks: list[str],
    job_tools: list[str],
) -> int:
    """Calculate total match score between candidate and job requirements.

    Args:
        candidate_languages: Languages the candidate knows
        candidate_frameworks: Frameworks the candidate has used
        candidate_tools: Tools the candidate has used
        job_languages: Languages required by the job
        job_frameworks: Frameworks required by the job
        job_tools: Tools required by the job

    Returns:
        Integer score representing total matches
    """
    score = 0

    # Normalize candidate data (lowercase, strip whitespace)
    normalized_candidate_languages = {
        lang.strip().lower() for lang in candidate_languages
    }
    normalized_candidate_frameworks = {
        fw.strip().lower() for fw in candidate_frameworks
    }
    normalized_candidate_tools = {tool.strip().lower() for tool in candidate_tools}

    # Score languages
    for lang in job_languages:
        if lang.strip().lower() in normalized_candidate_languages:
            score += 1

    # Score frameworks
    for fw in job_frameworks:
        if fw.strip().lower() in normalized_candidate_frameworks:
            score += 1

    # Score tools
    for tool in job_tools:
        if tool.strip().lower() in normalized_candidate_tools:
            score += 1

    return score
