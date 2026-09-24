(() => {
  /* ================== EDIT YOUR INFO HERE ================== */
  const DEV = {
    name: "Muhammad Hammad Ashraf",
    short: "Hammad",
    initials: "MH",
    phone: "0329-4502591",
    phoneIntl: "923294502591",
    email: "hamadashraf2591@gmail.com",
    linkedin: "https://www.linkedin.com/in/m-hamad-ashraf-4b15a53a9",
    github: "https://github.com/hamadashraf2591",
    location: "Pakistan",
    photo: "/static/img/developer.jpg",
    roles: ["AI & Machine Learning Developer", "Full-Stack Web Developer", "Computer Vision Enthusiast", "Creator of AgriMind AI"],
    skills: [["Python", 92], ["Machine Learning (scikit-learn)", 88], ["Flask & REST APIs", 90],
             ["HTML / CSS / JavaScript", 86], ["Computer Vision (Pillow / NumPy)", 80], ["SQL & SQLite", 82]]
  };
  /* ========================================================= */

  const ok = u => /^https?:\/\//i.test(u);
  const say = (m, t) => (typeof toast === "function" ? toast(m, t) : alert(m));
  const lnk = u => ok(u) ? `href="${u}" target="_blank" rel="noopener"` : `href="#" data-missing="1"`;
  const SVG = {
    li: '<svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>',
    gh: '<svg viewBox="0 0 16 16"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>'
  };
  const pic = () => `<img class="dev-pic" data-dev src="${DEV.photo}" alt="${DEV.name}">`;
  const wa = (t = "") => `https://wa.me/${DEV.phoneIntl}${t ? "?text=" + encodeURIComponent(t) : ""}`;

  function fixPhotos() {
    document.querySelectorAll("img[data-dev]").forEach(img => {
      const swap = () => { const d = document.createElement("div"); d.className = "dev-pic dev-initials"; d.textContent = DEV.initials; img.replaceWith(d); };
      if (img.complete && img.naturalWidth === 0) swap(); else img.addEventListener("error", swap, { once: true });
    });
  }

  /* ---------------- register page ---------------- */
  if (typeof PAGES !== "undefined") PAGES.developer = ["About Developer", "Meet the mind behind AgriMind AI"];
  const nav = document.querySelector(".sidebar nav");
  const item = document.createElement("a");
  item.className = "nav"; item.dataset.page = "developer";
  item.innerHTML = "<i>👨‍💻</i><span>About Developer</span>";
  item.addEventListener("click", () => go("developer"));
  nav.appendChild(item);

  const page = document.createElement("section");
  page.className = "page"; page.id = "page-developer";
  page.innerHTML = `
  <div class="dev-hero">
    <div class="dev-photo"><div class="ring"></div>${pic()}<span class="dev-badge"><i></i>Available for work</span></div>
    <div class="dev-text">
      <div class="dev-hi">👋 Hello, I'm</div>
      <h1>Muhammad <span>Hammad Ashraf</span></h1>
      <div class="dev-role"><span class="typed" id="typed"></span></div>
      <p>I build intelligent, real-world software that combines <b>Machine Learning</b>, <b>Computer Vision</b> and
         <b>modern web development</b>. AgriMind AI is my smart-farming platform that helps farmers detect crop
         diseases, plan irrigation and predict yield &amp; profit using AI.</p>
      <div class="dev-btns">
        <a class="dev-btn mail" href="mailto:${DEV.email}">✉️ Hire / Email Me</a>
        <a class="dev-btn li" ${lnk(DEV.linkedin)}>${SVG.li} LinkedIn</a>
        <a class="dev-btn gh" ${lnk(DEV.github)}>${SVG.gh} GitHub</a>
        <a class="dev-btn wa" href="${wa("Assalam o Alaikum Hammad! I saw AgriMind AI.")}" target="_blank" rel="noopener">💬 WhatsApp</a>
      </div>
    </div>
  </div>

  <div class="dev-stats" id="devStats">
    <div class="card dev-stat"><div class="ic">🧠</div><b data-to="4">0</b><small>ML Models Trained</small></div>
    <div class="card dev-stat"><div class="ic">🔌</div><b data-to="15" data-suf="+">0</b><small>API Endpoints</small></div>
    <div class="card dev-stat"><div class="ic">🧩</div><b data-to="8">0</b><small>Platform Modules</small></div>
    <div class="card dev-stat"><div class="ic">💻</div><b data-to="2000" data-suf="+">0</b><small>Lines of Code</small></div>
  </div>

  <div class="grid-2">
    <div class="card dev-about">
      <h2>🙋 About Me</h2>
      <p>I am <b>${DEV.name}</b>, a passionate developer from <b>${DEV.location}</b> focused on solving real problems
         with technology. I enjoy turning data into decisions: from training machine learning models to building
         complete, beautiful full-stack applications that people can actually use.</p>
      <div class="dev-info">
        <div><span>👤 Name</span><b>${DEV.name}</b></div>
        <div><span>📍 Location</span><b>${DEV.location}</b></div>
        <div><span>📞 Phone</span><b>${DEV.phone}</b></div>
        <div><span>✉️ Email</span><b>${DEV.email}</b></div>
        <div><span>🎯 Focus</span><b>AI · ML · Full-Stack</b></div>
      </div>
    </div>
    <div class="card skills" id="devSkills">
      <h2>🛠️ Skills</h2>
      ${DEV.skills.map(([s, v]) => `<div class="skill"><div class="top"><span>${s}</span><b>${v}%</b></div>
        <div class="sbar"><div style="--w:${v}%"></div></div></div>`).join("")}
    </div>
  </div>

  <div class="sec-head"><span>Get In Touch</span><h2>Contact Information</h2><p>Feel free to reach out for projects, collaboration or opportunities.</p></div>
  <div class="c-grid">
    <div class="card c-card" style="--c:#10b981"><div class="c-ic">📞</div><h4>Phone</h4><p>${DEV.phone}</p>
      <div class="c-act"><a href="tel:+${DEV.phoneIntl}">Call</a><button data-copy="${DEV.phone}">Copy</button></div></div>
    <div class="card c-card" style="--c:#25d366"><div class="c-ic">💬</div><h4>WhatsApp</h4><p>+92 329 4502591</p>
      <div class="c-act"><a href="${wa()}" target="_blank" rel="noopener">Chat</a><button data-copy="+${DEV.phoneIntl}">Copy</button></div></div>
    <div class="card c-card" style="--c:#ea4335"><div class="c-ic">✉️</div><h4>Gmail</h4><p>${DEV.email}</p>
      <div class="c-act"><a href="mailto:${DEV.email}">Email</a><button data-copy="${DEV.email}">Copy</button></div></div>
    <div class="card c-card" style="--c:#0a66c2"><div class="c-ic">${SVG.li}</div><h4>LinkedIn</h4><p>${ok(DEV.linkedin) ? "Let's connect" : "Link coming soon"}</p>
      <div class="c-act"><a ${lnk(DEV.linkedin)}>Open Profile</a></div></div>
    <div class="card c-card" style="--c:#6e5494"><div class="c-ic">${SVG.gh}</div><h4>GitHub</h4><p>${ok(DEV.github) ? "View my code" : "Link coming soon"}</p>
      <div class="c-act"><a ${lnk(DEV.github)}>Open Profile</a></div></div>
  </div>

  <div class="grid-2">
    <div class="card">
      <h2>🛣️ AgriMind AI: Project Journey</h2>
      <div class="tl">
        <div class="tl-item" data-ic="1"><small>Version 1.0</small><h4>Core ML Pipeline</h4><p>Disease detection, yield prediction and irrigation models served through a Flask API.</p></div>
        <div class="tl-item" data-ic="2"><small>Version 2.0 PRO</small><h4>Smart Dashboard</h4><p>Live weather API, crop advisor, fertilizer calculator, history charts and PDF reports.</p></div>
        <div class="tl-item" data-ic="3"><small>Design Upgrade</small><h4>Website Experience</h4><p>Hero section, feature cards, real photos, glassmorphism and scroll animations.</p></div>
        <div class="tl-item" data-ic="4"><small>Security</small><h4>Farmer Accounts</h4><p>Login &amp; signup, hashed passwords, private per-user history and profiles.</p></div>
        <div class="tl-item" data-ic="🚀"><small>Coming Next</small><h4>Deep Learning &amp; Urdu</h4><p>Real CNN on PlantVillage, Urdu language support and an AI farming chatbot.</p></div>
      </div>
    </div>
    <form class="card" id="devForm">
      <h2>✉️ Send Me a Message</h2>
      <div class="fields">
        <div class="f"><label>Your Name</label><input name="n" placeholder="e.g. Ali Khan" required></div>
        <div class="f"><label>Subject</label><input name="s" placeholder="Project / Collaboration" required></div>
        <div class="f full"><label>Message</label><textarea name="m" placeholder="Write your message..." required></textarea></div>
      </div>
      <div class="form-btns">
        <button class="dev-btn mail" type="submit">✉️ Send via Gmail</button>
        <button class="dev-btn wa" type="button" id="devWa">💬 Send via WhatsApp</button>
      </div>
    </form>
  </div>

  <div class="card"><h2>⚙️ Technologies Used in AgriMind AI</h2>
    <div class="stack"><span>Python</span><span>Flask</span><span>scikit-learn</span><span>Random Forest</span><span>NumPy</span>
    <span>Pillow (Computer Vision)</span><span>SQLite</span><span>Werkzeug Security</span><span>REST APIs</span><span>Open-Meteo API</span>
    <span>Chart.js</span><span>HTML5</span><span>CSS3</span><span>JavaScript (ES6)</span><span>PowerShell</span></div></div>

  <div class="card dev-quote">
    <h3>"Technology is most powerful when it reaches the people who feed the world."</h3>
    <p>— ${DEV.name}</p>
  </div>`;
  const main = document.querySelector(".main");
  main.insertBefore(page, document.querySelector(".site-footer"));

  /* ---------------- "Meet the developer" strip on dashboard ---------------- */
  const meet = document.createElement("div");
  meet.className = "card meet reveal show";
  meet.innerHTML = `<div class="mp">${pic()}</div>
    <div><h3>Designed &amp; Developed by ${DEV.name}</h3><p>AI & Full-Stack Developer · ${DEV.phone} · ${DEV.email}</p></div>
    <button class="dev-btn mail" data-go="developer">👨‍💻 Meet the Developer</button>`;
  document.getElementById("page-dashboard").appendChild(meet);

  /* ---------------- footer + sidebar credits ---------------- */
  const cols = document.querySelectorAll(".site-footer .ft-grid > div");
  if (cols.length) cols[cols.length - 1].innerHTML = `<h4>Developer</h4>
    <p>👨‍💻 ${DEV.name}<br>📞 ${DEV.phone}<br>✉️ ${DEV.email}</p>
    <div class="socials"><a ${lnk(DEV.linkedin)} title="LinkedIn"><span>${SVG.li.replace("<svg", '<svg width="16" height="16" fill="#fff"')}</span></a>
    <a ${lnk(DEV.github)} title="GitHub"><span>${SVG.gh.replace("<svg", '<svg width="16" height="16" fill="#fff"')}</span></a>
    <a href="${wa()}" target="_blank" rel="noopener" title="WhatsApp"><span>💬</span></a>
    <a href="mailto:${DEV.email}" title="Email"><span>✉️</span></a></div>`;
  const fb = document.querySelectorAll(".site-footer .ft-bottom span");
  if (fb[1]) fb[1].innerHTML = `Developed with 💚 by <a data-go="developer" style="display:inline;color:#34d399;cursor:pointer;font-weight:600">${DEV.name}</a>`;
  const sf = document.querySelector(".sidebar .side-foot");
  if (sf) sf.innerHTML = `4 ML Models · Live Weather<br>Developed by <a data-go="developer">${DEV.name}</a>`;

  fixPhotos();

  /* ---------------- typing animation ---------------- */
  const typed = document.getElementById("typed");
  let r = 0, c = 0, del = false;
  (function type() {
    const word = DEV.roles[r];
    typed.textContent = word.slice(0, c);
    if (!del && c < word.length) c++;
    else if (del && c > 0) c--;
    else if (!del) { del = true; return setTimeout(type, 1600); }
    else { del = false; r = (r + 1) % DEV.roles.length; }
    setTimeout(type, del ? 40 : 80);
  })();

  /* ---------------- counters + skill bars ---------------- */
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    io.unobserve(e.target);
    if (e.target.id === "devSkills") return e.target.classList.add("show");
    e.target.querySelectorAll("[data-to]").forEach(b => {
      const end = +b.dataset.to, suf = b.dataset.suf || "", t0 = performance.now();
      (function step(t) {
        const p = Math.min((t - t0) / 1400, 1);
        b.textContent = Math.round(end * (1 - Math.pow(1 - p, 3))).toLocaleString("en-US") + (p === 1 ? suf : "");
        if (p < 1) requestAnimationFrame(step);
      })(t0);
    });
  }), { threshold: .3 });
  io.observe(document.getElementById("devStats"));
  io.observe(document.getElementById("devSkills"));

  /* ---------------- contact form ---------------- */
  const form = document.getElementById("devForm");
  const msg = () => { const d = Object.fromEntries(new FormData(form)); return { ...d, body: `Name: ${d.n}\n\n${d.m}` }; };
  form.addEventListener("submit", e => {
    e.preventDefault();
    const d = msg();
    location.href = `mailto:${DEV.email}?subject=${encodeURIComponent("[AgriMind AI] " + d.s)}&body=${encodeURIComponent(d.body)}`;
    say("Opening your email app ✉️");
  });
  document.getElementById("devWa").addEventListener("click", () => {
    if (!form.reportValidity()) return;
    const d = msg();
    window.open(wa(`*${d.s}*\n${d.body}`), "_blank");
  });

  /* ---------------- copy + missing links ---------------- */
  document.addEventListener("click", async e => {
    const cp = e.target.closest("[data-copy]");
    if (cp) {
      try { await navigator.clipboard.writeText(cp.dataset.copy); }
      catch { const t = document.createElement("textarea"); t.value = cp.dataset.copy; document.body.appendChild(t); t.select(); document.execCommand("copy"); t.remove(); }
      const old = cp.textContent; cp.textContent = "✔ Copied"; setTimeout(() => cp.textContent = old, 1500);
      return say("Copied: " + cp.dataset.copy);
    }
    if (e.target.closest("[data-missing]")) { e.preventDefault(); say("Ye link abhi add nahi hua (Step 4 dekho)", "warn"); }
  });
})();


