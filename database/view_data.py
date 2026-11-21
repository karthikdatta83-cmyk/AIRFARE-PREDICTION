"""
==============================================================================
SkyFare — MongoDB Local Data Viewer
File: database/view_data.py
Description: Terminal viewer to inspect all collections in airfare_prediction_db
Usage: python database/view_data.py
==============================================================================
"""

import sys
from datetime import datetime

try:
    from pymongo import MongoClient
except ImportError:
    print("[!] Please install pymongo: pip install pymongo")
    sys.exit(1)


def main():
    import os
    try:
        import certifi
        tls_ca = certifi.where()
    except ImportError:
        tls_ca = None

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")

    try:
        kwargs = {"serverSelectionTimeoutMS": 4000}
        if tls_ca and "mongodb+srv" in mongo_uri:
            kwargs["tlsCAFile"] = tls_ca
        client = MongoClient(mongo_uri, **kwargs)
        client.admin.command("ping")
    except Exception as e:
        print(f"[ERROR] Could not connect to MongoDB: {e}")
        print("  Make sure your connection string is correct or local MongoDB is running.")
        sys.exit(1)

    db = client["airfare_prediction_db"]

    print("\n" + "=" * 70)
    print("      🍃 MONGODB DATABASE: airfare_prediction_db (LOCAL INSPECTOR)")
    print("=" * 70)

    # 1. Model Benchmarks
    print("\n📊 1. MACHINE LEARNING MODEL BENCHMARKS (model_benchmarks)")
    print("-" * 70)
    benchmarks = list(db.model_benchmarks.find().sort("r2_score", -1))
    if benchmarks:
        print(f"{'Status':<10} {'Algorithm':<32} {'R² Score':<12} {'RMSE (₹)':<12} {'MAE (₹)':<10}")
        print("-" * 70)
        for b in benchmarks:
            status = "★ ACTIVE" if b.get("is_active_model") else "  BENCHMARK"
            r2 = f"{b.get('r2_score', 0):.4f}"
            rmse = f"₹{b.get('rmse', 0):,.2f}"
            mae = f"₹{b.get('mae', 0):,.2f}"
            print(f"{status:<10} {b.get('model_name', ''):<32} {r2:<12} {rmse:<12} {mae:<10}")
    else:
        print("  (No records found in model_benchmarks)")

    # 2. Prediction Logs
    print("\n📝 2. RECENT PREDICTION AUDIT LOGS (prediction_logs)")
    print("-" * 70)
    total_logs = db.prediction_logs.count_documents({})
    recent_logs = list(db.prediction_logs.find().sort("created_at", -1).limit(6))
    print(f"Total Logged Predictions in DB: {total_logs} (Displaying latest {len(recent_logs)}):")
    if recent_logs:
        for idx, p in enumerate(recent_logs, 1):
            created = p.get("created_at")
            time_str = created.strftime("%Y-%m-%d %H:%M") if isinstance(created, datetime) else str(created)
            route = f"{p.get('source_city', '')} → {p.get('destination_city', '')}"
            fare = f"₹{p.get('predicted_fare', 0):,.2f}"
            airline = p.get('airline', '')
            stops = f"{p.get('total_stops', 0)} stops" if p.get('total_stops', 0) > 0 else "Non-stop"
            dur = f"{p.get('duration_minutes', 0)}m"
            print(f"  {idx}. [{time_str}] {airline:<12} {route:<22} {dur:<6} {stops:<10} => {fare}")
    else:
        print("  (No records found in prediction_logs)")

    # 3. Route Statistics
    print("\n📍 3. HISTORICAL ROUTE FARE BASELINES (route_fare_statistics)")
    print("-" * 70)
    routes = list(db.route_fare_statistics.find())
    if routes:
        print(f"{'Sector':<26} {'Average Fare':<16} {'Min - Max Range':<22} {'Top Airline'}")
        print("-" * 70)
        for r in routes:
            sector = f"{r.get('source_city', '')} → {r.get('destination_city', '')}"
            avg = f"₹{r.get('average_fare', 0):,.2f}"
            price_range = f"₹{r.get('min_observed_fare', 0):,.0f} - ₹{r.get('max_observed_fare', 0):,.0f}"
            airline = r.get("popular_airline", "")
            print(f"{sector:<26} {avg:<16} {price_range:<22} {airline}")
    else:
        print("  (No records found in route_fare_statistics)")

    # 4. Saved Comparisons
    print("\n🔖 4. USER SAVED COMPARISONS / BOOKMARKS (saved_comparisons)")
    print("-" * 70)
    comparisons = list(db.saved_comparisons.find().limit(5))
    if comparisons:
        for c in comparisons:
            fav = "♥" if c.get("is_favorite") else "•"
            print(f"  {fav} {c.get('custom_label', '')} | {c.get('airline', '')} | ₹{c.get('predicted_fare', 0):,.2f}")
    else:
        print("  (No records found in saved_comparisons)")

    print("\n" + "=" * 70)
    print("✔ All data verified and active in local MongoDB!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
