"""
Takes raw repo data from github_client.py and turns it into
meaningful stats: language breakdown, top repos by stars,
and repo creation trends over time.
"""

from collections import Counter
from datetime import datetime

def original_repos(repos):
    """Filters out forks, kept in one place since every stat below needs it."""
    return [r for r in repos if not r["fork"]]

def analyze_languages(language_byte_maps):
    """
    Aggregates per-repo {language: bytes} maps (from get_repo_languages)
    into one Counter of total bytes per language across all repos.
    """
    total = Counter()
    for byte_map in language_byte_maps:
        total.update(byte_map)
    return total

def top_repos_by_stars(repos, limit=5):
    sorted_repos = sorted(
        original_repos(repos),
        key=lambda r: r["stargazers_count"],
        reverse=True
    )

    return sorted_repos[:limit]


def repo_growth_by_month(repos):
    """
    Groups repo creation dates by month. Excludes the current month since
    it's still in progress, showing its partial count next to fully
    completed months would misrepresent it as a final tally.
    """
    growth = Counter()
    current_month = datetime.now().strftime("%Y-%m")

    for repo in original_repos(repos):
        created = datetime.strptime(repo["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        month_key = created.strftime("%Y-%m")
        if month_key == current_month:
            continue
        growth[month_key] += 1

    return dict(sorted(growth.items()))


def most_active_day(repos):
    """
        Finds the single calendar date (from repo 'updated_at' timestamps)
        with the most repo updates.
    """
    day_counts = Counter()

    for repo in original_repos(repos):
        updated = datetime.strptime(repo["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
        day_counts[updated.strftime("%b %d, %Y")] += 1

    if not day_counts:
        return ("No Data", 0)

    return day_counts.most_common(1)[0]

def total_commits_last_year(weekly_stats):
    """
    Sums the 'total' field across a get_commit_activity() response.
    Returns None if stats are still being computed by GitHub (see
    get_commit_activity), so callers can tell "not ready" from "really 0".
    """
    if weekly_stats is None:
        return None
    return sum(week["total"] for week in weekly_stats)
