/**
 * Agent Monitor demo — solo frontend, datos estáticos JSON.
 */

const statusEl = document.getElementById("status");
const statsEl = document.getElementById("stats");
const listEl = document.getElementById("eventList");
const filterType = document.getElementById("filterType");
const filterQuery = document.getElementById("filterQuery");
const btnExport = document.getElementById("btnExport");

let map;
let layerGroup;
let allEvents = [];

async function loadData() {
  const res = await fetch("data/events.json", { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data.events || [];
}

function initMap() {
  map = L.map("map", { scrollWheelZoom: true }).setView([-17.8, -63.2], 6);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap",
  }).addTo(map);
  layerGroup = L.layerGroup().addTo(map);
}

function renderStats(events) {
  const byModel = {};
  let totalDur = 0;
  for (const e of events) {
    byModel[e.model] = (byModel[e.model] || 0) + 1;
    totalDur += e.duration_s || 0;
  }
  statsEl.innerHTML = "";
  const cards = [
    { k: "Eventos", v: events.length },
    { k: "Duración Σ (s)", v: totalDur },
    { k: "Modelos", v: Object.keys(byModel).length },
  ];
  for (const c of cards) {
    const div = document.createElement("div");
    div.className = "stat-card";
    div.innerHTML = `<strong>${c.v}</strong><span>${c.k}</span>`;
    statsEl.appendChild(div);
  }
}

function populateFilterTypes(events) {
  const types = new Set(events.map((e) => e.label));
  filterType.innerHTML = '<option value="all">Todos</option>';
  for (const t of types) {
    const opt = document.createElement("option");
    opt.value = t;
    opt.textContent = t;
    filterType.appendChild(opt);
  }
}

function matchesFilters(e) {
  const t = filterType.value;
  if (t !== "all" && e.label !== t) return false;
  const q = (filterQuery.value || "").trim().toLowerCase();
  if (!q) return true;
  const hay = `${e.label} ${e.model} ${e.detail} ${e.region}`.toLowerCase();
  return hay.includes(q);
}

function renderList(events) {
  listEl.innerHTML = "";
  const filtered = events.filter(matchesFilters);
  for (const e of filtered) {
    const li = document.createElement("li");
    li.innerHTML = `<strong>${e.label}</strong> · ${e.model}<br /><small>${e.region} — ${e.detail}</small>`;
    listEl.appendChild(li);
  }
}

function renderMarkers(events) {
  layerGroup.clearLayers();
  const filtered = events.filter(matchesFilters);
  const bounds = [];
  for (const e of filtered) {
    const m = L.circleMarker([e.lat, e.lng], {
      radius: 10,
      color: "#3d9eff",
      fillColor: "#3ecf8e",
      fillOpacity: 0.7,
    }).bindPopup(
      `<b>${e.label}</b><br/>${e.model}<br/><small>${e.detail}</small>`,
    );
    m.addTo(layerGroup);
    bounds.push([e.lat, e.lng]);
  }
  if (bounds.length) {
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 8 });
  }
}

function refresh() {
  renderList(allEvents);
  renderMarkers(allEvents);
}

async function main() {
  try {
    initMap();
    allEvents = await loadData();
    renderStats(allEvents);
    populateFilterTypes(allEvents);
    filterType.addEventListener("change", refresh);
    filterQuery.addEventListener("input", refresh);
    btnExport.addEventListener("click", exportFilteredJson);
    refresh();
  } catch (err) {
    statusEl.textContent = `Error: ${err.message} (usá http.server, no abras file://)`;
    console.error(err);
  }
}

main();
