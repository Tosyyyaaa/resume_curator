"""Resume header data model with line length calculation.

This module provides the ResumeHeader class for representing the header section
of a resume, including name, contact information, and social links.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ResumeHeader:
    """Resume header section containing personal information.

    Attributes:
        name: Full name of the candidate
        email: Email address
        phone: Phone number
        location: Current location (city, country)
        linkedin: LinkedIn profile URL (optional)
        github: GitHub profile URL (optional)
        website: Personal website URL (optional)
        line_length: Number of lines the header occupies
    """

    name: str
    email: str
    phone: str
    location: str
    linkedin: str | None = None
    github: str | None = None
    website: str | None = None
    line_length: int = 0

    def __post_init__(self) -> None:
        """Calculate line length after initialization."""
        # Convert empty strings to None
        if self.linkedin == "":
            self.linkedin = None
        if self.github == "":
            self.github = None
        if self.website == "":
            self.website = None

        self.line_length = self.calculate_line_length()

    def calculate_line_length(self) -> int:
        """Calculate number of lines needed for header.

        Header format:
            Line 1: Name (centered, typically larger font)
            Line 2: email | phone | location
            Line 3 (optional): linkedin | github | website (if any present)

        Returns:
            Number of lines (2-3 depending on social links)
        """
        lines = 2  # Name + contact info always present

        # Add line for social links if any are present
        if self.linkedin or self.github or self.website:
            lines += 1

        return lines

    def to_dict(self) -> dict[str, Any]:
        """Convert ResumeHeader to dictionary.

        Returns:
            Dictionary representation with all fields
        """
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "linkedin": self.linkedin,
            "github": self.github,
            "website": self.website,
            "line_length": self.line_length,
        }

    @classmethod
    def from_metadata(cls, metadata: dict[str, Any]) -> "ResumeHeader":
        """Create ResumeHeader from metadata dictionary.

        Args:
            metadata: Dictionary containing personal information

        Returns:
            ResumeHeader instance

        Raises:
            KeyError: If required fields (name, email, phone, location) are missing
        """
        return cls(
            name=metadata["name"],
            email=metadata["email"],
            phone=metadata["phone"],
            location=metadata["location"],
            linkedin=metadata.get("linkedin"),
            github=metadata.get("github"),
            website=metadata.get("website"),
        )
