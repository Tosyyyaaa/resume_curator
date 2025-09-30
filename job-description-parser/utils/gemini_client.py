"""Gemini API client utilities.

This module provides a wrapper for interacting with Google's Gemini API,
including error handling, rate limiting, and response parsing.
"""

import json
import os
import time
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()


class GeminiClient:
    """Client for interacting with Google's Gemini API.

    Handles API configuration, request management, and error handling
    for Gemini model interactions.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        """Initialize Gemini client.

        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            model: Model name (defaults to GEMINI_MODEL env var or gemini-1.5-pro)
            max_retries: Maximum number of retry attempts for failed requests
            retry_delay: Initial delay between retries in seconds (uses exponential backoff)

        Raises:
            ValueError: If API key is not provided or found in environment
        """
        self.api_key: str = api_key or os.getenv("GEMINI_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY must be provided or set in environment variables"
            )

        self.model_name: str = model or os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
        self.max_retries: int = max_retries
        self.retry_delay: float = retry_delay

        # Configure the Gemini client
        self.client: genai.Client = genai.Client(api_key=self.api_key)

    def generate_content(
        self,
        prompt: str,
        temperature: float = 0.1,
        response_mime_type: str = "application/json",
    ) -> str:
        """Generate content using Gemini API.

        Args:
            prompt: Input prompt for content generation
            temperature: Sampling temperature (0.0-1.0, lower = more deterministic)
            response_mime_type: Expected response MIME type

        Returns:
            Generated text content from the model

        Raises:
            Exception: If API request fails after all retries
        """
        config: types.GenerateContentConfig = types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type=response_mime_type,
        )

        for attempt in range(self.max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config,
                )

                if response.text:
                    return response.text

                raise ValueError("Empty response from Gemini API")

            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay: float = self.retry_delay * (2**attempt)
                    print(
                        f"API request failed (attempt {attempt + 1}/{self.max_retries}): {e}"
                    )
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise Exception(
                        f"Failed to generate content after {self.max_retries} attempts: {e}"
                    ) from e

        raise Exception("Unexpected error in generate_content")

    def parse_json_response(self, response_text: str) -> dict[str, Any]:
        """Parse JSON response from Gemini API.

        Args:
            response_text: Raw text response from API

        Returns:
            Parsed JSON as dictionary

        Raises:
            json.JSONDecodeError: If response is not valid JSON
        """
        # Strip markdown code blocks if present
        cleaned_text: str = response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]

        cleaned_text = cleaned_text.strip()

        return json.loads(cleaned_text)

    def generate_structured_json(
        self, prompt: str, temperature: float = 0.1
    ) -> dict[str, Any]:
        """Generate and parse structured JSON response.

        Args:
            prompt: Input prompt for JSON generation
            temperature: Sampling temperature

        Returns:
            Parsed JSON dictionary

        Raises:
            Exception: If generation or parsing fails
        """
        response_text: str = self.generate_content(
            prompt=prompt,
            temperature=temperature,
            response_mime_type="application/json",
        )

        return self.parse_json_response(response_text)