# GitHub Stats Dashboard

Automatically fetch your GitHub profile data, analyze contribution patterns, and generate beautiful Markdown reports. No manual tracking. No dashboards to refresh. Just your code, analyzed.

## What It Does

- **Fetches your GitHub stats** via authenticated REST API (repos, commits, stars, languages)
- **Analyzes contribution patterns** (most active day, language breakdown, repo growth over time)
- **Generates a Markdown report** with tables, charts, and trends
- **Timestamps reports** automatically — `reports/github_report_2026-06-20_1432.md`

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
```

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
Fetching GitHub profile...
Fetching repositories (this may take a few seconds)...
Found 14 repos
Analyzing data...
Generating report...
Report saved to: reports/github_report_2026-06-20_1432.md
```

Open `reports/github_report_2026-06-20_1432.md` in your editor or Markdown viewer.

---

## What's in the Report?

Each generated report includes:

- **Header**: Your name, bio, follower count, public repo count
- **Languages**: Language breakdown by repo count with a text-based bar chart
- **Top Repositories**: Your 5 most-starred repos with clickable links
- **Repo Growth**: How many repos you created each month
- **Most Active Day**: Which day of the week you push code most

Example section:
```markdown
## Languages

| Language   | Repos | Share | Visual       |
|------------|-------|-------|--------------|
| Python     | 6     | 60.0% | ██████       |
| JavaScript | 3     | 30.0% | ███          |
| HTML       | 1     | 10.0% | █            |
```

---

## Project Structure

```
github_stats/
├── .env                      # Your secrets (NOT in Git)
├── .env_example              # Template for .env
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
- `get_commit_activity()`: Weekly commit stats (if needed for v2)

### 3. **`analyzer.py`** - Data crunching
Pure logic, no API calls:
- `analyze_languages()`: Counts repos by language
- `top_repos_by_stars()`: Sorts repos by star count
- `repo_growth_by_month()`: Groups repo creation dates by month
- `most_active_day()`: Finds your most active weekday

### 4. **`report_generator.py`** — Markdown formatting
Builds report sections as strings:
- `generate_header()`, `generate_language_section()`, etc.
- `build_full_report()`: Stitches all sections together

### 5. **`main.py`** — Orchestration
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
- Check `GITHUB_USERNAME` in `.env` — it must be exact (case-sensitive)

**Report is missing data or sections**
- Some repos may not have detected languages (empty repos)
- Forked repos are excluded (they're not your original work)
- If a repo was created today, it might not appear in growth stats

---

## Dependencies

- **`requests`** — HTTP requests to GitHub API
- **`python-dotenv`** — Load environment variables from `.env`

See `requirements.txt` for exact versions.
