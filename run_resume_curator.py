#!/usr/bin/env python3
"""Launcher script for resume curator that handles import paths correctly."""

import sys
from pathlib import Path

# Add both directories to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root / "job-description-parser"))
sys.path.insert(0, str(repo_root / "resume-curator"))

# Now run main
from main import main  # type: ignore

if __name__ == "__main__":
    main()
