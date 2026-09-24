(() => {
  const IMG = "/static/img/";
  const CROP = { Wheat: "wheat.jpg", Rice: "rice.jpg", Maize: "maize.jpg", Cotton: "cotton.jpg", Sugarcane: "sugarcane.jpg" };
  const DIS = { "Healthy": "healthy.jpg", "Leaf Blight": "blight.jpg", "Leaf Rust": "rust.jpg", "Powdery Mildew": "mildew.jpg", "Leaf Spot": "spot.jpg" };
  const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html) e.innerHTML = html; return e; };

  /* ---------------- HERO (dashboard) ---------------- */
  const dash = document.getElementById("page-dashboard");
  const form = document.getElementById("analyzeForm");
  dash.prepend(el("div", "hero", `
    <div class="hero-content">
      <span class="hero-tag">🌾 AI-Powered Smart Farming Platform</span>
      <h1>Grow More. <span>Lose Less.</span><br>Farm Smarter with AI</h1>
      <p>Upload a single leaf photo and get instant disease detection, a 7-day irrigation plan,
         yield &amp; profit prediction and exact fertilizer advice, all in one place.</p>
      <div class="hero-btns">
        <button class="btn auto" data-go="scroll">🔍 Start Crop Analysis</button>
        <button class="btn-ghost" data-go="weather">🌦️ Check Weather</button>
      </div>
      <div class="hero-stats">
        <div><b data-count="4">0</b><small>ML Models</small></div>
        <div><b data-count="5">0</b><small>Diseases Detected</small></div>
        <div><b data-count="7">0</b><small>Day Forecast</small></div>
        <div><b data-count="5">0</b><small>Crops Supported</small></div>
      </div>
    </div>
    <div class="hero-float">
      <div class="hf-row"><span>🦠</span><div><small>Disease Scan</small><b>Instant Heatmap</b></div></div>
      <div class="hf-row"><span>🛰️</span><div><small>Weather</small><b>Live 7-Day Forecast</b></div></div>
      <div class="hf-row"><span>💰</span><div><small>Profit</small><b>Yield × Market Price</b></div></div>
    </div>`));

  /* ---------------- FEATURES ---------------- */
  const FEATURES = [
    ["disease.jpg", "🦠", "Disease Detection", "Computer-vision leaf scan classifies 5 disease types and highlights infected spots.", "scroll"],
    ["weather.jpg", "🛰️", "Live Weather", "Real-time 7-day forecast with spraying and irrigation advisory.", "weather"],
    ["irrigation.jpg", "💧", "Smart Irrigation", "Day-by-day watering schedule based on forecast and soil moisture.", "scroll"],
    ["yield.jpg", "📦", "Yield & Profit", "Predict harvest in tonnes and estimated revenue in rupees.", "scroll"],
    ["fertilizer.jpg", "🧪", "Fertilizer Planner", "Exact bags of Urea, DAP and MOP with total cost for your field.", "fertilizer"],
    ["advisor.jpg", "🌱", "Crop Advisor", "Machine learning recommends the most suitable crop for your soil.", "advisor"]
  ];
  const featHead = el("div", "sec-head reveal", `<span>Our Features</span><h2>Everything a Modern Farmer Needs</h2>
    <p>Six powerful AI tools working together to protect your crop and increase your profit.</p>`);
  const feats = el("div", "features", FEATURES.map(f => `
    <div class="feature reveal" data-go="${f[4]}">
      <div class="f-wrap"><div class="f-img" style="background-image:url(${IMG + f[0]})"></div></div>
      <div class="f-body"><div class="f-icon">${f[1]}</div><h3>${f[2]}</h3><p>${f[3]}</p><a>Explore →</a></div>
    </div>`).join(""));

  /* ---------------- HOW IT WORKS ---------------- */
  const stepsHead = el("div", "sec-head reveal", `<span>How It Works</span><h2>3 Simple Steps</h2>`);
  const steps = el("div", "steps", [
    ["📷", "Upload Leaf Photo", "Take a clear photo of the crop leaf and upload it with your field details."],
    ["🧠", "AI Analyzes", "4 machine learning models process the image, soil, and live weather data."],
    ["📋", "Get Action Plan", "Receive diagnosis, irrigation schedule, fertilizer plan and a PDF report."]
  ].map((s, i) => `<div class="card step-card reveal"><div class="step-num">${s[0]}<b>${i + 1}</b></div>
      <h3>${s[1]}</h3><p>${s[2]}</p></div>`).join(""));

  const formHead = el("div", "sec-head reveal", `<span>Start Now</span><h2>Analyze Your Crop</h2>
    <p>Use a quick preset or enter your own field data below.</p>`);
  formHead.id = "startAnalysis";
  form.before(featHead, feats, stepsHead, steps, formHead);

  /* ---------------- PAGE BANNERS ---------------- */
  const BANNERS = {
    weather: ["weather.jpg", "🌦️ Weather Intelligence", "Live 7-day forecast with smart farming advisory"],
    advisor: ["advisor.jpg", "🌱 AI Crop Advisor", "Discover the best crop for your soil and climate"],
    fertilizer: ["fertilizer.jpg", "🧪 Fertilizer Calculator", "Exact Urea, DAP and MOP bags with total cost"],
    history: ["history.jpg", "🗂️ Farm Records", "Every analysis saved with trends and printable reports"],
    library: ["library.jpg", "📚 Disease Library", "Symptoms, causes, treatments and prevention"],
    about: ["models.jpg", "🤖 Inside AgriMind AI", "Four machine learning models working together"]
  };
  Object.entries(BANNERS).forEach(([k, [img, t, s]]) => {
    const p = document.getElementById("page-" + k);
    if (!p) return;
    const b = el("div", "page-banner", `<h2>${t}</h2><p>${s}</p>`);
    b.style.backgroundImage = `linear-gradient(90deg,rgba(3,20,11,.92),rgba(3,20,11,.35)),url(${IMG + img})`;
    p.prepend(b);
  });

  /* ---------------- FOOTER ---------------- */
  document.querySelector(".main").appendChild(el("footer", "site-footer", `
    <div class="ft-grid">
      <div><h3>🌾 AgriMind AI</h3>
        <p>AI-powered decision support for modern farmers. Detect diseases early, save water and grow more profitable crops.</p>
        <div class="socials"><span>📘</span><span>📸</span><span>▶️</span><span>💼</span></div></div>
      <div><h4>Tools</h4><a data-go="scroll">Crop Analysis</a><a data-go="weather">Weather</a>
        <a data-go="advisor">Crop Advisor</a><a data-go="fertilizer">Fertilizer</a></div>
      <div><h4>Resources</h4><a data-go="library">Disease Library</a><a data-go="history">History</a><a data-go="about">AI Models</a></div>
      <div><h4>Contact</h4><p>📍 Pakistan<br>✉️ support@agrimind.ai<br>📞 +92 300 0000000</p></div>
    </div>
    <div class="ft-bottom"><span>© ${new Date().getFullYear()} AgriMind AI · All rights reserved</span><span>Built with 💚 for farmers</span></div>`));

  /* ---------------- NAVIGATION CLICKS ---------------- */
  document.addEventListener("click", e => {
    const g = e.target.closest("[data-go]");
    if (!g) return;
    const t = g.dataset.go;
    if (t === "scroll") {
      if (!dash.classList.contains("active")) go("dashboard");
      setTimeout(() => document.getElementById("startAnalysis").scrollIntoView({ behavior: "smooth" }), 350);
    } else go(t);
  });

  /* ---------------- COUNTERS ---------------- */
  document.querySelectorAll("[data-count]").forEach(c => {
    const end = +c.dataset.count; let n = 0;
    const iv = setInterval(() => { n++; c.textContent = n; if (n >= end) clearInterval(iv); }, 180);
  });

  /* ---------------- SCROLL REVEAL ---------------- */
  const io = new IntersectionObserver(es => es.forEach(x => { if (x.isIntersecting) { x.target.classList.add("show"); io.unobserve(x.target); } }), { threshold: .12 });
  document.querySelectorAll(".reveal").forEach(r => io.observe(r));

  /* ---------------- AUTO IMAGES (library + crops) ---------------- */
  function enhance() {
    document.querySelectorAll("#libGrid .card:not(.done)").forEach(c => {
      c.classList.add("done");
      const t = c.querySelector("h3")?.textContent || "";
      const n = Object.keys(DIS).find(k => t.includes(k));
      if (n) { const d = el("div", "lib-img"); d.style.backgroundImage = `url(${IMG + DIS[n]})`; c.prepend(d); }
    });
    document.querySelectorAll(".crop-row .ic:not(.done)").forEach(ic => {
      ic.classList.add("done");
      const name = ic.parentElement.querySelector("b")?.textContent.trim();
      if (!CROP[name]) return;
      const emoji = ic.textContent, img = new Image();
      img.src = IMG + CROP[name]; img.alt = name;
      img.onerror = () => { ic.textContent = emoji; };
      ic.textContent = ""; ic.appendChild(img);
    });
    document.querySelectorAll(".winner:not(.done)").forEach(w => {
      w.classList.add("done");
      const name = w.querySelector("h3")?.textContent.trim(), big = w.querySelector(".big");
      if (!CROP[name] || !big) return;
      const emoji = big.textContent, img = new Image();
      img.src = IMG + CROP[name]; img.className = "winner-img";
      img.onerror = () => { big.textContent = emoji; };
      big.textContent = ""; big.appendChild(img);
    });
  }
  new MutationObserver(enhance).observe(document.body, { childList: true, subtree: true });
})();
