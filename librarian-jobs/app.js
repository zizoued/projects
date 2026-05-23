// Bay Area Librarian Jobs — static viewer for data/jobs.json.

const SOURCE_LABELS = {
  calopps: "CalOpps",
  governmentjobs: "GovernmentJobs",
  edjoin: "EdJoin (schools)",
};

const COUNTY_ORDER = [
  "San Francisco", "San Mateo", "Santa Clara",
  "Alameda", "Contra Costa", "Marin",
];

const state = {
  jobs: [],
  countiesActive: new Set(),
  sourcesActive: new Set(),
  sort: "new",
  generatedAt: null,
};

async function load() {
  // Cache-bust so a fresh deploy never serves yesterday's payload.
  const res = await fetch(`data/jobs.json?t=${Date.now()}`);
  const payload = await res.json();
  state.jobs = payload.jobs;
  state.generatedAt = payload.generated_at;

  const counties = COUNTY_ORDER.filter(c =>
    state.jobs.some(j => j.county === c)
  );
  const sources = Object.keys(SOURCE_LABELS).filter(s =>
    state.jobs.some(j => j.source === s)
  );

  state.countiesActive = new Set(counties);
  state.sourcesActive = new Set(sources);

  renderFilters("county-filters", counties, state.countiesActive, c => c);
  renderFilters("source-filters", sources, state.sourcesActive,
                s => SOURCE_LABELS[s] ?? s);

  document.querySelectorAll('input[name="sort"]').forEach(input => {
    input.addEventListener("change", e => {
      state.sort = e.target.value;
      render();
    });
  });

  render();
}

function renderFilters(containerId, items, activeSet, labelFn) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";
  items.forEach(item => {
    const label = document.createElement("label");
    label.className = "chip active";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = true;
    cb.dataset.value = item;
    cb.addEventListener("change", () => {
      if (cb.checked) activeSet.add(item);
      else activeSet.delete(item);
      label.classList.toggle("active", cb.checked);
      render();
    });
    label.appendChild(cb);
    label.appendChild(document.createTextNode(" " + labelFn(item)));
    container.appendChild(label);
  });
}

function parseDeadline(j) {
  if (j.closes_date) return new Date(j.closes_date);
  // CalOpps/GovernmentJobs don't always give a parseable date — best effort.
  const m = (j.closes || "").match(/Closes in (\d+) (day|week|month)/i);
  if (!m) return null;
  const n = parseInt(m[1], 10);
  const days = m[2].toLowerCase().startsWith("day") ? n
             : m[2].toLowerCase().startsWith("week") ? n * 7
             : n * 30;
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d;
}

function daysUntil(d) {
  if (!d) return null;
  const ms = d.getTime() - Date.now();
  return Math.ceil(ms / 86400000);
}

function isNew(j) {
  if (!j.first_seen) return false;
  const seen = new Date(j.first_seen + "T00:00:00");
  const ageDays = (Date.now() - seen.getTime()) / 86400000;
  return ageDays < 2; // surfaced in the last ~24h
}

function render() {
  const filtered = state.jobs.filter(j =>
    state.countiesActive.has(j.county) && state.sourcesActive.has(j.source)
  );

  const sorted = [...filtered].sort((a, b) => {
    if (state.sort === "title") return a.title.localeCompare(b.title);
    if (state.sort === "deadline") {
      const da = parseDeadline(a), db = parseDeadline(b);
      if (!da && !db) return 0;
      if (!da) return 1;
      if (!db) return -1;
      return da - db;
    }
    // "new": first_seen desc, then deadline
    const fa = a.first_seen || "", fb = b.first_seen || "";
    if (fa !== fb) return fb.localeCompare(fa);
    const da = parseDeadline(a), db = parseDeadline(b);
    if (!da) return 1;
    if (!db) return -1;
    return da - db;
  });

  const root = document.getElementById("jobs");
  root.innerHTML = "";

  if (sorted.length === 0) {
    const div = document.createElement("div");
    div.className = "empty";
    div.textContent = "No jobs match the current filters.";
    root.appendChild(div);
  } else if (state.sort === "new" || state.sort === "deadline") {
    // Flat list — sorting overrides county grouping.
    sorted.forEach(j => root.appendChild(renderJob(j)));
  } else {
    // Group by county
    for (const county of COUNTY_ORDER) {
      const group = sorted.filter(j => j.county === county);
      if (group.length === 0) continue;
      const section = document.createElement("section");
      section.className = "county-section";
      const h2 = document.createElement("h2");
      h2.textContent = `${county} County · ${group.length}`;
      section.appendChild(h2);
      group.forEach(j => section.appendChild(renderJob(j)));
      root.appendChild(section);
    }
  }

  document.getElementById("job-count").textContent = filtered.length;
  document.getElementById("new-count").textContent =
    state.jobs.filter(isNew).length;

  if (state.generatedAt) {
    const d = new Date(state.generatedAt);
    document.getElementById("generated-at").textContent =
      d.toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" });
  }
}

function renderJob(j) {
  const card = document.createElement("article");
  card.className = "job";

  const header = document.createElement("div");
  header.className = "job-header";
  const h3 = document.createElement("h3");
  const a = document.createElement("a");
  a.href = j.url;
  a.target = "_blank";
  a.rel = "noopener";
  a.textContent = j.title;
  h3.appendChild(a);
  header.appendChild(h3);

  const badges = document.createElement("div");
  badges.className = "badges";
  if (isNew(j)) {
    const b = document.createElement("span");
    b.className = "badge new";
    b.textContent = "New";
    badges.appendChild(b);
  }
  const d = daysUntil(parseDeadline(j));
  if (d !== null && d >= 0 && d <= 5) {
    const b = document.createElement("span");
    b.className = "badge closing-soon";
    b.textContent = d === 0 ? "Closes today" :
                    d === 1 ? "Closes tomorrow" :
                    `Closes in ${d}d`;
    badges.appendChild(b);
  }
  const src = document.createElement("span");
  src.className = "badge source";
  src.textContent = SOURCE_LABELS[j.source] ?? j.source;
  badges.appendChild(src);
  header.appendChild(badges);

  card.appendChild(header);

  const agency = document.createElement("p");
  agency.className = "job-agency";
  agency.textContent = j.agency;
  card.appendChild(agency);

  const meta = document.createElement("p");
  meta.className = "job-meta";
  if (j.location) meta.appendChild(metaItem("location", j.location));
  if (j.employment_type) meta.appendChild(metaItem("type", j.employment_type));
  if (j.salary) meta.appendChild(metaItem("salary", j.salary));
  if (j.closes && !badges.querySelector(".closing-soon")) {
    const span = metaItem("deadline", j.closes);
    if (d !== null && d <= 7) span.classList.add("closing-soon");
    meta.appendChild(span);
  }
  card.appendChild(meta);

  return card;
}

function metaItem(cls, text) {
  const span = document.createElement("span");
  span.className = cls;
  span.textContent = text;
  return span;
}

load().catch(err => {
  document.getElementById("jobs").innerHTML =
    `<div class="empty">Couldn't load jobs.json — ${err.message}</div>`;
});
