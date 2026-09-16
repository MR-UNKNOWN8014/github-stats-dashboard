import os
import sys
from datetime import datetime
from github_client import (
    get_user_profile,
    get_all_repos,
    get_commit_activity,
    get_repo_languages,
    GitHubAPIError,
)
from analyzer import (
    analyze_languages,
    top_repos_by_stars,
    repo_growth_by_month,
    most_active_day,
    total_commits_last_year,
    original_repos,
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
    owner = profile["login"]

    print("Fetching GitHub Repos (This may take a minute)")
    repos = get_all_repos()
    print(f"Found {len(repos)} repos")

    non_forks = original_repos(repos)

    print(f"Fetching commit activity ({len(non_forks)} repos)")
    total_commits = 0
    pending_repos = 0
    for repo in non_forks:
        commits = total_commits_last_year(get_commit_activity(repo["name"], owner=owner))
        if commits is None:
            pending_repos += 1
        else:
            total_commits += commits

    print(f"Fetching language breakdown ({len(non_forks)} repos)")
    language_byte_maps = [get_repo_languages(repo["name"], owner=owner) for repo in non_forks]

    print("Analyzing Data")
    language_counter = analyze_languages(language_byte_maps)
    top_repos = top_repos_by_stars(repos, limit=5)
    growth_by_month = repo_growth_by_month(repos)
    active_day = most_active_day(repos)

    print("Generating Report")
    report = build_full_report(
        profile, language_counter, top_repos, growth_by_month, active_day,
        total_commits, pending_repos,
    )

    ensure_reports_folder()
    filename = generate_filename()

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report saved to: {filename}")


if __name__ == "__main__":
    try:
        run()
    except GitHubAPIError as e:
        print(f"Error: {e}")
        sys.exit(1)
