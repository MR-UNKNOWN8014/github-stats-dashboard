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

1. On `master`, generate a JSON report:
   ```bash
   python main.py --format json
   ```
2. Open `static/index.html` in a browser (double-click it, no server needed).
3. Drag the generated `.json` file onto the page, or click "Load report"
   and pick it from the file dialog.

## Design notes

- The palette is CVD-checked against the project's data-viz validator, has
  no purple, and every surface (light and dark) is a flat solid color, no
  gradients anywhere.
- The language breakdown is a single segmented bar (the same idea as
  GitHub's own repo-language bar), not a pie or donut. It caps at 6 explicit
  languages plus an "Other" bucket, both for readability and to stay inside
  the palette's color-safety limits at a glance.
- No frameworks, no build tooling, no dependencies. Plain HTML/CSS/vanilla
  JS, so it can be opened as a local file or hosted as a static page (for
  example GitHub Pages) with zero setup.

## Browser support

Any modern evergreen browser (Chrome, Firefox, Edge, Safari). Uses
`File.text()`, CSS custom properties, and `prefers-color-scheme`, no
polyfills.

## Report format

The dashboard reads exactly what `python main.py --format json` writes:
`profile`, `languages`, `top_repos`, `growth_by_month`, `most_active_day`,
`commit_activity`. See `sample-data.json` for the shape.

---

For the CLI tool itself (Python, GitHub API, JSON/Markdown reports), see the
`master` branch.
