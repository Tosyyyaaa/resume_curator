"""Line length calculation utilities for resume formatting.

This module provides utilities for converting between pages, lines, and
characters to ensure resume content fits within specified page limits.
"""

from typing import Final


class LineMetrics:
    """Utility class for line length calculations.

    This class provides methods to convert between pages, lines, and characters,
    enabling accurate calculation of how much content fits on a resume page.

    Constants:
        CHARS_PER_LINE: Standard character count per line (LaTeX default: 80)
        LINES_PER_PAGE: Standard line count per page (LaTeX default: 45)
    """

    CHARS_PER_LINE: Final[int] = 80
    LINES_PER_PAGE: Final[int] = 45

    @classmethod
    def page_to_lines(cls, pages: int) -> int:
        """Convert page count to line count.

        Args:
            pages: Number of pages

        Returns:
            Number of lines that fit on the specified pages
        """
        return pages * cls.LINES_PER_PAGE

    @classmethod
    def chars_to_lines(cls, chars: int, chars_per_line: int | None = None) -> int:
        """Convert character count to line count.

        Args:
            chars: Number of characters
            chars_per_line: Characters per line (defaults to CHARS_PER_LINE)

        Returns:
            Number of lines needed for the character count (rounded up)
        """
        if chars == 0:
            return 0

        cpl = chars_per_line if chars_per_line is not None else cls.CHARS_PER_LINE
        return (chars + cpl - 1) // cpl  # Ceiling division

    @classmethod
    def calculate_text_lines(
        cls, text: str, chars_per_line: int | None = None
    ) -> int:
        """Calculate number of lines needed for text.

        This method accounts for both explicit newlines and line wrapping
        based on character count.

        Args:
            text: Text content to measure
            chars_per_line: Characters per line (defaults to CHARS_PER_LINE)

        Returns:
            Number of lines needed to display the text

        Algorithm:
            1. Split text by explicit newlines
            2. For each segment, calculate ceil(len(segment) / chars_per_line)
            3. Sum all line counts
            4. Handle empty strings as 0 lines
        """
        if not text.strip():
            return 0

        cpl = chars_per_line if chars_per_line is not None else cls.CHARS_PER_LINE
        lines = text.split("\n")
        total_lines = 0

        for line in lines:
            if len(line) == 0:
                total_lines += 1  # Empty line still takes space
            else:
                total_lines += cls.chars_to_lines(len(line), cpl)

        return total_lines
