# ✈️ SkyFare — AI Airfare Price Prediction System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5%2B-F7931E.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/Tests-8%20Passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

**SkyFare** is an end-to-end Machine Learning web application and RESTful API that predicts domestic airline ticket prices in India. Powered by a **Random Forest Regression** ensemble (100 decision trees) and served via **FastAPI**, SkyFare calculates not only the expected flight fare but also an empirical **price variance range** (10th to 90th percentile bounds) based on individual decision tree predictions.

---

## 🌟 Key Features

- **Ensemble Price Estimation**: Delivers expected flight fares alongside realistic confidence bounds (`₹ Min – ₹ Max`) derived from 100 decision tree estimators.
- **Smart Route Auto-Inference**: Automatically generates and formats valid multi-leg IATA transit sequences (`DEL → BOM → COK`) based on cities and stops, with normalization for typed arrows (`->` to ` → `).
- **Auto-Calculated Flight Duration**: Automatically calculates journey minutes from departure and arrival times, with automatic overnight flight (`+1 Day`) detection.
- **Unified Monorepo Architecture**: Serves the modern dark-mode responsive Web UI directly from the FastAPI root (`/`), with full backward-compatibility for standalone static hosting (GitHub Pages, Vercel, Render).
- **Zero-CORS-Friction API**: Preconfigured CORS policies ensure seamless communication across all local development ports (`5500`, `3000`, `5173`, `8000`) and remote cloud hosts.
- **Quick-Test Presets**: One-click flight presets (Delhi–Cochin, Bangalore–Delhi, Mumbai–Hyderabad, Kolkata–Bangalore) for instant testing.
- **Production-Ready**: Includes Docker containerization, comprehensive `pytest` test suite, and standalone model retraining script.

---

## 🏛️ System Architecture

```
                          ┌───────────────────────────┐
                          │    Browser / Client UI    │
                          │   (HTML5 / CSS3 / ES6)    │
                          └─────────────┬─────────────┘
                                        │ HTTP POST /predict
                                        ▼
                          ┌───────────────────────────┐
                          │    FastAPI Application    │
                          │   (Pydantic Validation)   │
                          └─────────────┬─────────────┘
                                        │
                         Route Normalization & Metadata
                                        ▼
                          ┌───────────────────────────┐
                          │     ColumnTransformer     │
                          │ OneHotEncoder + Passthrough│
                          └─────────────┬─────────────┘
                                        │ 169-Dim Feature Vector
                                        ▼
                          ┌───────────────────────────┐
                          │   Random Forest Regressor │
                          │     (100 Decision Trees)  │
                          └─────────────┬─────────────┘
                                        │
                    Mean Prediction + 10th-90th Percentile Range
                                        ▼
                          ┌───────────────────────────┐
                          │     Prediction Output     │
                          │ Fare, Range, Conf, Summary│
                          └───────────────────────────┘
```

---

## 📁 Repository Structure

```
AIRFARE-PREDICTION/
├── frontend/                     # Interactive Web Application
│   ├── index.html                # Responsive UI layout & flight form
│   ├── style.css                 # Modern styling & animations
│   └── script.js                 # Dynamic routing, duration & API client
├── main.py                       # FastAPI application & REST endpoints
├── metadata.py                   # Route normalizer & categorical mappings
├── categories.json               # Trained feature categories snapshot
├── flight_model.pkl              # Serialized Random Forest Regressor
├── preprocessor.pkl              # Serialized ColumnTransformer
├── train_pipeline.py             # Reproducible training & evaluation script
├── test_app.py                   # Automated pytest test suite
├── requirements.txt              # Project dependencies
├── Dockerfile                    # Containerization specification
└── README.md                     # Documentation
```

---

## 🚀 Quick Start (Local Setup)

### 1. Prerequisites
- Python 3.10+ installed
- Git

### 2. Clone and Setup Environment
```bash
git clone https://github.com/karthikdatta83-cmyk/AIRFARE-PREDICTION.git
cd AIRFARE-PREDICTION

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Launch the Server
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- **Web Application**: Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
- **Interactive Swagger API Docs**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
- **Alternative ReDoc Docs**: Open [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).

---

## 📡 API Reference

### `POST /predict`
Estimates flight fare, price variance range, and confidence score.

#### Request Example:
```json
{
  "Airline": "IndiGo",
  "Source": "Delhi",
  "Destination": "Cochin",
  "Route": "DEL → BOM → COK",
  "Additional_Info": "No info",
  "Duration": 150,
  "Total_Stops": 1,
  "Journey_Day": 25,
  "Journey_Month": 11,
  "Dep_Hour": 10,
  "Dep_Minute": 30,
  "Arrival_Hour": 13,
  "Arrival_Minute": 0
}
```

#### Response Example:
```json
{
  "predicted_fare": 4119.93,
  "formatted_fare": "₹4,120",
  "currency": "INR",
  "fare_range": {
    "min": 3858.0,
    "max": 4840.7,
    "formatted_min": "₹3,858",
    "formatted_max": "₹4,841",
    "formatted_range": "₹3,858 – ₹4,841"
  },
  "confidence": "High",
  "flight_summary": {
    "airline": "IndiGo",
    "source": "Delhi",
    "destination": "Cochin",
    "route": "DEL → BOM → COK",
    "stops": 1,
    "duration": "2h 30m"
  }
}
```

### Other Endpoints:
- `GET /health`: Model status and health verification.
- `GET /api/metadata`: Returns available airlines, sources, destinations, and airport mappings.
- `GET /api/routes?source={city}&destination={city}&stops={int}`: Returns valid transit routes.
- `GET /about`: Architecture and framework overview.

---

## 🧪 Automated Testing

Run the automated test suite with pytest:
```bash
pytest test_app.py -v
```

The test suite validates:
- System health and metadata integrity.
- Direct and connecting flight predictions.
- Automatic route normalization (converting typed `->` into Unicode ` → `).
- Automatic route fallback synthesis.
- Pydantic schema validation errors.

---

## 📊 Machine Learning Methodology

### Feature Importance Breakdown:
| Feature | Importance | Description |
| :--- | :---: | :--- |
| `Duration` | **43.3%** | Total flight time in minutes |
| `Journey_Day` | **9.5%** | Calendar day of departure |
| `Additional_Info` | **7.6%** | Ancillary service tier (e.g. no meals included) |
| `Airline_Jet Airways Business` | **7.0%** | Premium luxury travel class |
| `Airline_Jet Airways` | **5.8%** | Historical full-service carrier premium |
| `Journey_Month` | **4.7%** | Seasonal travel trends |
| `Total_Stops` | **2.3%** | Non-stop vs. multi-hop connection penalty |
| Timing Features | **~1.1% – 1.6% each** | Time-of-day pricing windows |

### Retraining Pipeline:
To train or re-evaluate the model:
```bash
python train_pipeline.py --help
# Run with demonstration synthesized data:
python train_pipeline.py
# Retrain from custom dataset and save artifacts:
python train_pipeline.py --data /path/to/Data_Train.xlsx --save
```

---

## 🐳 Docker Deployment

Build and run with Docker in a single command:
```bash
docker build -t skyfare-app .
docker run -p 8000:8000 skyfare-app
```
Visit [http://localhost:8000](http://localhost:8000) to view the running containerized application.

---

## 📄 License
This project is licensed under the MIT License.
