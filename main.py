import json
import os
import sys
from datetime import datetime
from cli import parse_args
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
from report_generator import build_full_report, build_report_data

def ensure_folder(path):
    """Creates the parent directory of path, if it has one."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

def generate_filename(ext):
    """
    Builds a unique, sortable filename using the current timestamp
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    return f"reports/github_report_{timestamp}.{ext}"

def run(username=None, include_private=None, output=None, fmt="md"):
    print("Fetching GitHub Profile")
    profile = get_user_profile(username=username, include_private=include_private)
    owner = profile["login"]

    print("Fetching GitHub Repos (This may take a minute)")
    repos = get_all_repos(username=username, include_private=include_private)
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
    if fmt == "json":
        data = build_report_data(
            profile, language_counter, top_repos, growth_by_month, active_day,
            total_commits, pending_repos,
        )
        content = json.dumps(data, indent=2)
    else:
        content = build_full_report(
            profile, language_counter, top_repos, growth_by_month, active_day,
            total_commits, pending_repos,
        )

    filename = output or generate_filename(fmt)
    ensure_folder(filename)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Report saved to: {filename}")


if __name__ == "__main__":
    args = parse_args()

    if args.username and args.private:
        print("Error: --username and --private cannot be combined (private repos are only visible for the token's own account).")
        sys.exit(1)

    try:
        run(username=args.username, include_private=args.private or None, output=args.output, fmt=args.format)
    except GitHubAPIError as e:
        print(f"Error: {e}")
        sys.exit(1)
