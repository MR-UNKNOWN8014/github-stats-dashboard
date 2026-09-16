"""
Takes analyzed stats and formats them into a Markdown report string.
"""

from datetime import datetime

def generate_header(profile):
    """
    Builds the title block: name, bio, and generation timestamp.
    """
    name = profile.get("name") or profile["login"]
    bio = profile.get("bio") or "No bio set"
    generated_on = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""# GitHub Stats Report - {name}

> {bio}

**Generated:** {generated_on}
**Public repos:** {profile.get('public_repos', 0)} | **Followers:** {profile.get('followers', 0)} | **Following:** {profile.get('following', 0)}

---
"""

def generate_language_section(language_counter):
    if not language_counter:
        return "## Languages\n\nNo language data available.\n\n---\n"

    total = sum(language_counter.values())

    lines = ["## Languages\n"]
    lines.append("| Language | Bytes | Share | Visual |")
    lines.append("|----------|-------|-------|--------|")

    for language, byte_count in language_counter.most_common():
        percent = (byte_count / total) * 100
        bar_length = int(percent / 5)
        bar = "█" * bar_length

        lines.append(f"| {language} | {byte_count:,} | {percent:.1f}% | {bar} |")

    body = "\n".join(lines)

    return f"{body}\n\n---\n"

def generate_top_repos_section(top_repos):
    if not top_repos:
        return "## Top Repositories\n\nNo repos found.\n\n---\n"

    lines = ["## Top Repositories\n"]
    lines.append("| Repo | Language | Stars | Forks |")
    lines.append("|------|----------|-------|-------|")

    for repo in top_repos:
        language = repo.get("language") or "N/A"
        lines.append(
            f"| [{repo['name']}]({repo['html_url']}) | {language} | "
            f"{repo['stargazers_count']} | {repo['forks_count']} |"
        )

    body = "\n".join(lines)
    return f"{body}\n\n---\n"

def generate_growth_section(growth_by_month):
    if not growth_by_month:
        return "## Repo Growth\n\nNo growth data available.\n\n---\n"

    lines = ["## Repo Growth (by month created)\n"]

    for month, count in growth_by_month.items():
        bar = "▓" * count
        lines.append(f"- **{month}**: {count} repo(s) {bar}")

    body = "\n".join(lines)
    return f"{body}\n\n---\n"

def generate_activity_section(active_day):
    day_name, count = active_day
    return f"## Most Active Day\n\n**{day_name}**: {count} updates logged\n\n---\n"

def generate_commit_activity_section(total_commits, pending_repos):
    lines = ["## Commit Activity (last 12 months)\n"]
    lines.append(f"Total commits: {total_commits}")
    if pending_repos:
        lines.append(f"\n{pending_repos} repo(s) still computing stats on GitHub's side, rerun later for a complete count.")
    body = "\n".join(lines)
    return f"{body}\n\n---\n"

def generate_footer():
    return "\n*Report generated automatically by GitHub Stats Dashboard*\n"

def build_report_data(profile, language_counter, top_repos, growth_by_month, active_day, total_commits, pending_repos):
    """Same stats as build_full_report, as a plain JSON-serializable dict."""
    return {
        "profile": profile,
        "languages": dict(language_counter),
        "top_repos": top_repos,
        "growth_by_month": growth_by_month,
        "most_active_day": {"day": active_day[0], "count": active_day[1]},
        "commit_activity": {"total_commits": total_commits, "pending_repos": pending_repos},
    }

def build_full_report(profile, language_counter, top_repos, growth_by_month, active_day, total_commits, pending_repos):
    sections = [
        generate_header(profile),
        generate_language_section(language_counter),
        generate_top_repos_section(top_repos),
        generate_growth_section(growth_by_month),
        generate_activity_section(active_day),
        generate_commit_activity_section(total_commits, pending_repos),
        generate_footer(),
    ]

    return "\n".join(sections)