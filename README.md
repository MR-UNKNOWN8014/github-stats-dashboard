# GitHub Stats Dashboard

Automatically fetch your GitHub profile data, analyze contribution patterns, and generate beautiful Markdown reports. No manual tracking. No dashboards to refresh. Just your code, analyzed.

## What It Does

- **Fetches your GitHub stats** via authenticated REST API (repos, commits, stars, languages)
- **Analyzes contribution patterns** (most active day, language breakdown, repo growth over time)
- **Generates a Markdown report** with tables, charts, and trends
- **Timestamps reports** automatically: `reports/github_report_2026-06-20_1432.md`

Perfect for portfolio updates, quarterly reviews, or just understanding your own coding habits.

---

## Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/MR-UNKNOWN8014/github-stats-dashboard.git
cd github-stats-dashboard
```

### 2. Set up your environment

**Create a Personal Access Token (PAT):**
1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token (classic)**
3. Give it a name like `github-stats-dashboard`
4. **Scopes:** Check `repo` and `read:user`
5. Set expiration as you like (best is 30 days)
6. Copy the token (you'll only see it once)

**Create `.env` file:**
```bash
cp .env_example .env
```

Then edit `.env` and paste your values:
```env
GITHUB_TOKEN=ghp_your_actual_token_here
GITHUB_USERNAME=your_github_username
GITHUB_INCLUDE_PRIVATE=false
```

Set `GITHUB_INCLUDE_PRIVATE=true` to include your own private repos in the report. This only ever works for the token's own account, GitHub does not let a token see another account's private repos no matter what `GITHUB_USERNAME` is set to, so in this mode `GITHUB_USERNAME` is ignored and the token owner's identity is used instead.

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Generate your first report
```bash
python main.py
```

Output:
```
Fetching GitHub Profile
Fetching GitHub Repos (This may take a minute)
Found 14 repos
Fetching commit activity (12 repos)
Analyzing Data
Generating Report
Report saved to: reports/github_report_2026-06-20_1432.md
```

Note: fetching commit activity makes one extra API call per non-fork repo, so it uses more of your rate limit and takes longer on accounts with many repos.

Open `reports/github_report_2026-06-20_1432.md` in your editor or Markdown viewer.

---

## CLI Usage

```bash
# Check someone else's public profile instead of the one in .env
python main.py -u octocat

# Include your own private repos (only works for the token's own account)
python main.py --private

# Get the raw stats as JSON instead of Markdown
python main.py --format json

# Write to a specific path
python main.py -u octocat -o reports/octocat.md
```

`--username` and `--private` cannot be combined, private repos are only ever visible for the token's own account. Run `python main.py --help` for the full flag list.

---

## What's in the Report?

Each generated report includes:

- **Header**: Your name, bio, follower count, public repo count
- **Languages**: Language breakdown by total bytes across all repos (matches how GitHub's own profile language bars work) with a text-based bar chart
- **Top Repositories**: Your 5 most-starred repos with clickable links
- **Repo Growth**: How many repos you created each month
- **Most Active Day**: Which day of the week you push code most
- **Commit Activity**: Total commits across your non-fork repos over the last 12 months

Example section:
```markdown
## Languages

| Language   | Bytes  | Share | Visual       |
|------------|--------|-------|--------------|
| Python     | 12,400 | 60.0% | ██████       |
| JavaScript | 6,200  | 30.0% | ███          |
| HTML       | 2,100  | 10.0% | █            |
```

---

## Project Structure

```
github_stats/
├── .env                      # Your secrets (NOT in Git)
├── .env_example               # Template for .env
├── .gitignore                
├── requirements.txt          # Python dependencies
├── README.md                 
│
├── config.py                 # Load GitHub token & username from .env
├── github_client.py          # Fetch data from GitHub API
├── analyzer.py               # Analyze repos, languages, growth
├── report_generator.py       # Format data into Markdown
├── main.py                   # Orchestrate the full pipeline
│
└── reports/                  # Generated reports live here
    └── github_report_2026-06-20_1432.md
```

---

## How It Works (Under the Hood)

### 1. **`config.py`** - Secure configuration
Loads `GITHUB_TOKEN` and `GITHUB_USERNAME` from `.env` using `python-dotenv`. Fails loudly if either is missing.

### 2. **`github_client.py`** - API communication
Makes authenticated requests to GitHub REST API:
- `get_user_profile()`: Profile stats (followers, bio, public repos)
- `get_all_repos()`: All your repos with pagination
- `get_commit_activity()`: Weekly commit stats for a single repo
- `get_repo_languages()`: Byte-count-per-language breakdown for a single repo

### 3. **`analyzer.py`** - Data crunching
Pure logic, no API calls:
- `analyze_languages()`: Counts repos by language
- `top_repos_by_stars()`: Sorts repos by star count
- `repo_growth_by_month()`: Groups repo creation dates by month
- `most_active_day()`: Finds your most active weekday
- `total_commits_last_year()`: Sums weekly commit totals for a repo

### 4. **`report_generator.py`** - Markdown formatting
Builds report sections as strings:
- `generate_header()`, `generate_language_section()`, etc.
- `build_full_report()`: Stitches all sections together

### 5. **`main.py`** - Orchestration
Calls functions from all modules in order:
1. Fetch profile & repos
2. Analyze the data
3. Generate Markdown
4. Save to `reports/` with a timestamp

---

## Troubleshooting

**Error: `GITHUB_TOKEN not found`**
- Confirm `.env` exists in the same folder as `main.py`
- Check that `GITHUB_TOKEN=` line has no extra spaces
- Make sure you copied the full token (starts with `ghp_`)

**Error: `401 Unauthorized`**
- Your token is invalid or expired
- Regenerate a new token on GitHub and update `.env`

**Error: `404 Not Found`**
- Check `GITHUB_USERNAME` in `.env`, it must be exact (case-sensitive)

**Error: GitHub rate limit hit**
- You've used up your API quota for the hour, mostly from the per-repo commit activity and language calls
- Wait for the reset time printed in the error, or use a token with a higher rate limit

**Total commits shows 0, or a "still computing" note**
- The first time this tool queries a repo's commit stats, GitHub computes them in the background and returns nothing yet
- The tool retries once after a short delay; if it's still not ready, that repo is reported as pending, rerun later and it'll usually be populated by then

---

## Privacy and Scope

- `GITHUB_USERNAME` can be set to any GitHub account, not just your own, and the report will include everything public: public repos, public profile info, and their languages/commit stats on those public repos.
- Private repos are never visible for an account you don't own, no matter what scopes your token has. A token only ever authorizes what its own account can see. Setting `GITHUB_INCLUDE_PRIVATE=true` only pulls in the token owner's own private repos, it cannot be pointed at someone else's private data.

**Report is missing data or sections**
- Some repos may not have detected languages (empty repos)
- Forked repos are excluded (they're not your original work)
- If a repo was created today, it might not appear in growth stats

---

## Dependencies

- **`requests`**: HTTP requests to GitHub API
- **`python-dotenv`**: Load environment variables from `.env`

See `requirements.txt` for exact versions.
