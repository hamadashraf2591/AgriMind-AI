import os, json, secrets, datetime
from collections import Counter
from flask import request, session, redirect, jsonify, render_template, abort
from werkzeug.security import generate_password_hash, check_password_hash

OPEN = {"static", "login_page", "auth_login", "auth_signup", "auth_demo", "logout"}

def init_auth(app, db):
    base = app.root_path
    upload = os.path.join(base, "uploads")

    # ---------- secret key (sessions survive restarts) ----------
    key_file = os.path.join(base, "secret.key")
    if not os.path.exists(key_file):
        with open(key_file, "w") as f:
            f.write(secrets.token_hex(32))
    with open(key_file) as f:
        app.secret_key = f.read().strip()
    app.permanent_session_lifetime = datetime.timedelta(days=30)

    # ---------- database ----------
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
            name TEXT, city TEXT, crop INTEGER DEFAULT 0, area REAL DEFAULT 2, phone TEXT, created TEXT)""")
        cols = [r[1] for r in c.execute("PRAGMA table_info(analyses)").fetchall()]
        if "user_id" not in cols:
            c.execute("ALTER TABLE analyses ADD COLUMN user_id INTEGER")

    def uid():
        return session.get("uid")

    def start(user_id, remember=True):
        session.clear()
        session["uid"] = user_id
        session.permanent = bool(remember)

    def create_user(c, username, password, name, city="", crop=0, area=2.0, phone="", claim=True):
        real_users = c.execute("SELECT COUNT(*) FROM users WHERE username != 'demo'").fetchone()[0]
        cur = c.execute("""INSERT INTO users(username,password,name,city,crop,area,phone,created)
                           VALUES(?,?,?,?,?,?,?,?)""",
                        (username, generate_password_hash(password, method="pbkdf2:sha256"), name, city,
                         crop, area, phone, datetime.datetime.now().strftime("%d %b %Y")))
        if claim and real_users == 0:   # first real account gets all old analyses
            c.execute("UPDATE analyses SET user_id=? WHERE user_id IS NULL", (cur.lastrowid,))
        return cur.lastrowid

    # ---------- route protection ----------
    @app.before_request
    def guard():
        if request.endpoint is None or request.endpoint in OPEN:
            return None
        if not uid():
            if request.path.startswith("/api/"):
                return jsonify(ok=False, error="Session expired. Please login again."), 401
            return redirect("/login")
        return None

    # ---------- auth routes ----------
    @app.route("/login", endpoint="login_page")
    def login_page():
        if uid():
            return redirect("/")
        return render_template("login.html")

    @app.route("/auth/login", methods=["POST"], endpoint="auth_login")
    def auth_login():
        d = request.get_json(silent=True) or {}
        u = (d.get("username") or "").strip().lower()
        p = d.get("password") or ""
        with db() as c:
            row = c.execute("SELECT id, password, name FROM users WHERE username=?", (u,)).fetchone()
        if not row or not check_password_hash(row["password"], p):
            return jsonify(ok=False, error="Invalid username or password"), 400
        start(row["id"], d.get("remember", True))
        return jsonify(ok=True, name=row["name"])

    @app.route("/auth/signup", methods=["POST"], endpoint="auth_signup")
    def auth_signup():
        d = request.get_json(silent=True) or {}
        u = (d.get("username") or "").strip().lower()
        p = d.get("password") or ""
        name = (d.get("name") or "").strip()[:40]
        if not name:
            return jsonify(ok=False, error="Please enter your full name"), 400
        if len(u) < 3 or " " in u:
            return jsonify(ok=False, error="Username must be 3+ characters without spaces"), 400
        if u == "demo":
            return jsonify(ok=False, error="This username is reserved"), 400
        if len(p) < 6:
            return jsonify(ok=False, error="Password must be at least 6 characters"), 400
        try:
            crop = min(max(int(d.get("crop") or 0), 0), 4)
            area = max(float(d.get("area") or 2), 0.01)
        except ValueError:
            return jsonify(ok=False, error="Farm area must be a number"), 400
        with db() as c:
            if c.execute("SELECT 1 FROM users WHERE username=?", (u,)).fetchone():
                return jsonify(ok=False, error="Username already taken"), 400
            new_id = create_user(c, u, p, name, (d.get("city") or "").strip()[:40], crop, area,
                                 (d.get("phone") or "").strip()[:20])
        start(new_id, True)
        return jsonify(ok=True, name=name)

    @app.route("/auth/demo", methods=["POST"], endpoint="auth_demo")
    def auth_demo():
        with db() as c:
            row = c.execute("SELECT id FROM users WHERE username='demo'").fetchone()
            user_id = row["id"] if row else create_user(c, "demo", secrets.token_hex(8), "Demo Farmer",
                                                        "Lahore", 0, 5.0, "", claim=False)
        start(user_id, False)
        return jsonify(ok=True, name="Demo Farmer")

    @app.route("/logout", endpoint="logout")
    def logout():
        session.clear()
        return redirect("/login")

    # ---------- profile API ----------
    @app.route("/api/me")
    def api_me():
        with db() as c:
            u = c.execute("SELECT id,username,name,city,crop,area,phone,created FROM users WHERE id=?", (uid(),)).fetchone()
            s = c.execute("SELECT COUNT(*) n, AVG(health) h, SUM(revenue) r FROM analyses WHERE user_id=?", (uid(),)).fetchone()
        if not u:
            session.clear()
            return jsonify(ok=False, error="User not found"), 401
        return jsonify(ok=True, user=dict(u),
                       stats={"total": s["n"], "avg_health": round(s["h"] or 0, 1), "total_revenue": int(s["r"] or 0)})

    @app.route("/api/profile", methods=["POST"])
    def api_profile():
        d = request.get_json(silent=True) or {}
        name = (d.get("name") or "").strip()[:40]
        if not name:
            return jsonify(ok=False, error="Name is required"), 400
        try:
            crop = min(max(int(d.get("crop") or 0), 0), 4)
            area = max(float(d.get("area") or 2), 0.01)
        except ValueError:
            return jsonify(ok=False, error="Farm area must be a number"), 400
        new_p = d.get("new_password") or ""
        with db() as c:
            if new_p:
                row = c.execute("SELECT password FROM users WHERE id=?", (uid(),)).fetchone()
                if not check_password_hash(row["password"], d.get("current_password") or ""):
                    return jsonify(ok=False, error="Current password is incorrect"), 400
                if len(new_p) < 6:
                    return jsonify(ok=False, error="New password must be at least 6 characters"), 400
                c.execute("UPDATE users SET password=? WHERE id=?",
                          (generate_password_hash(new_p, method="pbkdf2:sha256"), uid()))
            c.execute("UPDATE users SET name=?, city=?, crop=?, area=?, phone=? WHERE id=?",
                      (name, (d.get("city") or "").strip()[:40], crop, area, (d.get("phone") or "").strip()[:20], uid()))
        return jsonify(ok=True)

    # ---------- per-user data (overrides original routes) ----------
    def history():
        with db() as c:
            rows = c.execute("""SELECT id,created,farmer,crop,disease,health,yield_t,revenue,image
                                FROM analyses WHERE user_id=? ORDER BY id DESC""", (uid(),)).fetchall()
        return jsonify([dict(r) for r in rows])

    def delete(rid):
        with db() as c:
            row = c.execute("SELECT image, heatmap FROM analyses WHERE id=? AND user_id=?", (rid, uid())).fetchone()
            if not row:
                return jsonify(ok=False, error="Not found"), 404
            for fn in (row["image"], row["heatmap"]):
                try:
                    os.remove(os.path.join(upload, fn))
                except OSError:
                    pass
            c.execute("DELETE FROM analyses WHERE id=?", (rid,))
        return jsonify(ok=True)

    def stats():
        with db() as c:
            rows = c.execute("""SELECT created, disease, health, yield_t, revenue FROM analyses
                                WHERE user_id=? ORDER BY id""", (uid(),)).fetchall()
        if not rows:
            return jsonify(total=0, avg_health=0, total_yield=0, total_revenue=0, top_disease="-", dist={}, trend=[])
        dist = Counter(r["disease"] for r in rows)
        sick = [kv for kv in dist.most_common() if kv[0] != "Healthy"]
        return jsonify(total=len(rows), avg_health=round(sum(r["health"] for r in rows) / len(rows), 1),
                       total_yield=round(sum(r["yield_t"] for r in rows), 2),
                       total_revenue=int(sum(r["revenue"] for r in rows)),
                       top_disease=sick[0][0] if sick else "None", dist=dict(dist),
                       trend=[{"date": r["created"][5:], "health": r["health"]} for r in rows[-12:]])

    def report(rid):
        with db() as c:
            row = c.execute("SELECT data FROM analyses WHERE id=? AND user_id=?", (rid, uid())).fetchone()
        if not row:
            abort(404)
        return render_template("report.html", d=json.loads(row["data"]))

    for ep, fn in {"api_history": history, "api_delete": delete, "api_stats": stats, "report": report}.items():
        if ep in app.view_functions:
            app.view_functions[ep] = fn

    # ---------- tag new analyses with the logged-in user ----------
    @app.after_request
    def tag_analysis(resp):
        if request.endpoint == "api_analyze" and resp.status_code == 200 and uid():
            try:
                d = resp.get_json(silent=True) or {}
                if d.get("ok") and d.get("id"):
                    with db() as c:
                        c.execute("UPDATE analyses SET user_id=? WHERE id=?", (uid(), d["id"]))
            except Exception:
                pass
        return resp

    print("Auth system ready (login required).")
