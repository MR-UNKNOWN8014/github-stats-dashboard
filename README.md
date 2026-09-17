# GitHub Stats Dashboard - HTML Dashboard

This branch holds a static, dependency-free HTML/CSS/JS viewer for the JSON
reports produced by the CLI tool on the `master` branch. It lives on its own
branch on purpose and is not meant to be merged back, the CLI and the
dashboard stay separate.

## What it is

- `static/index.html` / `static/style.css` / `static/app.js`: a single-page dashboard. No build
  step, no npm, no framework, opens directly in a browser.
- Renders: profile header, KPI stat tiles (public repos, followers,
  following, commits in the last 12 months, most active day), a byte-based
  language breakdown bar, a repo growth chart, and a top-repos card grid.
- Light/dark theme toggle that remembers your choice, drag-and-drop or
  file-picker loading of a report, and the last-loaded report is remembered
  in your browser only (localStorage, nothing leaves your machine).
- Ships with `sample-data.json` so the dashboard has something to show
  before you load your own report.

## Usage

1. On `master`, generate a report (JSON is the default format):
   ```bash
   python main.py
   ```
2. Open `static/index.html` in a browser (double-click it, no server needed).
3. Drag the generated `.json` file onto the page, or click "Load report"
   and pick it from the file dialog.

## Browser support

Any modern evergreen browser (Chrome, Firefox, Edge, Safari). Uses
`File.text()`, CSS custom properties, and `prefers-color-scheme`, no
polyfills.

## Report format

The dashboard reads exactly what `python main.py` writes (JSON is the default format):
`profile`, `languages`, `top_repos`, `growth_by_month`, `most_active_day`,
`commit_activity`. See `sample-data.json` for the shape.

---

For the CLI tool itself (Python, GitHub API, JSON/Markdown reports), see the
`master` branch.
