"""
Handles all communication with the GitHub REST API
"""

import time
import requests
from config import GITHUB_TOKEN, GITHUB_USERNAME, INCLUDE_PRIVATE

BASE_URL="https://api.github.com"
TIMEOUT = 10

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

class GitHubAPIError(RuntimeError):
    """Raised for any GitHub API failure, with a human-readable message."""

def _raise_friendly(response):
    # Turns raw HTTP errors into short, readable messages instead of tracebacks
    if response.status_code == 401:
        raise GitHubAPIError("GitHub rejected the token. Check GITHUB_TOKEN in your .env file.")
    if response.status_code == 404:
        raise GitHubAPIError("GitHub user not found. Check the username (GITHUB_USERNAME in .env, or --username).")
    if response.status_code == 403:
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        raise GitHubAPIError(f"GitHub rate limit hit (remaining: {remaining}, resets at epoch {reset}).")
    response.raise_for_status()

def _request(url, params=None, retries=2):
    # Retries transient network failures (timeouts, dropped connections),
    # not HTTP error responses, those are handled by _raise_friendly.
    for attempt in range(retries):
        try:
            return requests.get(url, headers=HEADERS, params=params, timeout=TIMEOUT)
        except requests.exceptions.RequestException as e:
            if attempt == retries - 1:
                raise GitHubAPIError(f"Could not reach GitHub: {e}") from e
            time.sleep(1)

def _get(url, params=None):
    response = _request(url, params=params)
    if not response.ok:
        _raise_friendly(response)
    return response

def get_user_profile(username=None, include_private=None):
    """
        Fetches profile info: name, bio, follower count, public repo count.
        Uses the authenticated /user endpoint when include_private is on
        (that's the only identity GitHub will ever show private data for),
        otherwise the public /users/{username} view.
    """
    username = username or GITHUB_USERNAME
    include_private = INCLUDE_PRIVATE if include_private is None else include_private
    url = f"{BASE_URL}/user" if include_private else f"{BASE_URL}/users/{username}"
    return _get(url).json()

def get_all_repos(username=None, include_private=None):
    """
        Fetches all repos for the user, handles pagination automatically.
        include_private switches to the authenticated /user/repos endpoint
        (token owner's own repos, public + private). GitHub never exposes
        another account's private repos no matter what username is set to,
        so this path always reflects the token owner, not the username arg.
    """
    username = username or GITHUB_USERNAME
    include_private = INCLUDE_PRIVATE if include_private is None else include_private
    repos = []
    page = 1
    per_page = 100

    while True:
        if include_private:
            url = f"{BASE_URL}/user/repos"
            params = {"per_page": per_page, "page": page, "sort": "updated", "affiliation": "owner"}
        else:
            url = f"{BASE_URL}/users/{username}/repos"
            params = {"per_page": per_page, "page": page, "sort": "updated"}

        page_data = _get(url, params=params).json()

        # Stops if there is nothing left
        if not page_data:
            break

        repos.extend(page_data)

        # If we got fewer than a full page, this WAS the last page
        if len(page_data) < per_page:
            break

        page += 1

    return repos

def get_commit_activity(repo_name, owner=None):
    """
        Fetches weekly commit activity for a single repo (last 52 weeks).
        Returns a list of weekly stats, [] if the repo genuinely has none,
        or None if GitHub is still computing stats for it (retry later).
    """
    owner = owner or GITHUB_USERNAME
    url = f"{BASE_URL}/repos/{owner}/{repo_name}/stats/commit_activity"

    # GitHub returns 202 while it computes stats in the background for a
    # repo it hasn't analyzed before. One short retry usually has data ready.
    for attempt in range(2):
        response = _request(url)

        if response.status_code == 202:
            if attempt == 0:
                time.sleep(2)
                continue
            return None

        if not response.ok:
            _raise_friendly(response)

        return response.json()

def get_repo_languages(repo_name, owner=None):
    """
        Fetches byte-count-per-language breakdown for a single repo
        (GitHub's own "top languages" bar uses this, not just the repo's
        single primary language field).
    """
    owner = owner or GITHUB_USERNAME
    url = f"{BASE_URL}/repos/{owner}/{repo_name}/languages"
    return _get(url).json()
