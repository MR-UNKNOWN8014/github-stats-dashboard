"""
Loads sensitive configuration (API token, username) from environment
"""

import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found. Check your .env file.")

if not GITHUB_USERNAME:
    raise ValueError("GITHUB_USERNAME not found. Check your .env file.")