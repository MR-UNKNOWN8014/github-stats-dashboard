import os
from datetime import datetime
from github_client import get_user_profile, get_all_repos
from analyzer import (
    analyze_languages,
    top_repos_by_stars,
    repo_growth_by_month,
    most_active_day,
)
from report_generator import build_full_report

def ensure_reports_folder():
    """
    Creates the reports/ folder if it doesn't exist yet.
    """
    os.makedirs("reports", exist_ok=True)

def generate_filename():
    """
    Builds a unique, sortable filename using the current timestamp
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    return f"reports/github_report_{timestamp}.md"

def run():
    print("Fetching GitHub Profile")
    profile = get_user_profile()

    print("Fetching GitHub Repos (This may take a minute)")
    repos = get_all_repos()
    print(f"Found {len(repos)} repos")

    print("Analyzing Data")
    language_counter = analyze_languages(repos)
    top_repos = top_repos_by_stars(repos, limit=5)
    growth_by_month = repo_growth_by_month(repos)
    active_day = most_active_day(repos)

    print("Generating Report")
    report = build_full_report(
        profile, language_counter, top_repos, growth_by_month, active_day
    )

    ensure_reports_folder()
    filename = generate_filename()

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report saved to: {filename}")


if __name__ == "__main__":
    run()