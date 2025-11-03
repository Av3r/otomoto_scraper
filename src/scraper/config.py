"""Configuration values for the scraper.

This module reads environment variables (via python-dotenv) and exposes
configuration constants used across the package.
"""

import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("OTOMOTO_URL", "https://www.otomoto.pl/osobowe/bmw/seria-5")
