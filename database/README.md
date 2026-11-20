# 🍃 MongoDB Database Architecture: Airfare Price Estimation & Pattern Analysis

This directory contains the complete **MongoDB** database setup, schemas, seeders, and analytical queries for the **Airfare Price Estimation and Fare Pattern Analysis** project.

---

## 📌 Why These Collections Exist (Without Login/Registration)

Even though this project has **no user login or registration page**, a database layer is essential to fulfill the problem statement and full-stack project requirements:

1. **Prediction Logging (`prediction_logs`)**:
   * Logs every fare estimation request made via the API or frontend form.
   * Tracks searched airlines, origin-destination sectors, duration, stop counts, predicted prices, confidence intervals, and buying advisories.
2. **Saved Flight Comparisons (`saved_comparisons`)**:
   * Allows users to bookmark flights and compare them side-by-side using an anonymous browser `session_id`.
   * Satisfies complete **CRUD** requirements (Create bookmark, Read list, Update custom notes/budget, Delete comparison).
3. **ML Model Performance Benchmarks (`model_benchmarks`)**:
   * Directly addresses **Step 8 of the Problem Statement** ("Compare regression algorithms").
   * Stores $R^2$ scores, RMSE, and MAE across Linear Regression, Decision Tree, Random Forest, and XGBoost to feed dashboard charts.
4. **Route Fare Patterns (`route_fare_statistics`)**:
   * Stores pre-computed aggregate baseline patterns (average fare, price ranges, median durations) derived from the 10,683 training flight records.

---

## 📁 Directory Structure

```
database/
├── README.md                      # MongoDB architecture and execution guide
└── mongodb/
    ├── setup_mongo.py             # 1-command Python initializer & seeder
    ├── 01_init_mongo.js           # Collections with JSON schema validation & indexes
    ├── 02_seed_data.js            # Initial dataset benchmarks and sample logs
    ├── 03_aggregation_queries.js  # Mongosh analytical pipelines matching problem statement
    └── exported_data/             # Ready-to-import JSON files for MongoDB Compass
        ├── prediction_logs.json
        ├── model_benchmarks.json
        ├── route_fare_statistics.json
        └── saved_comparisons.json
```

---

## 🍃 MongoDB Document Schemas

### 1. Collection: `prediction_logs`
```json
{
  "_id": ObjectId("..."),
  "session_id": "sess-demo-849201",
  "airline": "IndiGo",
  "source_city": "Delhi",
  "destination_city": "Cochin",
  "route": "DEL → BOM → COK",
  "journey_date": "2024-05-25",
  "duration_minutes": 375,
  "total_stops": 1,
  "predicted_fare": 6450.00,
  "fare_range": { "min": 5920.00, "max": 7150.00 },
  "confidence": "High",
  "advisory": {
    "action": "BUY NOW",
    "headline": "Urgent Booking Window"
  },
  "created_at": ISODate("2024-11-20T10:30:00Z")
}
```

### 2. Collection: `saved_comparisons`
```json
{
  "_id": ObjectId("..."),
  "session_id": "sess-demo-849201",
  "custom_label": "Budget Option - SpiceJet Non-Stop",
  "airline": "SpiceJet",
  "source_city": "Delhi",
  "destination_city": "Cochin",
  "route": "DEL → COK",
  "total_stops": 0,
  "duration_minutes": 195,
  "predicted_fare": 4890.00,
  "fare_range_display": "₹4,400 – ₹5,320",
  "user_note": "Cheapest direct flight option for May vacation",
  "is_favorite": true,
  "created_at": ISODate("2024-11-20T10:35:00Z"),
  "updated_at": ISODate("2024-11-20T10:35:00Z")
}
```

### 3. Collection: `model_benchmarks`
```json
{
  "_id": ObjectId("..."),
  "model_name": "Random Forest Regressor",
  "algorithm_category": "Tree Ensemble (Bagging)",
  "r2_score": 0.8842,
  "rmse": 1640.25,
  "mae": 1120.10,
  "is_active_model": true,
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 25,
    "min_samples_split": 5
  },
  "evaluated_at": ISODate("2024-11-20T10:00:00Z")
}
```

### 4. Collection: `route_fare_statistics`
```json
{
  "_id": ObjectId("..."),
  "source_city": "Delhi",
  "destination_city": "Cochin",
  "average_fare": 10539.43,
  "median_fare": 10262.00,
  "min_observed_fare": 4200.00,
  "max_observed_fare": 54747.00,
  "avg_duration_minutes": 795,
  "popular_airline": "Jet Airways",
  "sample_count": 4537,
  "last_updated": ISODate("2024-11-20T10:00:00Z")
}
```

---

## 🚀 How to Run & Verify

### Option 1: Automated 1-Command Setup (Python)
From the project root:
```bash
pip install pymongo
python database/mongodb/setup_mongo.py
```

### Option 2: Using MongoDB Compass (Visual UI)
1. Open **MongoDB Compass** and connect to `mongodb://localhost:27017`.
2. Select database `airfare_prediction_db`.
3. To import pre-seeded data, click **"Add Data" $\rightarrow$ "Import JSON"** and choose the files from `database/mongodb/exported_data/`.

### Option 3: Using MongoDB Shell (`mongosh`)
```bash
mongosh < database/mongodb/01_init_mongo.js
mongosh < database/mongodb/02_seed_data.js
mongosh < database/mongodb/03_aggregation_queries.js
```
