(() => {
  const NAME = "Muhammad Hammad Ashraf", INIT = "MH";
  const say = (m, t) => (typeof toast === "function" ? toast(m, t) : alert(m));
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  let INFO = { exists: false }, img = new Image(), pendingFile = null, drag = null;

  document.head.insertAdjacentHTML("beforeend", `<style>
  .dev-tools{position:absolute;left:50%;bottom:-62px;transform:translateX(-50%);display:flex;gap:6px;z-index:5;white-space:nowrap}
  .dev-tools button{border:1px solid rgba(255,255,255,.25);background:rgba(3,20,11,.78);backdrop-filter:blur(8px);color:#fff;padding:7px 12px;border-radius:9px;font-size:.75rem;font-weight:600;cursor:pointer;font-family:inherit;transition:.2s}
  .dev-tools button:hover{border-color:#34d399;color:#34d399}
  .dev-tools button.del:hover{border-color:#ef4444;color:#ef4444}
  .pe-box{max-width:460px}
  .pe-body{padding:22px 24px 26px;text-align:center}
  .pe-canvas{width:260px;height:260px;border-radius:50%;border:4px solid var(--accent);box-shadow:0 12px 30px rgba(16,185,129,.3);cursor:grab;touch-action:none;background:var(--card2)}
  .pe-canvas:active{cursor:grabbing}
  .pe-hint{font-size:.78rem;color:var(--muted);margin:8px 0 12px}
  .pe-sl{text-align:left;margin:10px 0}
  .pe-sl label{display:flex;justify-content:space-between}
  .pe-sl input[type=range]{padding:0;border:none;background:none;accent-color:#10b981;box-shadow:none}
  .pe-btns{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px}
  .pe-btns button{font-family:inherit;cursor:pointer}
  @media(max-width:1000px){.dev-hero.has-tools .dev-photo{margin-bottom:60px}}
  </style>`);

  /* ---------- editor modal ---------- */
  const modal = document.createElement("div");
  modal.className = "modal";
  modal.innerHTML = `<div class="modal-box pe-box">
    <div class="modal-head"><div><h2>🖼️ Adjust Developer Photo</h2><p>Drag the photo or use the sliders</p></div>
      <button class="modal-close" data-pe-close>✕</button></div>
    <div class="pe-body">
      <canvas class="pe-canvas" width="520" height="520"></canvas>
      <p class="pe-hint">🖱️ Drag to move · sliders to zoom &amp; position</p>
      <div class="pe-sl"><label>🔍 Zoom <b id="peZv"></b></label><input type="range" id="peZ" min="0" max="85" step="1"></div>
      <div class="pe-sl"><label>↔️ Left / Right</label><input type="range" id="peX" min="0" max="100" step="0.1"></div>
      <div class="pe-sl"><label>↕️ Up / Down</label><input type="range" id="peY" min="0" max="100" step="0.1"></div>
      <div class="pe-btns"><button type="button" class="btn-outline" data-pe-close>Cancel</button>
        <button type="button" class="btn" id="peSave" style="margin:0">💾 Save Photo</button></div>
    </div></div>`;
  document.body.appendChild(modal);
  const cv = modal.querySelector("canvas"), ctx = cv.getContext("2d");
  const Z = modal.querySelector("#peZ"), X = modal.querySelector("#peX"), Y = modal.querySelector("#peY");
  const zoomVal = () => (100 - +Z.value) / 100;

  function draw() {
    if (!img.naturalWidth) return;
    const w = img.naturalWidth, h = img.naturalHeight, side = zoomVal() * Math.min(w, h);
    const left = clamp(+X.value / 100 * w - side / 2, 0, w - side);
    const top = clamp(+Y.value / 100 * h - side / 2, 0, h - side);
    ctx.clearRect(0, 0, cv.width, cv.height);
    ctx.drawImage(img, left, top, side, side, 0, 0, cv.width, cv.height);
    modal.querySelector("#peZv").textContent = (1 / zoomVal()).toFixed(1) + "×";
  }
  [Z, X, Y].forEach(s => s.addEventListener("input", draw));

  cv.addEventListener("pointerdown", e => { drag = { sx: e.clientX, sy: e.clientY, x: +X.value, y: +Y.value }; cv.setPointerCapture(e.pointerId); });
  cv.addEventListener("pointermove", e => {
    if (!drag || !img.naturalWidth) return;
    const w = img.naturalWidth, h = img.naturalHeight, k = zoomVal() * Math.min(w, h) / cv.clientWidth;
    X.value = clamp(drag.x - (e.clientX - drag.sx) * k / w * 100, 0, 100);
    Y.value = clamp(drag.y - (e.clientY - drag.sy) * k / h * 100, 0, 100);
    draw();
  });
  ["pointerup", "pointercancel"].forEach(ev => cv.addEventListener(ev, () => drag = null));

  function openEditor(src, file) {
    pendingFile = file || null;
    Z.value = 100 - Math.round((file ? 0.8 : INFO.zoom) * 100);
    X.value = (file ? 0.5 : INFO.x) * 100;
    Y.value = (file ? 0.4 : INFO.y) * 100;
    img = new Image();
    img.onload = draw;
    img.onerror = () => say("Photo load nahi hui", "err");
    img.src = src;
    modal.classList.add("show");
  }
  function close() {
    modal.classList.remove("show");
    if (pendingFile && img.src.startsWith("blob:")) URL.revokeObjectURL(img.src);
    pendingFile = null;
  }

  modal.querySelector("#peSave").onclick = async e => {
    const btn = e.currentTarget;
    btn.disabled = true; btn.textContent = "⏳ Saving...";
    const x = +X.value / 100, y = +Y.value / 100, zoom = zoomVal();
    try {
      let r;
      if (pendingFile) {
        const fd = new FormData();
        fd.append("photo", pendingFile); fd.append("x", x); fd.append("y", y); fd.append("zoom", zoom);
        r = await fetch("/api/dev-photo", { method: "POST", body: fd });
      } else {
        r = await fetch("/api/dev-photo/crop", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ x, y, zoom }) });
      }
      const d = await r.json();
      if (!d.ok) throw new Error(d.error);
      INFO = d; render(); close(); say("Photo saved ✅");
    } catch (err) {
      say(err.message || "Save failed", "err");
    } finally {
      btn.disabled = false; btn.textContent = "💾 Save Photo";
    }
  };

  /* ---------- hidden file input ---------- */
  const input = document.createElement("input");
  input.type = "file"; input.accept = "image/jpeg,image/png,image/webp,image/bmp"; input.hidden = true;
  document.body.appendChild(input);
  input.onchange = () => {
    const f = input.files[0];
    input.value = "";
    if (!f) return;
    if (f.size > 10 * 1024 * 1024) return say("Photo 10MB se bari hai", "err");
    openEditor(URL.createObjectURL(f), f);
  };

  /* ---------- render photos everywhere ---------- */
  function initials() { const d = document.createElement("div"); d.className = "dev-pic dev-initials"; d.textContent = INIT; return d; }
  function node() {
    if (!INFO.exists) return initials();
    const i = new Image();
    i.className = "dev-pic"; i.alt = NAME;
    i.src = "/static/img/developer.jpg?v=" + INFO.v;
    i.onerror = () => i.replaceWith(initials());
    return i;
  }
  function tools() {
    const box = document.querySelector(".dev-photo"), hero = document.querySelector(".dev-hero");
    if (!box) return;
    box.querySelector(".dev-tools")?.remove();
    hero?.classList.toggle("has-tools", !!INFO.can_edit);
    if (!INFO.can_edit) return;
    const t = document.createElement("div");
    t.className = "dev-tools";
    t.innerHTML = `<button data-pe="change">📷 ${INFO.exists ? "Change" : "Upload"}</button>` +
      (INFO.has_original ? `<button data-pe="adjust">✏️ Adjust</button>` : "") +
      (INFO.exists ? `<button data-pe="delete" class="del">🗑️ Delete</button>` : "");
    box.appendChild(t);
  }
  function render() {
    document.querySelectorAll(".dev-pic").forEach(el => el.replaceWith(node()));
    tools();
  }

  document.addEventListener("click", async e => {
    const b = e.target.closest("[data-pe]");
    if (b) {
      const a = b.dataset.pe;
      if (a === "change") input.click();
      else if (a === "adjust") openEditor("/static/img/developer_original.jpg?v=" + INFO.v);
      else if (a === "delete") {
        if (!confirm("Developer photo delete karni hai?")) return;
        const d = await (await fetch("/api/dev-photo", { method: "DELETE" })).json();
        if (!d.ok) return say(d.error, "err");
        INFO = d; render(); say("Photo deleted 🗑️", "warn");
      }
      return;
    }
    if (e.target === modal || e.target.closest("[data-pe-close]")) close();
  });
  document.addEventListener("keydown", e => { if (e.key === "Escape") close(); });

  fetch("/api/dev-photo").then(r => r.json()).then(d => { if (d.ok) { INFO = d; render(); } }).catch(() => {});
})();
