"""
Handles all communication with the GitHub REST API
"""

import requests
from config import GITHUB_TOKEN, GITHUB_USERNAME

BASE_URL="https://api.github.com"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

def get_user_profile():
    """
        Fetches basic profile info: name, bio, follower count, public repo count.
        Returns a dict (the parsed JSON response).
    """
    url = f"{BASE_URL}/users/{GITHUB_USERNAME}"
    response = requests.get(url, headers=HEADERS)

    # raise_for_status() throws an exception if GitHub returned an
    # error code (401 = bad token, 404 = user not found, etc.)
    response.raise_for_status()

    return response.json()

def get_all_repos():
    """
        Fetches all repos for the user, handles pagination automatically.
    """
    repos = []
    page = 1
    per_page = 100

    while True:
        url = f"{BASE_URL}/users/{GITHUB_USERNAME}/repos"
        params = {
            "per_page": per_page,
            "page": page,
            "sort": "updated",
        }

        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()

        page_data = response.json()

        # Stops if there is nothing left
        if not page_data:
            break

        repos.extend(page_data)

        # If we got fewer than a full page, this WAS the last page
        if len(page_data) < per_page:
            break

        page += 1

    return repos

def get_commit_activity(repo_name):
    """
        Fetches weekly commit activity for a single repo (last 52 weeks).
        Returns a list of weekly stats, or empty list if data isn't ready yet
    """
    url = f"{BASE_URL}/repos/{GITHUB_USERNAME}/{repo_name}/stats/commit_activity"
    response = requests.get(url, headers=HEADERS)

    # GitHub returns 202 (Accepted) when it's still computing stats
    # in the background for a repo it hasn't analyzed before.
    # In that case, there's no data yet — return empty rather than crash.
    if response.status_code == 202:
        return []

    response.raise_for_status()
    return response.json()