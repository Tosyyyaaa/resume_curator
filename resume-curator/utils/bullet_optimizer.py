"""LLM-based bullet point optimizer for resume content.

This module uses Gemini to optimize and rank bullet points for resume
experiences and projects, ensuring they fit within character constraints
while maintaining professionalism.
"""

import sys
from pathlib import Path
from typing import Any

# Import GeminiClient from job-description-parser
# Get the absolute path to the job-description-parser directory
_current_file = Path(__file__).resolve()
_resume_curator_dir = _current_file.parent.parent
_repo_root = _resume_curator_dir.parent
_parser_dir = _repo_root / "job-description-parser"

if str(_parser_dir) not in sys.path:
    sys.path.insert(0, str(_parser_dir))

# Import using importlib for better control
import importlib.util

_gemini_spec = importlib.util.spec_from_file_location(
    "gemini_client", _parser_dir / "utils" / "gemini_client.py"
)
_gemini_module = importlib.util.module_from_spec(_gemini_spec)  # type: ignore
_gemini_spec.loader.exec_module(_gemini_module)  # type: ignore
GeminiClient = _gemini_module.GeminiClient


class BulletOptimizer:
    """Optimizes bullet points using LLM for resume content."""

    def __init__(self, gemini_client: GeminiClient | None = None):
        """Initialize bullet optimizer.

        Args:
            gemini_client: Gemini client instance (creates new one if None)
        """
        self.client = gemini_client or GeminiClient()

    def optimize_bullets(
        self, bullets: list[str], max_chars_per_bullet: int = 80
    ) -> list[str]:
        """Optimize and rank bullet points for resume.

        Uses LLM to:
        1. Compress long bullet points to fit character limit
        2. Split bullets if compression loses important information
        3. Rank bullets by importance (most important first)

        Args:
            bullets: List of bullet point strings
            max_chars_per_bullet: Maximum characters per bullet point

        Returns:
            Optimized and ranked list of bullet points
        """
        if not bullets:
            return []

        # Build prompt for Gemini
        prompt = self._build_optimization_prompt(bullets, max_chars_per_bullet)

        try:
            # Get structured response from Gemini
            response = self.client.generate_structured_json(prompt, temperature=0.2)

            # Extract optimized bullets
            optimized = response.get("bullets", [])

            # Validate response
            if not isinstance(optimized, list):
                print("Warning: Invalid response format from LLM, using original bullets")
                return bullets

            # Filter out empty bullets
            optimized = [b.strip() for b in optimized if b and b.strip()]

            if not optimized:
                print("Warning: LLM returned empty bullets, using original")
                return bullets

            return optimized

        except Exception as e:
            print(f"Warning: Failed to optimize bullets with LLM: {e}")
            print("Falling back to original bullets")
            return bullets

    def _build_optimization_prompt(
        self, bullets: list[str], max_chars: int
    ) -> str:
        """Build prompt for Gemini to optimize bullets.

        Args:
            bullets: Original bullet points
            max_chars: Maximum characters per bullet

        Returns:
            Formatted prompt string
        """
        bullets_text = "\n".join(f"{i+1}. {bullet}" for i, bullet in enumerate(bullets))

        prompt = f"""You are a professional resume writer. Optimize the following bullet points for a resume.

**Requirements:**
1. Each bullet point must be at most {max_chars} characters
2. Compress long bullets by removing filler words while keeping key achievements/metrics
3. If a bullet contains multiple distinct achievements and cannot be compressed without losing critical information, split it into multiple bullets
4. Maintain professional tone and active voice
5. Rank the bullets by importance (most impressive/relevant achievements first)
6. Preserve specific numbers, metrics, and technical details

**Original Bullet Points:**
{bullets_text}

**Instructions:**
- Analyze each bullet for key achievements and metrics
- Compress verbose language to fit character limit
- Split bullets only if compression would lose important information
- Rank final bullets by impact (quantified results > technical achievements > responsibilities)

Return a JSON object with this structure:
{{
    "bullets": ["optimized bullet 1", "optimized bullet 2", ...]
}}

The bullets array should contain the optimized and ranked bullet points."""

        return prompt


def optimize_experience_bullets(
    bullets: list[str], max_chars_per_bullet: int = 80
) -> list[str]:
    """Convenience function to optimize experience bullets.

    Args:
        bullets: List of bullet points
        max_chars_per_bullet: Maximum characters per bullet

    Returns:
        Optimized bullet points
    """
    optimizer = BulletOptimizer()
    return optimizer.optimize_bullets(bullets, max_chars_per_bullet)
