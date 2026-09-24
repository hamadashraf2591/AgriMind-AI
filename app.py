import os, json, math, uuid, sqlite3, datetime, urllib.request, urllib.parse
from collections import Counter
import numpy as np
import joblib
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_from_directory, abort

BASE = os.path.dirname(os.path.abspath(__file__))
UPLOAD = os.path.join(BASE, "uploads")
DB = os.path.join(BASE, "agrimind.db")
os.makedirs(UPLOAD, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

print("Loading AI models...")
M = {k: joblib.load(os.path.join(BASE, "models", f"{k}_model.pkl")) for k in ("disease", "yield", "irrigation", "crop")}
print("All models loaded.")

DISEASES = ["Healthy", "Leaf Blight", "Leaf Rust", "Powdery Mildew", "Leaf Spot"]
CROPS = ["Wheat", "Rice", "Maize", "Cotton", "Sugarcane"]
STAGES = ["Seedling", "Vegetative", "Flowering", "Maturity"]
CROP_ICON = {"Wheat": "🌾", "Rice": "🍚", "Maize": "🌽", "Cotton": "☁️", "Sugarcane": "🎋"}
PRICES = {"Wheat": 100000, "Rice": 140000, "Maize": 65000, "Cotton": 210000, "Sugarcane": 10000}  # PKR / tonne
FERT_TARGET = {"Wheat": (150, 80, 60), "Rice": (120, 60, 60), "Maize": (180, 90, 70),
               "Cotton": (160, 70, 80), "Sugarcane": (250, 100, 150)}
BAG_PRICE = {"Urea": 4600, "DAP": 12500, "MOP": 11000}  # PKR per 50kg bag

DISEASE_INFO = {
    "Healthy": {"icon": "✅", "severity": "None", "color": "#22c55e",
        "cause": "No pathogen detected on the leaf surface.",
        "symptoms": "Uniform green colour, smooth texture, no lesions or spots.",
        "treatment": "No chemical treatment required.",
        "organic": "Monthly preventive neem oil spray (5 ml/L) and compost application.",
        "prevention": "Crop rotation, balanced fertilization and weekly field scouting."},
    "Leaf Blight": {"icon": "🔥", "severity": "High", "color": "#ef4444",
        "cause": "Fungal/bacterial pathogens (Helminthosporium, Xanthomonas) favoured by warm, humid weather.",
        "symptoms": "Large brown/tan dry lesions starting from leaf tips and margins, leaves look burnt.",
        "treatment": "Mancozeb 75WP @ 2 g/L or Copper Oxychloride @ 3 g/L, repeat after 10 days.",
        "organic": "Neem oil 5 ml/L spray; remove and burn infected leaves.",
        "prevention": "Resistant varieties, certified seed, avoid dense sowing and waterlogging."},
    "Leaf Rust": {"icon": "🟠", "severity": "High", "color": "#f97316",
        "cause": "Puccinia fungus spread by wind-borne spores during cool, moist nights.",
        "symptoms": "Orange-brown powdery pustules scattered on the leaf surface.",
        "treatment": "Propiconazole 25EC @ 1 ml/L or Tebuconazole @ 1 ml/L.",
        "organic": "Sulphur dusting or garlic-extract spray every 7 days.",
        "prevention": "Timely sowing, rust-resistant varieties, remove volunteer plants."},
    "Powdery Mildew": {"icon": "⚪", "severity": "Medium", "color": "#a3a3a3",
        "cause": "Erysiphe fungus, most active during dry days with humid nights.",
        "symptoms": "White-grey powdery coating on the upper leaf surface.",
        "treatment": "Wettable Sulphur 80WP @ 2.5 g/L or Hexaconazole @ 1 ml/L.",
        "organic": "Baking soda 5 g/L + few drops of liquid soap, or milk spray (1:9).",
        "prevention": "Good air circulation, avoid excess nitrogen, ensure sunlight exposure."},
    "Leaf Spot": {"icon": "🟤", "severity": "Medium", "color": "#a855f7",
        "cause": "Cercospora / Septoria fungi splashing from infected soil and crop debris.",
        "symptoms": "Small circular brown spots with yellow halos on leaves.",
        "treatment": "Chlorothalonil @ 2 g/L or Carbendazim @ 1 g/L.",
        "organic": "Trichoderma-based bio-fungicide; remove lower infected leaves.",
        "prevention": "Avoid overhead irrigation, destroy crop residue, rotate crops."},
}

# ------------------------------- DATABASE -------------------------------
def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

with db() as c:
    c.execute("""CREATE TABLE IF NOT EXISTS analyses(
        id INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT, farmer TEXT, crop TEXT, disease TEXT,
        health REAL, disease_prob REAL, water_mm REAL, yield_t REAL, revenue REAL,
        image TEXT, heatmap TEXT, data TEXT)""")

# ---------------------------- IMAGE ANALYSIS ----------------------------
def analyze_image(path, heat_name):
    img = Image.open(path).convert("RGB")
    small = img.resize((128, 128))
    arr = np.asarray(small).astype(np.float32) / 255.0
    hsv = np.asarray(small.convert("HSV")).astype(np.float32) / 255.0
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    green = np.mean((g > r) & (g > b) & (g > 0.25))
    brown = np.mean((r > 0.25) & (r < 0.65) & (g < 0.5) & (b < 0.4) & (r >= g))
    yellow = np.mean((r > 0.5) & (g > 0.5) & (b < 0.45))
    gray = arr.mean(axis=2)
    edge = min((np.abs(np.diff(gray, axis=1)).mean() + np.abs(np.diff(gray, axis=0)).mean()) * 10, 1.0)
    feats = np.array([[h.mean(), s.mean(), v.mean(), green, brown, yellow, v.std(), edge]], dtype=np.float32)

    # Disease heatmap: highlight infected (brown/yellow) regions in red
    w = 420
    hh = max(1, int(img.height * w / img.width))
    big = np.asarray(img.resize((w, hh))).astype(np.float32)
    R, G, B = big[..., 0] / 255, big[..., 1] / 255, big[..., 2] / 255
    m_dis = ((R > 0.25) & (R < 0.65) & (G < 0.5) & (B < 0.4) & (R >= G)) | ((R > 0.5) & (G > 0.5) & (B < 0.45))
    m_green = (G > R) & (G > B) & (G > 0.25)
    plant = m_dis | m_green
    affected = float(m_dis.sum() / max(plant.sum(), 1) * 100)
    over = big.copy()
    over[~plant] *= 0.35
    over[m_dis] = over[m_dis] * 0.35 + np.array([255, 30, 30]) * 0.65
    Image.fromarray(np.clip(over, 0, 255).astype(np.uint8)).save(os.path.join(UPLOAD, heat_name))
    return feats, float(green), round(affected, 1)

# ------------------------------- WEATHER --------------------------------
def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "AgriMindAI/2.0"})
    with urllib.request.urlopen(req, timeout=7) as r:
        return json.loads(r.read().decode())

def simulate_weather(temp=28.0, hum=60.0, label="Simulated forecast"):
    rng = np.random.default_rng(int(datetime.date.today().strftime("%Y%m%d")))
    today = datetime.date.today()
    days = []
    for i in range(7):
        rain = float(max(0.0, rng.normal(1.5, 5)))
        days.append({"date": str(today + datetime.timedelta(days=i)),
                     "tmax": round(float(temp + 3 + rng.normal(0, 1.5)), 1),
                     "tmin": round(float(temp - 5 + rng.normal(0, 1.5)), 1),
                     "rain": round(rain, 1), "hum": round(float(hum + rng.normal(0, 5))),
                     "code": 61 if rain > 5 else (2 if rain > 0.5 else 0)})
    return {"live": False, "city": label,
            "current": {"temp": temp, "humidity": hum, "wind": round(float(rng.uniform(5, 15)), 1), "precip": 0, "code": 0},
            "days": days}

def get_weather(city):
    try:
        geo = fetch_json("https://geocoding-api.open-meteo.com/v1/search?" +
                         urllib.parse.urlencode({"name": city, "count": 1}))
        if not geo.get("results"):
            raise ValueError("city not found")
        loc = geo["results"][0]
        f = fetch_json("https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode({
            "latitude": loc["latitude"], "longitude": loc["longitude"],
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean,weather_code",
            "timezone": "auto", "forecast_days": 7}))
        cur, d = f["current"], f["daily"]
        hums = d.get("relative_humidity_2m_mean") or [None] * len(d["time"])
        days = [{"date": d["time"][i], "tmax": d["temperature_2m_max"][i], "tmin": d["temperature_2m_min"][i],
                 "rain": d["precipitation_sum"][i] or 0, "hum": hums[i] if hums[i] is not None else cur["relative_humidity_2m"],
                 "code": d["weather_code"][i]} for i in range(len(d["time"]))]
        return {"live": True, "city": f"{loc['name']}, {loc.get('country', '')}",
                "current": {"temp": cur["temperature_2m"], "humidity": cur["relative_humidity_2m"],
                            "wind": cur["wind_speed_10m"], "precip": cur["precipitation"], "code": cur["weather_code"]},
                "days": days}
    except Exception as e:
        print("Weather fallback:", e)
        return simulate_weather(label=f"{city} (offline data)")

# ------------------------------ AI HELPERS ------------------------------
def irrigation_plan(days, humidity, moisture, rain7, stage):
    plan, sm, r7 = [], moisture, rain7
    for d in days:
        t = (d["tmax"] + d["tmin"]) / 2
        h = d.get("hum") or humidity
        r7 = r7 * 6 / 7 + d["rain"]
        w = max(float(M["irrigation"].predict([[t, h, r7, sm, stage]])[0]), 0.0)
        action = "Irrigate" if (w >= 4 and d["rain"] < 5) else ("Light" if (w >= 2.5 and d["rain"] < 5) else "Skip")
        plan.append({"date": d["date"], "tmax": round(d["tmax"], 1), "tmin": round(d["tmin"], 1),
                     "rain": round(d["rain"], 1), "code": d["code"], "water_mm": round(w, 1), "action": action})
        sm = min(60, max(5, sm + d["rain"] * 0.4 - w * 0.8 + (12 if action == "Irrigate" else 5 if action == "Light" else 0)))
    return plan

def fertilizer_plan(crop, n, p, k, area):
    tn, tp, tk = FERT_TARGET[crop]
    dn, dp, dk = max(tn - n, 0), max(tp - p, 0), max(tk - k, 0)
    dap = dp / 0.46
    urea = max(dn - dap * 0.18, 0) / 0.46
    mop = dk / 0.60
    items = []
    for key, label, kg_ha, nut in [("Urea", "Urea (46% N)", urea, "Nitrogen"),
                                   ("DAP", "DAP (18-46-0)", dap, "Phosphorus"),
                                   ("MOP", "MOP (60% K2O)", mop, "Potassium")]:
        total = kg_ha * area
        bags = math.ceil(total / 50) if total > 0 else 0
        items.append({"name": label, "nutrient": nut, "kg_ha": round(kg_ha, 1), "total_kg": round(total, 1),
                      "bags": bags, "cost": bags * BAG_PRICE[key]})
    return {"crop": crop, "area": area, "target": {"N": tn, "P": tp, "K": tk},
            "deficit": {"N": round(dn, 1), "P": round(dp, 1), "K": round(dk, 1)},
            "items": items, "total_cost": sum(i["cost"] for i in items)}

def recommend_crops(n, p, k, t, h, ph, rain):
    pr = M["crop"].predict_proba([[n, p, k, t, h, ph, rain]])[0]
    return [{"crop": CROPS[i], "icon": CROP_ICON[CROPS[i]], "score": round(float(pr[i]) * 100, 1)}
            for i in np.argsort(pr)[::-1][:3]]

def build_recommendations(disease, water, ph, n, moisture, rain7, temp, humidity, affected, plan):
    recs = []
    info = DISEASE_INFO[disease]
    if disease == "Healthy":
        recs.append({"icon": "✅", "level": "ok", "text": "Crop looks healthy. Continue the current care routine and scout weekly."})
    else:
        recs.append({"icon": "💊", "level": "danger", "text": f"{disease} detected: {info['treatment']}"})
        recs.append({"icon": "🌿", "level": "info", "text": f"Organic option: {info['organic']}"})
    if affected > 25:
        recs.append({"icon": "🚨", "level": "danger", "text": f"{affected}% leaf area affected. Act within 48 hours to prevent spread."})
    if water >= 7:
        recs.append({"icon": "💧", "level": "warn", "text": "High water demand. Irrigate today, early morning or evening."})
    elif water >= 3:
        recs.append({"icon": "💧", "level": "info", "text": "Moderate water demand. Irrigate within 1-2 days."})
    else:
        recs.append({"icon": "💧", "level": "ok", "text": "Low water demand. Skip irrigation, soil moisture is sufficient."})
    rainy = [p for p in plan if p["rain"] >= 5]
    if rainy:
        recs.append({"icon": "🌧️", "level": "info", "text": f"Rain expected on {rainy[0]['date']}. Avoid pesticide spraying 24h before rain."})
    if temp > 38:
        recs.append({"icon": "🌡️", "level": "warn", "text": "Heat stress risk. Use light, frequent irrigation and mulching."})
    if humidity > 80 and disease != "Healthy":
        recs.append({"icon": "🍄", "level": "warn", "text": "High humidity favours fungal spread. Improve airflow between rows."})
    if ph < 6:
        recs.append({"icon": "⚗️", "level": "warn", "text": "Soil is acidic. Apply agricultural lime (1-2 t/ha)."})
    elif ph > 7.5:
        recs.append({"icon": "⚗️", "level": "warn", "text": "Soil is alkaline. Apply gypsum or organic matter."})
    if n < 100:
        recs.append({"icon": "🧪", "level": "warn", "text": "Nitrogen is low. See the fertilizer plan below."})
    if moisture < 15:
        recs.append({"icon": "🏜️", "level": "danger", "text": "Soil moisture critically low. Prioritize irrigation."})
    return recs

def health_label(h):
    return "Excellent" if h >= 80 else "Good" if h >= 60 else "Fair" if h >= 40 else "Poor"

# -------------------------------- ROUTES --------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/uploads/<path:name>")
def uploaded(name):
    return send_from_directory(UPLOAD, name)

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    try:
        f = request.files.get("image")
        if not f or not f.filename:
            return jsonify(ok=False, error="Please upload a leaf image."), 400
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp", ".bmp"):
            return jsonify(ok=False, error="Unsupported file type. Use JPG/PNG/WEBP."), 400
        uid = uuid.uuid4().hex
        img_name, heat_name = uid + ext, uid + "_heat.png"
        f.save(os.path.join(UPLOAD, img_name))

        feats, green, affected = analyze_image(os.path.join(UPLOAD, img_name), heat_name)
        proba = M["disease"].predict_proba(feats)[0]
        di = int(np.argmax(proba))
        disease = DISEASES[di]
        healthy_p = float(proba[0])

        g = request.form.get
        num = lambda k, d: float(g(k) or d)
        farmer = (g("farmer") or "Farmer").strip()[:40]
        city = (g("city") or "").strip()
        ph, n, p, k = num("soil_ph", 6.5), num("soil_n", 150), num("soil_p", 60), num("soil_k", 200)
        rainfall, temp, hum = num("rainfall", 800), num("temperature", 28), num("humidity", 60)
        area, moisture, rain7 = max(num("area", 2), 0.01), num("soil_moisture", 30), num("rain7", 20)
        crop_idx, stage_idx = int(g("crop_type") or 0), int(g("crop_stage") or 1)
        crop = CROPS[crop_idx]
        price = num("price", PRICES[crop])

        health = round(100 * (0.6 * healthy_p + 0.2 * min(green * 1.6, 1.0) + 0.2 * (1 - affected / 100)), 1)
        dprob = round((1 - healthy_p) * 100, 1) if disease == "Healthy" else round(float(proba[di]) * 100, 1)

        yld = max(float(M["yield"].predict([[ph, n, p, k, rainfall, temp, hum, crop_idx, 1 - healthy_p, area]])[0]), 0.05)
        water = max(float(M["irrigation"].predict([[temp, hum, rain7, moisture, stage_idx]])[0]), 0.0)
        wlabel = "Low" if water < 3 else ("Moderate" if water < 7 else "High")

        weather = get_weather(city) if city else simulate_weather(temp, hum)
        plan = irrigation_plan(weather["days"], hum, moisture, rain7, stage_idx)

        result = {
            "ok": True, "farmer": farmer, "crop": crop, "crop_icon": CROP_ICON[crop], "stage": STAGES[stage_idx],
            "image_url": f"/uploads/{img_name}", "heatmap_url": f"/uploads/{heat_name}",
            "crop_health": health, "health_label": health_label(health),
            "disease": disease, "disease_probability": dprob, "disease_info": DISEASE_INFO[disease],
            "disease_all": {DISEASES[i]: round(float(v) * 100, 1) for i, v in enumerate(proba)},
            "affected_area": affected,
            "water_mm": round(water, 1), "water_label": wlabel, "water_litres": int(water * area * 10000),
            "expected_yield": round(yld, 2), "yield_per_hectare": round(yld / area, 2),
            "price": int(price), "revenue": int(round(yld * price)),
            "weather_live": weather["live"], "weather_city": weather["city"], "irrigation_plan": plan,
            "fertilizer": fertilizer_plan(crop, n, p, k, area),
            "best_crops": recommend_crops(n, p, k, temp, hum, ph, rainfall),
            "inputs": {"Soil pH": ph, "Nitrogen": n, "Phosphorus": p, "Potassium": k, "Soil moisture %": moisture,
                       "Seasonal rain mm": rainfall, "Rain 7d mm": rain7, "Temperature C": temp,
                       "Humidity %": hum, "Area ha": area},
            "recommendations": build_recommendations(disease, water, ph, n, moisture, rain7, temp, hum, affected, plan),
        }
        created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        result["created"] = created
        with db() as c:
            cur = c.execute("""INSERT INTO analyses(created,farmer,crop,disease,health,disease_prob,water_mm,
                               yield_t,revenue,image,heatmap,data) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (created, farmer, crop, disease, health, dprob, result["water_mm"],
                             result["expected_yield"], result["revenue"], img_name, heat_name, ""))
            result["id"] = cur.lastrowid
            c.execute("UPDATE analyses SET data=? WHERE id=?", (json.dumps(result), result["id"]))
        return jsonify(result)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 400

@app.route("/api/weather")
def api_weather():
    city = request.args.get("city", "").strip()
    return jsonify(get_weather(city) if city else simulate_weather())

@app.route("/api/recommend-crop", methods=["POST"])
def api_recommend():
    d = request.get_json(force=True)
    try:
        v = [float(d[k]) for k in ("n", "p", "k", "temperature", "humidity", "ph", "rainfall")]
    except Exception:
        return jsonify(ok=False, error="Please fill all fields with numbers."), 400
    pr = M["crop"].predict_proba([v])[0]
    ranked = [{"crop": CROPS[i], "icon": CROP_ICON[CROPS[i]], "score": round(float(pr[i]) * 100, 1),
               "price": PRICES[CROPS[i]]} for i in np.argsort(pr)[::-1]]
    return jsonify(ok=True, ranked=ranked)

@app.route("/api/fertilizer", methods=["POST"])
def api_fertilizer():
    d = request.get_json(force=True)
    try:
        crop = CROPS[int(d["crop_type"])]
        plan = fertilizer_plan(crop, float(d["n"]), float(d["p"]), float(d["k"]), max(float(d["area"]), 0.01))
    except Exception:
        return jsonify(ok=False, error="Please fill all fields correctly."), 400
    return jsonify(ok=True, plan=plan)

@app.route("/api/history")
def api_history():
    with db() as c:
        rows = c.execute("SELECT id,created,farmer,crop,disease,health,yield_t,revenue,image FROM analyses ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/history/<int:rid>", methods=["DELETE"])
def api_delete(rid):
    with db() as c:
        row = c.execute("SELECT image, heatmap FROM analyses WHERE id=?", (rid,)).fetchone()
        if row:
            for fn in (row["image"], row["heatmap"]):
                try:
                    os.remove(os.path.join(UPLOAD, fn))
                except OSError:
                    pass
            c.execute("DELETE FROM analyses WHERE id=?", (rid,))
    return jsonify(ok=True)

@app.route("/api/stats")
def api_stats():
    with db() as c:
        rows = c.execute("SELECT created, disease, health, yield_t, revenue FROM analyses ORDER BY id").fetchall()
    if not rows:
        return jsonify(total=0, avg_health=0, total_yield=0, total_revenue=0, top_disease="-", dist={}, trend=[])
    dist = Counter(r["disease"] for r in rows)
    sick = [kv for kv in dist.most_common() if kv[0] != "Healthy"]
    return jsonify(total=len(rows), avg_health=round(sum(r["health"] for r in rows) / len(rows), 1),
                   total_yield=round(sum(r["yield_t"] for r in rows), 2),
                   total_revenue=int(sum(r["revenue"] for r in rows)),
                   top_disease=sick[0][0] if sick else "None", dist=dict(dist),
                   trend=[{"date": r["created"][5:], "health": r["health"]} for r in rows[-12:]])

@app.route("/api/diseases")
def api_diseases():
    return jsonify(DISEASE_INFO)

@app.route("/api/models")
def api_models():
    try:
        with open(os.path.join(BASE, "models", "metrics.json")) as fh:
            return jsonify(json.load(fh))
    except Exception:
        return jsonify({})

@app.route("/report/<int:rid>")
def report(rid):
    with db() as c:
        row = c.execute("SELECT data FROM analyses WHERE id=?", (rid,)).fetchone()
    if not row:
        abort(404)
    return render_template("report.html", d=json.loads(row["data"]))

from auth import init_auth
init_auth(app, db)

from dev_admin import init_dev_admin
init_dev_admin(app, db)

if __name__ == "__main__":
    app.run(debug=True)


