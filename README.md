# 🌾 AgriMind AI: Smart Farming Intelligence Platform

> AI-powered decision support for farmers. Upload a crop leaf photo and get disease detection, a 7-day irrigation plan, yield & profit prediction and exact fertilizer advice in one place.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-REST%20API-black?logo=flask)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange?logo=scikitlearn&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite)

## ✨ Features

| Module | Description |
|---|---|
| 🦠 **Disease Detection** | Computer-vision features + Random Forest classifier (5 classes) with infected-area heatmap |
| 🛰️ **Live Weather** | Real 7-day forecast from Open-Meteo API with farming advisory |
| 💧 **Smart Irrigation** | ML-based water demand and 7-day Irrigate / Light / Skip schedule |
| 📦 **Yield & Profit** | Yield prediction (tonnes) and estimated revenue (PKR) |
| 🌱 **Crop Advisor** | Recommends the most suitable crop for soil and climate |
| 🧪 **Fertilizer Calculator** | Exact Urea, DAP and MOP bags with total cost |
| 🗂️ **History & Reports** | Saved analyses, trend charts and printable PDF reports |
| 🔐 **Farmer Accounts** | Login / signup, hashed passwords, private per-user data |
| 📚 **Disease Library** | Symptoms, causes, treatments and prevention |

## 🧠 AI Pipeline

Leaf Image → Feature Extraction → Disease Model → Weather API → Irrigation Model → Yield Model → Recommendations

| Model | Algorithm |
|---|---|
| Disease Classifier | Random Forest (250 trees) |
| Yield Predictor | Random Forest Regressor |
| Irrigation Model | Random Forest Regressor |
| Crop Recommender | Random Forest |

> ℹ️ Current models are trained on synthetic, domain-informed data for demonstration. Next step: CNN on the PlantVillage dataset.

## 🛠️ Tech Stack

**Backend:** Python, Flask, scikit-learn, NumPy, Pillow, SQLite
**Frontend:** HTML5, CSS3, JavaScript, Chart.js
**APIs:** Open-Meteo (weather + geocoding)

## 🚀 Run Locally

```
git clone https://github.com/hamadashraf2591/AgriMind-AI.git
cd AgriMind-AI
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python train_models.py
python app.py
```

Open **http://127.0.0.1:5000** and create an account (or use **Continue as Demo Farmer**).

## 👨‍💻 Developer

**Muhammad Hammad Ashraf**: AI & Full-Stack Developer

- 💼 LinkedIn: [m-hamad-ashraf](https://www.linkedin.com/in/m-hamad-ashraf-4b15a53a9)
- 🐙 GitHub: [hamadashraf2591](https://github.com/hamadashraf2591)
- ✉️ Email: hamadashraf2591@gmail.com

⭐ If you like this project, please give it a star!