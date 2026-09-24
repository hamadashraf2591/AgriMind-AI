const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const charts = {};
const fmt = n => Number(n).toLocaleString("en-US");
const sleep = ms => new Promise(r => setTimeout(r, ms));
const dayName = d => new Date(d + "T00:00:00").toLocaleDateString("en-US", { weekday: "short" });

const PAGES = {
  dashboard: ["Crop Analysis", "Upload a leaf image and field data for a complete AI diagnosis"],
  weather: ["Weather Intelligence", "Live 7-day forecast with farming advisory"],
  advisor: ["Crop Advisor", "Find the most suitable crop for your soil and climate"],
  fertilizer: ["Fertilizer Calculator", "Exact Urea, DAP and MOP requirement with cost"],
  history: ["Analysis History", "All saved farm reports and trends"],
  library: ["Disease Library", "Symptoms, causes, treatment and prevention"],
  about: ["AI Models", "How AgriMind AI thinks"]
};

/* ---------------- navigation / theme / clock / toast ---------------- */
function go(page) {
  $$(".nav").forEach(n => n.classList.toggle("active", n.dataset.page === page));
  $$(".page").forEach(p => p.classList.toggle("active", p.id === "page-" + page));
  $("#pageTitle").textContent = PAGES[page][0];
  $("#pageSub").textContent = PAGES[page][1];
  $("#sidebar").classList.remove("open");
  if (page === "history") loadHistory();
  if (page === "library") loadLibrary();
  if (page === "about") loadModels();
  if (page === "weather" && $("#wxWrap").classList.contains("hidden")) loadWeather();
  window.scrollTo({ top: 0, behavior: "smooth" });
}
$$(".nav").forEach(n => n.addEventListener("click", () => go(n.dataset.page)));
$("#menuBtn").onclick = () => $("#sidebar").classList.toggle("open");

function applyTheme(t) {
  document.documentElement.dataset.theme = t;
  $("#themeBtn").textContent = t === "dark" ? "☀️" : "🌙";
  localStorage.setItem("agri-theme", t);
}
applyTheme(localStorage.getItem("agri-theme") || "dark");
$("#themeBtn").onclick = () => applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");

function tick() {
  $("#clock").textContent = new Date().toLocaleString("en-US", { weekday: "short", hour: "2-digit", minute: "2-digit", second: "2-digit" });
}
tick(); setInterval(tick, 1000);

function toast(msg, type = "ok") {
  const t = document.createElement("div");
  t.className = "toast " + type; t.textContent = msg;
  $("#toasts").appendChild(t);
  setTimeout(() => t.classList.add("show"), 10);
  setTimeout(() => { t.classList.remove("show"); setTimeout(() => t.remove(), 300); }, 3500);
}

Chart.defaults.color = "#8fb09c";
Chart.defaults.font.family = "Poppins";
Chart.defaults.borderColor = "rgba(143,176,156,.15)";
Chart.defaults.maintainAspectRatio = false;
function chart(id, cfg) { if (charts[id]) charts[id].destroy(); charts[id] = new Chart($("#" + id), cfg); }

function wx(c) {
  if (c === 0) return ["☀️", "Clear sky"];
  if (c <= 3) return ["⛅", "Partly cloudy"];
  if (c <= 48) return ["🌫️", "Foggy"];
  if (c <= 57) return ["🌦️", "Drizzle"];
  if (c <= 67) return ["🌧️", "Rain"];
  if (c <= 77) return ["❄️", "Snow"];
  if (c <= 82) return ["🌧️", "Rain showers"];
  return ["⛈️", "Thunderstorm"];
}

/* ---------------- stats strip ---------------- */
async function loadStats() {
  const s = await (await fetch("/api/stats")).json();
  $("#sTotal").textContent = s.total;
  $("#sHealth").textContent = s.avg_health + "%";
  $("#sThreat").textContent = s.top_disease;
  $("#sRevenue").textContent = "Rs " + fmt(s.total_revenue);
  return s;
}
loadStats();

/* ---------------- upload ---------------- */
const drop = $("#drop"), fileInput = $("#file");
drop.addEventListener("click", () => fileInput.click());
["dragenter", "dragover"].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add("drag"); }));
["dragleave", "drop"].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove("drag"); }));
drop.addEventListener("drop", e => { if (e.dataTransfer.files.length) { fileInput.files = e.dataTransfer.files; showPreview(); } });
fileInput.addEventListener("change", showPreview);
function showPreview() {
  const f = fileInput.files[0];
  if (!f) return;
  if (f.size > 10 * 1024 * 1024) { toast("File 10MB se bari hai", "err"); fileInput.value = ""; return; }
  $("#preview").src = URL.createObjectURL(f);
  drop.classList.add("has");
  $("#fileInfo").textContent = `📎 ${f.name} · ${(f.size / 1024).toFixed(0)} KB`;
}

/* ---------------- presets ---------------- */
const PRESETS = {
  wheat:  { farmer: "Ali Khan", city: "Lahore", crop_type: 0, crop_stage: 1, temperature: 21, humidity: 55, soil_ph: 7.0, soil_moisture: 28, soil_n: 120, soil_p: 55, soil_k: 60, rainfall: 450, rain7: 8, area: 5 },
  rice:   { farmer: "Ghulam Hussain", city: "Larkana", crop_type: 1, crop_stage: 2, temperature: 32, humidity: 82, soil_ph: 6.3, soil_moisture: 45, soil_n: 90, soil_p: 45, soil_k: 45, rainfall: 1400, rain7: 40, area: 3 },
  cotton: { farmer: "Ahmed Raza", city: "Multan", crop_type: 3, crop_stage: 1, temperature: 38, humidity: 45, soil_ph: 7.6, soil_moisture: 14, soil_n: 80, soil_p: 30, soil_k: 25, rainfall: 600, rain7: 0, area: 4 }
};
$$("[data-preset]").forEach(b => b.onclick = () => {
  const p = PRESETS[b.dataset.preset];
  Object.entries(p).forEach(([k, v]) => { const el = $(`#analyzeForm [name=${k}]`); if (el) el.value = v; });
  toast(`Preset loaded: ${b.textContent.trim()}`);
});

/* ---------------- live weather fill ---------------- */
$("#fillWeather").onclick = async () => {
  const city = $("#city").value.trim();
  if (!city) return toast("Pehle city ka naam likho", "err");
  const w = await (await fetch("/api/weather?city=" + encodeURIComponent(city))).json();
  $("[name=temperature]").value = w.current.temp;
  $("[name=humidity]").value = w.current.humidity;
  toast(w.live ? `🛰️ Live weather: ${w.city} · ${w.current.temp}°C` : "Live weather unavailable, offline data used", w.live ? "ok" : "warn");
};

/* ---------------- analysis ---------------- */
async function animateSteps() {
  const steps = $$("#loader .step");
  steps.forEach(s => s.classList.remove("active", "done"));
  for (const s of steps) { s.classList.add("active"); await sleep(550); s.classList.remove("active"); s.classList.add("done"); }
}

$("#analyzeForm").addEventListener("submit", async e => {
  e.preventDefault();
  if (!fileInput.files[0]) return toast("Pehle leaf image upload karo 📷", "err");
  const btn = $("#analyzeBtn");
  btn.disabled = true;
  $("#loader").classList.add("show");
  try {
    const [d] = await Promise.all([
      fetch("/api/analyze", { method: "POST", body: new FormData(e.target) }).then(r => r.json()),
      animateSteps()
    ]);
    if (!d.ok) throw new Error(d.error || "Analysis failed");
    renderResult(d);
    loadStats();
    toast("Analysis complete ✅");
  } catch (err) {
    toast(err.message, "err");
  } finally {
    $("#loader").classList.remove("show");
    btn.disabled = false;
  }
});

function renderFert(f) {
  return `<table><thead><tr><th>Fertilizer</th><th>kg/ha</th><th>Total</th><th>Bags</th><th>Cost</th></tr></thead><tbody>
    ${f.items.map(i => `<tr><td>${i.name}<br><small>${i.nutrient}</small></td><td>${i.kg_ha}</td><td>${i.total_kg} kg</td><td><b>${i.bags}</b></td><td>Rs ${fmt(i.cost)}</td></tr>`).join("")}
    </tbody></table>
    <p class="muted" style="margin-top:10px">Target N-P-K for ${f.crop}: ${f.target.N}-${f.target.P}-${f.target.K} kg/ha · Deficit: ${f.deficit.N}-${f.deficit.P}-${f.deficit.K}</p>
    <div class="total"><span>Total cost (${f.area} ha)</span><span>Rs ${fmt(f.total_cost)}</span></div>`;
}

function cropRows(list) {
  return list.map(c => `<div class="crop-row"><span class="ic">${c.icon}</span><div class="grow">
    <div class="top"><b>${c.crop}</b><span>${c.score}%</span></div>
    <div class="bar green"><div style="width:${c.score}%"></div></div></div></div>`).join("");
}

function renderResult(d) {
  const R = $("#results");
  R.classList.remove("hidden");

  const C = 2 * Math.PI * 52;
  const col = d.crop_health >= 80 ? "#34d399" : d.crop_health >= 60 ? "#a3e635" : d.crop_health >= 40 ? "#f59e0b" : "#ef4444";
  const arc = $("#gaugeArc");
  arc.style.strokeDasharray = C;
  arc.style.strokeDashoffset = C;
  arc.style.stroke = col;
  setTimeout(() => arc.style.strokeDashoffset = C * (1 - d.crop_health / 100), 50);
  $("#gaugeVal").textContent = d.crop_health + "%";
  $("#healthLabel").textContent = d.health_label;
  $("#healthLabel").style.color = col;

  const info = d.disease_info;
  $("#kDisease").textContent = info.icon + " " + d.disease;
  $("#kDiseaseSub").innerHTML = `${d.disease === "Healthy" ? "Risk" : "Confidence"}: <b>${d.disease_probability}%</b>
    <span class="badge" style="background:${info.color}22;color:${info.color}">${info.severity}</span>`;
  $("#kWater").textContent = d.water_label;
  $("#kWaterSub").textContent = `${d.water_mm} mm/day · ${fmt(d.water_litres)} L/day`;
  $("#kYield").textContent = d.expected_yield + " t";
  $("#kYieldSub").textContent = `${d.yield_per_hectare} t/ha · ${d.crop_icon} ${d.crop}`;
  $("#kRevenue").textContent = "Rs " + fmt(d.revenue);
  $("#kRevenueSub").textContent = `@ Rs ${fmt(d.price)}/tonne`;

  $("#imgOrig").src = d.image_url;
  $("#imgHeat").src = d.heatmap_url;
  $("#affected").textContent = d.affected_area + "%";
  setTimeout(() => $("#affBar").style.width = Math.min(d.affected_area, 100) + "%", 50);

  $("#dInfo").innerHTML = `<div class="section-title"><h3>${info.icon} ${d.disease}: Disease Intelligence</h3>
    <span class="badge" style="background:${info.color}22;color:${info.color};font-size:.8rem;padding:5px 12px">Severity: ${info.severity}</span></div>
    <div class="dinfo">
      <div><h5>🧬 Cause</h5><p>${info.cause}</p></div>
      <div><h5>🔍 Symptoms</h5><p>${info.symptoms}</p></div>
      <div><h5>💊 Chemical Treatment</h5><p>${info.treatment}</p></div>
      <div><h5>🌿 Organic Treatment</h5><p>${info.organic}</p></div>
      <div><h5>🛡️ Prevention</h5><p>${info.prevention}</p></div>
      <div><h5>📍 Crop Stage</h5><p>${d.crop} · ${d.stage}</p></div>
    </div>`;

  chart("probChart", {
    type: "doughnut",
    data: { labels: Object.keys(d.disease_all), datasets: [{ data: Object.values(d.disease_all),
      backgroundColor: ["#22c55e", "#ef4444", "#f97316", "#cbd5e1", "#a855f7"], borderWidth: 0 }] },
    options: { cutout: "65%", plugins: { legend: { position: "bottom" } } }
  });

  const p = d.irrigation_plan;
  chart("irrChart", {
    data: { labels: p.map(x => dayName(x.date)), datasets: [
      { type: "bar", label: "Water need (mm)", data: p.map(x => x.water_mm), backgroundColor: "#34d399", borderRadius: 6 },
      { type: "line", label: "Rain (mm)", data: p.map(x => x.rain), borderColor: "#38bdf8", backgroundColor: "#38bdf8", tension: .35 }] },
    options: { plugins: { legend: { position: "bottom" } }, scales: { y: { beginAtZero: true } } }
  });
  $("#irrTable").innerHTML = p.map(x => `<tr><td>${dayName(x.date)} <small>${x.date.slice(5)}</small></td>
    <td>${wx(x.code)[0]} ${x.tmax}° / ${x.tmin}°</td><td>${x.rain} mm</td><td>${x.water_mm} mm</td>
    <td><span class="pill ${x.action.toLowerCase()}">${x.action}</span></td></tr>`).join("");
  $("#wxSource").textContent = d.weather_live ? "🛰️ Live: " + d.weather_city : "📡 Simulated forecast (add city for live)";

  $("#fertBox").innerHTML = renderFert(d.fertilizer);
  $("#bestCrops").innerHTML = cropRows(d.best_crops) + `<p class="muted">Based on your soil N-P-K, pH, temperature, humidity and rainfall.</p>`;
  $("#recList").innerHTML = d.recommendations.map(r => `<div class="rec ${r.level}"><span>${r.icon}</span><p>${r.text}</p></div>`).join("");
  $("#reportBtn").href = "/report/" + d.id;
  R.scrollIntoView({ behavior: "smooth" });
}

/* ---------------- weather page ---------------- */
async function loadWeather() {
  const city = $("#wxCity").value.trim() || "Lahore";
  const w = await (await fetch("/api/weather?city=" + encodeURIComponent(city))).json();
  $("#wxWrap").classList.remove("hidden");
  const [ic, txt] = wx(w.current.code);
  $("#wxNow").innerHTML = `<span class="big">${ic}</span><div><h2>${w.current.temp}°C</h2><p>${txt} · ${w.city}</p>
    <p style="font-size:.75rem">${w.live ? "🛰️ Live data from Open-Meteo" : "📡 Offline simulated data"}</p></div>
    <div class="meta"><div><b>${w.current.humidity}%</b>Humidity</div><div><b>${w.current.wind} km/h</b>Wind</div><div><b>${w.current.precip} mm</b>Rain</div></div>`;
  $("#wxDays").innerHTML = w.days.map(d => `<div class="wx-day"><small>${dayName(d.date)}</small><div class="e">${wx(d.code)[0]}</div>
    <b>${Math.round(d.tmax)}° / ${Math.round(d.tmin)}°</b><small>💧 ${d.rain} mm</small></div>`).join("");
  chart("wxChart", {
    data: { labels: w.days.map(d => dayName(d.date)), datasets: [
      { type: "line", label: "Max °C", data: w.days.map(d => d.tmax), borderColor: "#f97316", backgroundColor: "#f97316", tension: .35 },
      { type: "line", label: "Min °C", data: w.days.map(d => d.tmin), borderColor: "#38bdf8", backgroundColor: "#38bdf8", tension: .35 },
      { type: "bar", label: "Rain mm", data: w.days.map(d => d.rain), backgroundColor: "#34d39988", borderRadius: 6 }] },
    options: { plugins: { legend: { position: "bottom" } } }
  });
  const adv = [];
  const rainy = w.days.filter(d => d.rain >= 5);
  const hot = w.days.filter(d => d.tmax >= 38);
  const spray = w.days.find(d => d.rain < 1 && d.tmax < 35);
  if (rainy.length) adv.push(["🌧️", "info", `Rain expected on ${rainy.map(d => dayName(d.date)).join(", ")}. Delay irrigation and pesticide spraying.`]);
  else adv.push(["☀️", "warn", "No significant rain this week. Plan irrigation carefully."]);
  if (hot.length) adv.push(["🌡️", "danger", `Heat stress risk on ${hot.map(d => dayName(d.date)).join(", ")}. Irrigate in the evening.`]);
  if (w.current.humidity > 80) adv.push(["🍄", "warn", "High humidity: fungal disease risk is elevated. Scout fields."]);
  if (spray) adv.push(["🧴", "ok", `Best day for spraying: ${dayName(spray.date)} (dry and mild).`]);
  if (w.current.wind > 20) adv.push(["💨", "warn", "Strong winds: avoid spraying to prevent drift."]);
  $("#wxAdvice").innerHTML = adv.map(a => `<div class="rec ${a[1]}"><span>${a[0]}</span><p>${a[2]}</p></div>`).join("");
  toast(w.live ? `Forecast loaded: ${w.city}` : "Live weather unavailable, showing simulated data", w.live ? "ok" : "warn");
}
$("#wxBtn").onclick = loadWeather;
$("#wxCity").addEventListener("keydown", e => { if (e.key === "Enter") loadWeather(); });

/* ---------------- crop advisor ---------------- */
$("#advisorForm").addEventListener("submit", async e => {
  e.preventDefault();
  const body = JSON.stringify(Object.fromEntries(new FormData(e.target)));
  const r = await (await fetch("/api/recommend-crop", { method: "POST", headers: { "Content-Type": "application/json" }, body })).json();
  if (!r.ok) return toast(r.error, "err");
  const top = r.ranked[0];
  $("#advisorOut").className = "";
  $("#advisorOut").innerHTML = `<div class="winner"><div class="big">${top.icon}</div><h3>${top.crop}</h3>
    <p class="muted">${top.score}% match · Market ~Rs ${fmt(top.price)}/tonne</p></div>${cropRows(r.ranked)}`;
  toast(`Best crop: ${top.crop} 🌱`);
});

/* ---------------- fertilizer ---------------- */
$("#fertForm").addEventListener("submit", async e => {
  e.preventDefault();
  const body = JSON.stringify(Object.fromEntries(new FormData(e.target)));
  const r = await (await fetch("/api/fertilizer", { method: "POST", headers: { "Content-Type": "application/json" }, body })).json();
  if (!r.ok) return toast(r.error, "err");
  $("#fertOut").className = "";
  $("#fertOut").innerHTML = renderFert(r.plan);
  toast("Fertilizer plan ready 🧪");
});

/* ---------------- history ---------------- */
async function loadHistory() {
  const [rows, s] = await Promise.all([fetch("/api/history").then(r => r.json()), loadStats()]);
  $("#histTable").innerHTML = rows.length ? rows.map(r => `<tr>
    <td><img class="thumb" src="/uploads/${r.image}"></td><td>${r.created}</td><td>${r.farmer}</td><td>${r.crop}</td>
    <td>${r.disease}</td><td><b>${r.health}%</b></td><td>${r.yield_t} t</td><td>Rs ${fmt(r.revenue)}</td>
    <td style="white-space:nowrap"><a class="btn-outline" href="/report/${r.id}" target="_blank">📄</a>
    <a class="btn-outline" style="border-color:#ef4444;color:#ef4444;cursor:pointer" onclick="delRow(${r.id})">🗑️</a></td></tr>`).join("")
    : `<tr><td colspan="9" class="empty">No analyses yet. Run your first crop analysis!</td></tr>`;
  chart("trendChart", {
    type: "line",
    data: { labels: s.trend.map(t => t.date), datasets: [{ label: "Crop Health %", data: s.trend.map(t => t.health),
      borderColor: "#34d399", backgroundColor: "#34d39933", fill: true, tension: .35 }] },
    options: { scales: { y: { min: 0, max: 100 } }, plugins: { legend: { display: false } } }
  });
  chart("distChart", {
    type: "pie",
    data: { labels: Object.keys(s.dist), datasets: [{ data: Object.values(s.dist),
      backgroundColor: ["#22c55e", "#ef4444", "#f97316", "#cbd5e1", "#a855f7"], borderWidth: 0 }] },
    options: { plugins: { legend: { position: "bottom" } } }
  });
}
async function delRow(id) {
  if (!confirm("Delete this analysis?")) return;
  await fetch("/api/history/" + id, { method: "DELETE" });
  toast("Deleted 🗑️", "warn");
  loadHistory();
}

/* ---------------- library ---------------- */
async function loadLibrary() {
  const lib = await (await fetch("/api/diseases")).json();
  $("#libGrid").innerHTML = Object.entries(lib).map(([name, i]) => `<div class="card">
    <h3>${i.icon} ${name} <span class="badge" style="background:${i.color}22;color:${i.color}">${i.severity}</span></h3>
    <p><b>Cause:</b> ${i.cause}</p><p><b>Symptoms:</b> ${i.symptoms}</p><p><b>Treatment:</b> ${i.treatment}</p>
    <p><b>Organic:</b> ${i.organic}</p><p><b>Prevention:</b> ${i.prevention}</p></div>`).join("");
}

/* ---------------- models ---------------- */
async function loadModels() {
  const m = await (await fetch("/api/models")).json();
  const icons = { disease: "🦠", yield: "📦", irrigation: "💧", crop: "🌱" };
  $("#modelGrid").innerHTML = Object.entries(m).map(([k, v]) => `<div class="card model">
    <h3>${icons[k] || "🤖"} ${v.name}</h3><p>${v.algo}</p><div class="val">${v.value}</div>
    <p><b>${v.metric}</b> · ${fmt(v.samples)} samples · ${v.features} features</p><p>Inputs: ${v.inputs}</p></div>`).join("");
}
