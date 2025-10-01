"""Unit tests for LineMetrics utility class."""

import sys
from pathlib import Path

import pytest

# Add parent directory to path to handle hyphenated module name
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.line_metrics import LineMetrics


class TestLineMetrics:
    """Test suite for LineMetrics class."""

    def test_page_to_lines_single_page(self):
        """Test conversion of 1 page to lines."""
        assert LineMetrics.page_to_lines(1) == 45

    def test_page_to_lines_multiple_pages(self):
        """Test conversion of multiple pages to lines."""
        assert LineMetrics.page_to_lines(2) == 90
        assert LineMetrics.page_to_lines(3) == 135

    def test_page_to_lines_zero_pages(self):
        """Test conversion of 0 pages returns 0 lines."""
        assert LineMetrics.page_to_lines(0) == 0

    def test_chars_to_lines_exact_fit(self):
        """Test character count that exactly fits one line."""
        assert LineMetrics.chars_to_lines(80) == 1

    def test_chars_to_lines_partial_line(self):
        """Test character count that requires partial line rounds up."""
        assert LineMetrics.chars_to_lines(81) == 2
        assert LineMetrics.chars_to_lines(1) == 1

    def test_chars_to_lines_empty(self):
        """Test empty string returns 0 lines."""
        assert LineMetrics.chars_to_lines(0) == 0

    def test_calculate_text_lines_empty_string(self):
        """Test empty string calculation."""
        assert LineMetrics.calculate_text_lines("") == 0
        assert LineMetrics.calculate_text_lines("   ") == 0

    def test_calculate_text_lines_single_line(self):
        """Test single short line."""
        text = "Hello, World!"
        assert LineMetrics.calculate_text_lines(text) == 1

    def test_calculate_text_lines_exact_80_chars(self):
        """Test text that is exactly 80 characters."""
        text = "a" * 80
        assert LineMetrics.calculate_text_lines(text) == 1

    def test_calculate_text_lines_over_80_chars(self):
        """Test text that wraps to multiple lines."""
        text = "a" * 81
        assert LineMetrics.calculate_text_lines(text) == 2

        text = "a" * 160
        assert LineMetrics.calculate_text_lines(text) == 2

        text = "a" * 161
        assert LineMetrics.calculate_text_lines(text) == 3

    def test_calculate_text_lines_with_newlines(self):
        """Test text with explicit newline characters."""
        text = "Line 1\nLine 2\nLine 3"
        assert LineMetrics.calculate_text_lines(text) == 3

    def test_calculate_text_lines_with_long_lines_and_newlines(self):
        """Test text with both newlines and lines over 80 chars."""
        text = "a" * 81 + "\n" + "b" * 80
        # First line: 81 chars = 2 lines
        # Second line: 80 chars = 1 line
        assert LineMetrics.calculate_text_lines(text) == 3

    def test_calculate_text_lines_with_empty_lines(self):
        """Test text with empty lines between content."""
        text = "Line 1\n\nLine 3"
        # Line 1: 1 line
        # Empty line: 1 line
        # Line 3: 1 line
        assert LineMetrics.calculate_text_lines(text) == 3

    def test_calculate_text_lines_bullet_points(self):
        """Test realistic bullet point scenario."""
        bullets = [
            "Increased user engagement by 200% using reinforcement learning",
            "Decreased instagram's load time by 50% using distributed systems",
        ]
        text = "\n".join(bullets)
        # Each bullet is under 80 chars, so 2 lines total
        assert LineMetrics.calculate_text_lines(text) == 2

    def test_calculate_text_lines_long_bullet(self):
        """Test bullet point that wraps to multiple lines."""
        bullet = "a" * 150  # 150 chars should wrap to 2 lines
        assert LineMetrics.calculate_text_lines(bullet) == 2

    def test_custom_chars_per_line(self):
        """Test custom character-per-line setting."""
        text = "a" * 100
        # With default 80 chars/line: should be 2 lines
        assert LineMetrics.calculate_text_lines(text, chars_per_line=80) == 2
        # With 100 chars/line: should be 1 line
        assert LineMetrics.calculate_text_lines(text, chars_per_line=100) == 1

    def test_unicode_characters(self):
        """Test handling of unicode characters."""
        text = "café résumé 日本語"
        # Should count unicode chars correctly
        assert LineMetrics.calculate_text_lines(text) == 1
