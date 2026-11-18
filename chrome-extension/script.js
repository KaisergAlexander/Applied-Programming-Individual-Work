"use strict";

// ---------- Storage helpers (chrome.storage.local, falls back to localStorage for plain-browser testing) ----------
const store = {
  async get(keys) {
    if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
      return chrome.storage.local.get(keys);
    }
    const out = {};
    for (const k of keys) {
      try { const v = localStorage.getItem(k); if (v !== null) out[k] = JSON.parse(v); } catch (e) { /* ignore */ }
    }
    return out;
  },
  async set(obj) {
    if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
      return chrome.storage.local.set(obj);
    }
    for (const [k, v] of Object.entries(obj)) {
      try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* ignore */ }
    }
  }
};

const $ = (id) => document.getElementById(id);
const todayKey = () => new Date().toISOString().slice(0, 10);

const state = {
  name: "",
  focus: null,          // { text, done, date }
  todos: [],            // { id, text, done }
  use24h: true,
  fahrenheit: false,
  bgMode: "photo",
  bgSeed: null
};

// ---------- Clock & greeting ----------
function pad(n) { return String(n).padStart(2, "0"); }

function renderClock() {
  const now = new Date();
  let h = now.getHours();
  const m = pad(now.getMinutes());
  let suffix = "";
  if (!state.use24h) {
    suffix = h >= 12 ? " PM" : " AM";
    h = h % 12 || 12;
  }
  $("clock").textContent = `${state.use24h ? pad(h) : h}:${m}${suffix}`;

  const hour = now.getHours();
  const word = hour < 5 ? "Good night" : hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
  $("greeting-text").textContent = word;
}

// ---------- Name ----------
function initName() {
  const el = $("name");
  el.textContent = state.name || "friend";
  el.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); el.blur(); } });
  el.addEventListener("blur", () => {
    state.name = el.textContent.trim();
    if (!state.name) el.textContent = "friend";
    store.set({ name: state.name });
  });
}

// ---------- Focus ----------
function renderFocus() {
  const f = state.focus;
  const has = f && f.text && f.date === todayKey();
  $("focus-label").textContent = has ? "Today" : "What is your main focus for today?";
  $("focus-input").hidden = !!has;
  $("focus-done").hidden = !has;
  if (has) {
    $("focus-text").textContent = f.text;
    $("focus-check").checked = !!f.done;
  }
}

function initFocus() {
  $("focus-input").addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    const text = e.target.value.trim();
    if (!text) return;
    state.focus = { text, done: false, date: todayKey() };
    e.target.value = "";
    store.set({ focus: state.focus });
    renderFocus();
  });
  $("focus-check").addEventListener("change", (e) => {
    state.focus.done = e.target.checked;
    store.set({ focus: state.focus });
  });
  $("focus-clear").addEventListener("click", () => {
    state.focus = null;
    store.set({ focus: null });
    renderFocus();
    $("focus-input").focus();
  });
}

// ---------- Todo ----------
function renderTodos() {
  const list = $("todo-list");
  list.textContent = "";
  for (const t of state.todos) {
    const li = document.createElement("li");
    if (t.done) li.className = "done";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = t.done;
    cb.addEventListener("change", () => { t.done = cb.checked; saveTodos(); renderTodos(); });
    const span = document.createElement("span");
    span.textContent = t.text;           // textContent: user text is never interpreted as HTML
    const del = document.createElement("button");
    del.textContent = "×";
    del.title = "Delete";
    del.addEventListener("click", () => { state.todos = state.todos.filter((x) => x.id !== t.id); saveTodos(); renderTodos(); });
    li.append(cb, span, del);
    list.appendChild(li);
  }
  const open = state.todos.filter((t) => !t.done).length;
  $("todo-btn").textContent = open ? `Todo (${open})` : "Todo";
}
function saveTodos() { store.set({ todos: state.todos }); }

function initTodos() {
  $("todo-btn").addEventListener("click", () => {
    const p = $("todo-panel");
    p.hidden = !p.hidden;
    if (!p.hidden) $("todo-input").focus();
  });
  $("todo-input").addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    const text = e.target.value.trim();
    if (!text) return;
    state.todos.push({ id: Date.now(), text, done: false });
    e.target.value = "";
    saveTodos();
    renderTodos();
  });
  renderTodos();
}

// ---------- Quote (same quote all day) ----------
function renderQuote() {
  const d = new Date();
  const dayNumber = Math.floor(d.getTime() / 86400000);
  const [text, author] = QUOTES[dayNumber % QUOTES.length];
  $("quote-text").textContent = `“${text}”`;
  $("quote-author").textContent = author;
}

// ---------- Background ----------
function applyBackground() {
  const bg = $("bg");
  if (state.bgMode === "gradient") { bg.style.backgroundImage = ""; return; }
  const seed = state.bgSeed || todayKey();
  const url = `https://picsum.photos/seed/${encodeURIComponent(seed)}/1920/1080`;
  const img = new Image();
  img.onload = () => { bg.style.backgroundImage = `url("${url}")`; };
  img.onerror = () => { bg.style.backgroundImage = ""; };   // offline: keep the gradient
  img.src = url;
}

// ---------- Weather (Open-Meteo, no API key) ----------
const WEATHER_CODES = [
  [[0], "☀️"], [[1, 2], "⛅"], [[3], "☁️"], [[45, 48], "🌫️"],
  [[51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82], "🌧️"],
  [[71, 73, 75, 77, 85, 86], "❄️"], [[95, 96, 99], "⛈️"]
];
function weatherIcon(code) {
  const hit = WEATHER_CODES.find(([codes]) => codes.includes(code));
  return hit ? hit[1] : "🌡️";
}

async function loadWeather() {
  const box = $("weather");
  try {
    const cached = (await store.get(["weatherCache"])).weatherCache;
    let data = cached && Date.now() - cached.time < 30 * 60 * 1000 ? cached.data : null;
    if (!data) {
      const pos = await new Promise((res, rej) => navigator.geolocation.getCurrentPosition(res, rej, { timeout: 8000 }));
      const { latitude, longitude } = pos.coords;
      const r = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,weather_code&timezone=auto`);
      if (!r.ok) throw new Error("HTTP " + r.status);
      const j = await r.json();
      data = { temp: j.current.temperature_2m, code: j.current.weather_code, tz: j.timezone };
      store.set({ weatherCache: { time: Date.now(), data } });
    }
    const t = state.fahrenheit ? data.temp * 9 / 5 + 32 : data.temp;
    $("weather-icon").textContent = weatherIcon(data.code);
    $("weather-temp").textContent = `${Math.round(t)}°${state.fahrenheit ? "F" : "C"}`;
    $("weather-place").textContent = (data.tz || "").split("/").pop().replace(/_/g, " ");
  } catch (e) {
    box.hidden = true;     // no location permission / offline: simply hide the widget
  }
}

// ---------- Quick links ----------
function renderLinks() {
  const links = [["Gmail", "https://mail.google.com"], ["YouTube", "https://www.youtube.com"], ["GitHub", "https://github.com"]];
  const box = $("links");
  for (const [label, href] of links) {
    const a = document.createElement("a");
    a.href = href;
    a.textContent = label;
    box.appendChild(a);
  }
}

// ---------- Settings ----------
function initSettings() {
  $("settings-btn").addEventListener("click", () => { $("settings").hidden = !$("settings").hidden; });
  $("opt-24h").checked = state.use24h;
  $("opt-fahrenheit").checked = state.fahrenheit;
  $("opt-bg").value = state.bgMode;
  $("opt-24h").addEventListener("change", (e) => { state.use24h = e.target.checked; store.set({ use24h: state.use24h }); renderClock(); });
  $("opt-fahrenheit").addEventListener("change", (e) => { state.fahrenheit = e.target.checked; store.set({ fahrenheit: state.fahrenheit }); loadWeather(); });
  $("opt-bg").addEventListener("change", (e) => { state.bgMode = e.target.value; store.set({ bgMode: state.bgMode }); applyBackground(); });
  $("refresh-bg").addEventListener("click", () => {
    state.bgSeed = String(Date.now());
    state.bgMode = "photo";
    $("opt-bg").value = "photo";
    store.set({ bgSeed: state.bgSeed, bgMode: "photo" });
    applyBackground();
  });
}

// ---------- Start ----------
(async function main() {
  const saved = await store.get(["name", "focus", "todos", "use24h", "fahrenheit", "bgMode", "bgSeed"]);
  if (typeof saved.name === "string") state.name = saved.name;
  if (saved.focus) state.focus = saved.focus;
  if (Array.isArray(saved.todos)) state.todos = saved.todos;
  if (typeof saved.use24h === "boolean") state.use24h = saved.use24h;
  if (typeof saved.fahrenheit === "boolean") state.fahrenheit = saved.fahrenheit;
  if (saved.bgMode) state.bgMode = saved.bgMode;
  if (saved.bgSeed) state.bgSeed = saved.bgSeed;

  initName();
  initFocus();
  initTodos();
  initSettings();
  renderLinks();
  renderQuote();
  renderFocus();
  renderClock();
  applyBackground();
  loadWeather();
  setInterval(renderClock, 1000);
})();
