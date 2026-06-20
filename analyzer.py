"""
Takes raw repo data from github_client.py and turns it into
meaningful stats: language breakdown, top repos by stars,
and repo creation trends over time.
"""

from collections import Counter
from datetime import datetime

def analyze_languages(repos):
    languages = []

    for repo in repos:
        # Skip fork repos
        if repo["fork"]:
            continue

        # Some repos have no detected language (empty/data-only repos)
        if repo["language"] is None:
            continue

        languages.append(repo["language"])
    return Counter(languages)

def top_repos_by_stars(repos, limit=5):
    original_repos = [r for r in repos if not r["fork"]]

    sorted_repos = sorted(
        original_repos,
        key=lambda r: r["stargazers_count"],
        reverse=True
    )

    return sorted_repos[:limit]


def repo_growth_by_month(repos):
    growth = Counter()

    for repo in repos:
        if repo["fork"]:
            continue

        created = datetime.strptime(repo["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        month_key = created.strftime("%Y-%m")
        growth[month_key] += 1

    return dict(sorted(growth.items()))


def most_active_day(repos):
    """
        Looks at repo 'updated_at' timestamps to guess which day of the
        week you push code most often. Rough signal, not perfectly precise
    """
    day_counts = Counter()

    for repo in repos:
        if repo["fork"]:
            continue

        updated = datetime.strptime(repo["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
        day_name = updated.strftime("%A")
        day_counts[day_name] += 1

    if not day_counts:
        return ("No Data", 0)

    return day_counts.most_common(1)[0]