"""
Command-line argument definitions for main.py.
"""

import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Generate a GitHub stats report.")
    parser.add_argument("-u", "--username", help="GitHub username to report on (defaults to GITHUB_USERNAME in .env). Public data only.")
    parser.add_argument("--private", action="store_true", help="Include your own private repos. Cannot be combined with --username.")
    parser.add_argument("-o", "--output", help="Output file path (defaults to reports/github_report_<timestamp>.<format>)")
    parser.add_argument("-f", "--format", choices=["md", "json"], default="json", help="Report format (default: json)")
    return parser.parse_args()
