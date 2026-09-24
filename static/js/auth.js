(() => {
  // Redirect to login automatically if session expires
  const nativeFetch = window.fetch.bind(window);
  window.fetch = async (...args) => {
    const r = await nativeFetch(...args);
    if (r.status === 401) location.href = "/login";
    return r;
  };

  const CROPS = ["🌾 Wheat", "🍚 Rice", "🌽 Maize", "☁️ Cotton", "🎋 Sugarcane"];
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const initials = n => (n || "U").trim().split(/\s+/).map(w => w[0]).join("").slice(0, 2).toUpperCase();
  const say = (m, t) => (typeof toast === "function" ? toast(m, t) : alert(m));
  let ME = null;

  const menu = document.createElement("div");
  menu.className = "user-menu";
  document.querySelector(".top-right").appendChild(menu);

  const modal = document.createElement("div");
  modal.className = "modal";
  document.body.appendChild(modal);

  async function loadMe() {
    const r = await fetch("/api/me");
    if (!r.ok) return;
    ME = await r.json();
    if (!ME.ok) return;
    renderMenu(); prefill(); greet();
  }

  function renderMenu() {
    const u = ME.user;
    menu.innerHTML = `
      <button class="user-btn"><span class="avatar">${esc(initials(u.name))}</span>
        <div><b>${esc(u.name)}</b><small>@${esc(u.username)}</small></div></button>
      <div class="dropdown">
        <div class="dh"><b>${esc(u.name)}</b><br><small>📍 ${esc(u.city || "No city set")} · ${ME.stats.total} analyses</small></div>
        <a data-act="profile">👤 My Profile</a>
        <a data-act="history">🗂️ My History</a>
        <a data-act="new">🔍 New Analysis</a>
        <a class="out" href="/logout">🚪 Logout</a>
      </div>`;
  }

  function prefill() {
    const f = document.getElementById("analyzeForm");
    if (!f) return;
    const u = ME.user;
    const field = n => f.querySelector(`[name=${n}]`);
    if (field("farmer") && !field("farmer").value) field("farmer").value = u.name;
    if (field("city") && !field("city").value && u.city) field("city").value = u.city;
    if (field("area") && u.area) field("area").value = u.area;
    if (field("crop_type")) field("crop_type").value = u.crop ?? 0;
  }

  function greet() {
    const tag = document.querySelector(".hero-tag");
    if (tag) tag.textContent = `👋 Welcome back, ${ME.user.name.split(" ")[0]} · AI Smart Farming`;
  }

  function openProfile() {
    const u = ME.user, s = ME.stats;
    modal.innerHTML = `<div class="modal-box">
      <div class="modal-head"><span class="avatar">${esc(initials(u.name))}</span>
        <div><h2>${esc(u.name)}</h2><p>@${esc(u.username)} · Member since ${esc(u.created)}</p></div>
        <button class="modal-close" data-close>✕</button></div>
      <div class="modal-body">
        <div class="p-stats">
          <div><b>${s.total}</b><small>Analyses</small></div>
          <div><b>${s.avg_health}%</b><small>Avg Crop Health</small></div>
          <div><b>Rs ${Number(s.total_revenue).toLocaleString("en-US")}</b><small>Est. Revenue</small></div>
        </div>
        <form id="profileForm">
          <h4>👤 Personal & Farm Details</h4>
          <div class="fields">
            <div class="f"><label>Full Name</label><input name="name" value="${esc(u.name)}" required></div>
            <div class="f"><label>Phone</label><input name="phone" value="${esc(u.phone)}" placeholder="03xx-xxxxxxx"></div>
            <div class="f"><label>City</label><input name="city" value="${esc(u.city)}" placeholder="e.g. Lahore"></div>
            <div class="f"><label>Farm Area (hectare)</label><input type="number" step="0.1" name="area" value="${esc(u.area)}"></div>
            <div class="f full"><label>Main Crop</label><select name="crop">
              ${CROPS.map((c, i) => `<option value="${i}" ${i == u.crop ? "selected" : ""}>${c}</option>`).join("")}</select></div>
          </div>
          <h4>🔒 Change Password (optional)</h4>
          <div class="fields">
            <div class="f"><label>Current Password</label><input type="password" name="current_password"></div>
            <div class="f"><label>New Password</label><input type="password" name="new_password" placeholder="min 6 characters"></div>
          </div>
          <button class="btn">💾 Save Changes</button>
        </form>
      </div></div>`;
    modal.classList.add("show");
    modal.querySelector("#profileForm").onsubmit = async e => {
      e.preventDefault();
      const body = JSON.stringify(Object.fromEntries(new FormData(e.target)));
      const r = await fetch("/api/profile", { method: "POST", headers: { "Content-Type": "application/json" }, body });
      const d = await r.json();
      if (!d.ok) return say(d.error, "err");
      modal.classList.remove("show");
      say("Profile updated ✅");
      loadMe();
    };
  }

  document.addEventListener("click", e => {
    const drop = menu.querySelector(".dropdown");
    if (e.target.closest(".user-btn")) { drop?.classList.toggle("open"); return; }
    const act = e.target.closest("[data-act]");
    if (act) {
      drop?.classList.remove("open");
      const a = act.dataset.act;
      if (a === "profile") openProfile();
      else if (a === "history") go("history");
      else if (a === "new") {
        go("dashboard");
        setTimeout(() => document.getElementById("startAnalysis")?.scrollIntoView({ behavior: "smooth" }), 350);
      }
      return;
    }
    if (e.target === modal || e.target.closest("[data-close]")) modal.classList.remove("show");
    if (!e.target.closest(".user-menu")) drop?.classList.remove("open");
  });
  document.addEventListener("keydown", e => { if (e.key === "Escape") modal.classList.remove("show"); });

  loadMe();
})();
