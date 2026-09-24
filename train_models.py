import os, json
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, r2_score, mean_absolute_error

os.makedirs("models", exist_ok=True)
rng = np.random.RandomState(42)
metrics = {}

def line(): print("=" * 58)
line(); print("   AgriMind AI v2.0 - Training 4 Machine Learning Models"); line()

# ---------------------------------------------------------------
# 1) DISEASE CLASSIFIER  (8 colour + texture features)
# ---------------------------------------------------------------
DISEASES = ["Healthy", "Leaf_Blight", "Leaf_Rust", "Powdery_Mildew", "Leaf_Spot"]
params = {
    "Healthy":        [(0.30,.04),(0.55,.08),(0.50,.08),(0.62,.08),(0.02,.01),(0.03,.01),(0.15,.03),(0.20,.05)],
    "Leaf_Blight":    [(0.20,.05),(0.45,.10),(0.38,.10),(0.33,.10),(0.26,.08),(0.08,.03),(0.22,.05),(0.38,.08)],
    "Leaf_Rust":      [(0.09,.03),(0.62,.08),(0.55,.08),(0.28,.08),(0.22,.06),(0.05,.02),(0.18,.04),(0.32,.06)],
    "Powdery_Mildew": [(0.24,.05),(0.18,.06),(0.72,.08),(0.38,.08),(0.02,.01),(0.05,.02),(0.10,.03),(0.14,.04)],
    "Leaf_Spot":      [(0.27,.05),(0.50,.08),(0.40,.08),(0.44,.08),(0.14,.05),(0.12,.04),(0.25,.05),(0.42,.07)],
}
X = np.clip(np.vstack([np.column_stack([rng.normal(mu, sd, 500) for mu, sd in params[d]]) for d in DISEASES]), 0, 1)
y = np.repeat(np.arange(len(DISEASES)), 500)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
model = RandomForestClassifier(n_estimators=250, random_state=42, n_jobs=-1).fit(Xtr, ytr)
acc = accuracy_score(yte, model.predict(Xte))
joblib.dump(model, "models/disease_model.pkl")
metrics["disease"] = {"name": "Disease Classifier", "algo": "Random Forest (250 trees)", "metric": "Accuracy",
                      "value": f"{acc*100:.2f}%", "samples": int(len(y)), "features": 8,
                      "inputs": "Hue, Saturation, Brightness, Green/Brown/Yellow ratio, Texture, Edge density"}
print(f"[1] Disease Classifier   -> Accuracy : {acc*100:.2f}%")

# ---------------------------------------------------------------
# 2) YIELD PREDICTOR  (tonnes, realistic per-crop potential)
# ---------------------------------------------------------------
n = 4000
ph = rng.uniform(4.5, 8.5, n); N = rng.uniform(20, 300, n); P = rng.uniform(5, 150, n); K = rng.uniform(40, 400, n)
rain = rng.uniform(200, 2200, n); temp = rng.uniform(10, 42, n); hum = rng.uniform(20, 95, n)
crop = rng.randint(0, 5, n); dprob = rng.uniform(0, 1, n); area = rng.uniform(0.5, 10, n)
ph_f = np.where((ph >= 6.0) & (ph <= 7.5), 1.0, 0.78)
suit = (np.clip(N/200, 0, 1.2)*0.35 + np.clip(P/80, 0, 1.2)*0.20 + np.clip(K/250, 0, 1.2)*0.15
        + np.clip(rain/1000, 0, 1.1)*0.20 + np.clip(1-np.abs(temp-25)/25, 0, 1)*0.20
        + np.clip(1-np.abs(hum-65)/60, 0, 1)*0.10) * ph_f * (1 - 0.45*dprob)
potential = np.array([4.5, 5.0, 7.0, 3.2, 75.0])[crop]   # Wheat, Rice, Maize, Cotton, Sugarcane (t/ha)
total = np.clip(suit * potential * area * (1 + rng.normal(0, 0.05, n)), 0.05, None)
Xy = np.column_stack([ph, N, P, K, rain, temp, hum, crop, dprob, area])
Xtr, Xte, ytr, yte = train_test_split(Xy, total, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=250, random_state=42, n_jobs=-1).fit(Xtr, ytr)
r2 = r2_score(yte, model.predict(Xte))
joblib.dump(model, "models/yield_model.pkl")
metrics["yield"] = {"name": "Yield Predictor", "algo": "Random Forest Regressor (250 trees)", "metric": "R2 Score",
                    "value": f"{r2:.3f}", "samples": n, "features": 10,
                    "inputs": "pH, N, P, K, Rainfall, Temperature, Humidity, Crop, Disease probability, Area"}
print(f"[2] Yield Predictor      -> R2 Score : {r2:.3f}")

# ---------------------------------------------------------------
# 3) IRRIGATION DEMAND  (mm/day)
# ---------------------------------------------------------------
n = 3000
t = rng.uniform(12, 46, n); h = rng.uniform(15, 95, n); r7 = rng.uniform(0, 150, n)
sm = rng.uniform(5, 60, n); st = rng.randint(0, 4, n)
water = 4 + 0.18*(t-25) - 0.05*(h-60) - 0.10*r7 - 0.12*(sm-30) + np.array([-1.0, 1.0, 3.0, 0.0])[st]
water = np.clip(water + rng.normal(0, 0.4, n), 0, None)
Xi = np.column_stack([t, h, r7, sm, st])
Xtr, Xte, ytr, yte = train_test_split(Xi, water, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1).fit(Xtr, ytr)
pred = model.predict(Xte); r2 = r2_score(yte, pred); mae = mean_absolute_error(yte, pred)
joblib.dump(model, "models/irrigation_model.pkl")
metrics["irrigation"] = {"name": "Irrigation Demand Model", "algo": "Random Forest Regressor (200 trees)",
                         "metric": "R2 / MAE", "value": f"{r2:.3f} / {mae:.2f} mm", "samples": n, "features": 5,
                         "inputs": "Temperature, Humidity, 7-day rain, Soil moisture, Crop stage"}
print(f"[3] Irrigation Model     -> R2 : {r2:.3f} | MAE : {mae:.2f} mm")

# ---------------------------------------------------------------
# 4) CROP RECOMMENDATION  (best crop for soil + climate)
# ---------------------------------------------------------------
profiles = [  # N, P, K, temp, humidity, pH, rainfall(mm)
    [(120,25),(60,15),(50,15),(20,3),(55,10),(6.8,.4),(450,100)],    # Wheat
    [(90,20),(45,10),(45,10),(27,2.5),(82,6),(6.2,.4),(1500,250)],   # Rice
    [(110,20),(55,12),(40,10),(24,3),(65,8),(6.3,.4),(800,150)],     # Maize
    [(130,20),(45,10),(25,8),(30,3),(50,10),(7.2,.4),(650,120)],     # Cotton
    [(150,25),(70,15),(120,25),(28,3),(75,8),(6.8,.5),(1800,250)],   # Sugarcane
]
Xc = np.clip(np.vstack([np.column_stack([rng.normal(mu, sd, 700) for mu, sd in p]) for p in profiles]), 0, None)
yc = np.repeat(np.arange(5), 700)
Xtr, Xte, ytr, yte = train_test_split(Xc, yc, test_size=0.2, random_state=42, stratify=yc)
model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1).fit(Xtr, ytr)
acc = accuracy_score(yte, model.predict(Xte))
joblib.dump(model, "models/crop_model.pkl")
metrics["crop"] = {"name": "Crop Recommender", "algo": "Random Forest (200 trees)", "metric": "Accuracy",
                   "value": f"{acc*100:.2f}%", "samples": int(len(yc)), "features": 7,
                   "inputs": "N, P, K, Temperature, Humidity, pH, Rainfall"}
print(f"[4] Crop Recommender     -> Accuracy : {acc*100:.2f}%")

with open("models/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)
line(); print("   All 4 models + metrics.json saved in /models  [OK]"); line()
