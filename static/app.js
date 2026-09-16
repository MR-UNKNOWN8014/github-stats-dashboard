const STORAGE_KEY = "gh-stats-dashboard:last-report";
const THEME_KEY = "gh-stats-dashboard:theme";

const SERIES_VARS = ["--series-1", "--series-2", "--series-3", "--series-4", "--series-5", "--series-6"];
const MAX_LANG_SLICES = 6;

const SAMPLE_DATA = {
  profile: {
    login: "octocat",
    name: "The Octocat",
    bio: "Sample data, load your own report to replace this.",
    avatar_url: "https://avatars.githubusercontent.com/u/583231?v=4",
    html_url: "https://github.com/octocat",
    public_repos: 8,
    followers: 24082,
    following: 9
  },
  languages: { Python: 124457, HTML: 29135, JavaScript: 20089, CSS: 16944, Shell: 969 },
  top_repos: [
    { name: "Spoon-Knife", html_url: "https://github.com/octocat/Spoon-Knife", language: "HTML", stargazers_count: 14035, forks_count: 159336 },
    { name: "Hello-World", html_url: "https://github.com/octocat/Hello-World", language: null, stargazers_count: 3813, forks_count: 6784 },
    { name: "git-consortium", html_url: "https://github.com/octocat/git-consortium", language: "Python", stargazers_count: 613, forks_count: 184 }
  ],
  growth_by_month: { "2011-01": 2, "2014-03": 2, "2014-06": 1, "2016-04": 1 },
  most_active_day: { day: "Wednesday", count: 2 },
  commit_activity: { total_commits: 118, pending_repos: 0 }
};

function isSafeUrl(url) {
  return typeof url === "string" && /^https:\/\//.test(url);
}

function formatBytes(n) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1) + "K";
  return String(n);
}

function el(tag, props = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(props)) {
    if (key === "text") node.textContent = value;
    else if (key === "class") node.className = value;
    else node.setAttribute(key, value);
  }
  for (const child of children) node.appendChild(child);
  return node;
}

function renderProfile(profile) {
  const card = document.getElementById("profile-card");
  card.innerHTML = "";
  card.classList.add("visible");

  if (isSafeUrl(profile.avatar_url)) {
    const img = el("img", { class: "profile-avatar", alt: "avatar" });
    img.src = profile.avatar_url;
    card.appendChild(img);
  }

  const info = el("div");
  info.appendChild(el("p", { class: "profile-name", text: profile.name || profile.login || "Unknown" }));
  if (profile.login) info.appendChild(el("p", { class: "profile-login", text: "@" + profile.login }));
  if (profile.bio) info.appendChild(el("p", { class: "profile-bio", text: profile.bio }));
  card.appendChild(info);
}

function statTile(label, value, note) {
  const tile = el("div", { class: "stat-tile" });
  tile.appendChild(el("p", { class: "stat-label", text: label }));
  tile.appendChild(el("p", { class: "stat-value", text: value }));
  if (note) tile.appendChild(el("p", { class: "stat-note", text: note }));
  return tile;
}

function renderKpis(profile, activeDay, commitActivity) {
  const row = document.getElementById("kpi-row");
  row.innerHTML = "";
  row.appendChild(statTile("Public repos", String(profile.public_repos ?? 0)));
  row.appendChild(statTile("Followers", String(profile.followers ?? 0)));
  row.appendChild(statTile("Following", String(profile.following ?? 0)));
  row.appendChild(statTile(
    "Commits (12mo)",
    String(commitActivity.total_commits ?? 0),
    commitActivity.pending_repos ? `${commitActivity.pending_repos} repo(s) still computing` : null
  ));
  row.appendChild(statTile("Most active day", activeDay.day, `${activeDay.count} updates`));
}

function renderLanguages(languages) {
  const bar = document.getElementById("languages-bar");
  const legend = document.getElementById("languages-legend");
  bar.innerHTML = "";
  legend.innerHTML = "";

  const entries = Object.entries(languages).sort((a, b) => b[1] - a[1]);
  if (entries.length === 0) {
    bar.appendChild(el("p", { class: "stat-note", text: "No language data available." }));
    return;
  }

  const total = entries.reduce((sum, [, bytes]) => sum + bytes, 0);
  const top = entries.slice(0, MAX_LANG_SLICES);
  const rest = entries.slice(MAX_LANG_SLICES);
  const otherBytes = rest.reduce((sum, [, bytes]) => sum + bytes, 0);

  const barEl = el("div", { class: "lang-bar" });
  const slices = otherBytes > 0 ? [...top, ["Other", otherBytes]] : top;

  slices.forEach(([name, bytes], i) => {
    const percent = (bytes / total) * 100;
    const colorVar = name === "Other" ? "var(--series-other)" : `var(${SERIES_VARS[i]})`;
    const segment = el("div", { class: "lang-bar-segment", title: `${name}: ${formatBytes(bytes)}B (${percent.toFixed(1)}%)` });
    segment.style.width = percent + "%";
    segment.style.background = colorVar;
    barEl.appendChild(segment);

    const item = el("li");
    const swatch = el("span", { class: "swatch" });
    swatch.style.background = colorVar;
    item.appendChild(swatch);
    item.appendChild(el("span", { class: "lang-name", text: name }));
    item.appendChild(el("span", { class: "lang-value", text: `${formatBytes(bytes)}B / ${percent.toFixed(1)}%` }));
    legend.appendChild(item);
  });

  bar.appendChild(barEl);
}

function langColor(languages, name) {
  const entries = Object.entries(languages || {}).sort((a, b) => b[1] - a[1]);
  const index = entries.findIndex(([lang]) => lang === name);
  if (index < 0 || index >= MAX_LANG_SLICES) return "var(--series-other)";
  return `var(${SERIES_VARS[index]})`;
}

function renderGrowth(growthByMonth) {
  const chart = document.getElementById("growth-chart");
  chart.innerHTML = "";

  const entries = Object.entries(growthByMonth);
  if (entries.length === 0) {
    chart.appendChild(el("p", { class: "stat-note", text: "No growth data available." }));
    return;
  }

  const max = Math.max(...entries.map(([, count]) => count));
  entries.forEach(([month, count]) => {
    const wrap = el("div", { class: "growth-bar-wrap" });
    const barHeight = Math.max((count / max) * 100, 6);
    const bar = el("div", { class: "growth-bar", title: `${month}: ${count} repo(s)` });
    bar.style.height = barHeight + "%";
    wrap.appendChild(bar);
    wrap.appendChild(el("span", { class: "growth-bar-label", text: month }));
    chart.appendChild(wrap);
  });
}

function renderRepos(topRepos, languages) {
  const grid = document.getElementById("repo-grid");
  grid.innerHTML = "";

  if (!topRepos || topRepos.length === 0) {
    grid.appendChild(el("p", { class: "stat-note", text: "No repos found." }));
    return;
  }

  topRepos.forEach((repo) => {
    const card = el("a", { class: "repo-card" });
    card.href = isSafeUrl(repo.html_url) ? repo.html_url : "#";
    card.target = "_blank";
    card.rel = "noopener";

    card.appendChild(el("span", { class: "repo-name", text: repo.name }));

    const meta = el("div", { class: "repo-meta" });
    if (repo.language) {
      const dot = el("span", { class: "repo-lang-dot" });
      dot.style.background = langColor(languages, repo.language);
      meta.appendChild(dot);
      meta.appendChild(document.createTextNode(repo.language));
      meta.appendChild(document.createTextNode(" · "));
    }
    meta.appendChild(document.createTextNode(`★ ${repo.stargazers_count ?? 0}`));
    meta.appendChild(document.createTextNode(` · fork ${repo.forks_count ?? 0}`));
    card.appendChild(meta);

    grid.appendChild(card);
  });
}

function render(data) {
  renderProfile(data.profile || {});
  renderKpis(data.profile || {}, data.most_active_day || { day: "No data", count: 0 }, data.commit_activity || {});
  renderLanguages(data.languages || {});
  renderGrowth(data.growth_by_month || {});
  renderRepos(data.top_repos || [], data.languages || {});
}

function showLoadError(message) {
  const banner = document.getElementById("dropzone-error");
  if (!message) {
    banner.hidden = true;
    banner.textContent = "";
    return;
  }
  banner.textContent = message;
  banner.hidden = false;
}

function loadFromText(text) {
  let data;
  try {
    data = JSON.parse(text);
  } catch (e) {
    showLoadError("That file isn't valid JSON. Generate one with: python main.py --format json");
    return;
  }
  try {
    render(data);
  } catch (e) {
    showLoadError("That file doesn't match the expected report format.");
    return;
  }
  showLoadError(null);
  try {
    localStorage.setItem(STORAGE_KEY, text);
  } catch (e) {
    // private browsing / storage disabled, nothing to do
  }
}

function setupFileLoading() {
  const input = document.getElementById("file-input");
  input.addEventListener("change", () => {
    const file = input.files[0];
    if (!file) return;
    file.text().then(loadFromText);
  });

  const dropzone = document.getElementById("dropzone");

  // Browsers navigate the whole tab to a dropped file unless every
  // dragover/drop on the page is prevented, not just on the dropzone box,
  // so a drop anywhere else on the page previously blew the page away
  // instead of loading the report.
  window.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("drag-over");
  });
  window.addEventListener("dragleave", (e) => {
    if (e.target === document.documentElement || e.target === document.body) {
      dropzone.classList.remove("drag-over");
    }
  });
  window.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    if (file) file.text().then(loadFromText);
  });
}

function setupTheme() {
  const toggle = document.getElementById("theme-toggle");
  const icon = document.getElementById("theme-icon");

  let saved = null;
  try {
    saved = localStorage.getItem(THEME_KEY);
  } catch (e) {
    // ignore
  }
  if (saved) document.documentElement.setAttribute("data-theme", saved);

  const effective = saved || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  icon.innerHTML = effective === "dark" ? "&#9788;" : "&#9789;";

  toggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme")
      || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    icon.innerHTML = next === "dark" ? "&#9788;" : "&#9789;";
    try {
      localStorage.setItem(THEME_KEY, next);
    } catch (e) {
      // ignore
    }
  });
}

function init() {
  setupTheme();
  setupFileLoading();

  let restored = null;
  try {
    restored = localStorage.getItem(STORAGE_KEY);
  } catch (e) {
    // ignore
  }

  if (restored) {
    loadFromText(restored);
  } else {
    render(SAMPLE_DATA);
  }
}

init();
