"""
==============================================================================
Airfare Price Estimation and Fare Pattern Analysis
MongoDB Python Automated Setup & Seeder Script
File: database/mongodb/setup_mongo.py
Description: Initializes the 'airfare_prediction_db' database in MongoDB,
             creates collections, builds indexes, seeds benchmark records,
             and executes validation queries.
==============================================================================
"""

import sys
from datetime import datetime, timedelta

def main():
    try:
        from pymongo import MongoClient, ASCENDING, DESCENDING
    except ImportError:
        print("\n[!] 'pymongo' library not found.")
        print("    Please install it using: pip install pymongo")
        sys.exit(1)

    # 1. Connect to MongoDB (Local or Cloud Atlas via MONGO_URI)
    import os
    try:
        import certifi
        tls_ca = certifi.where()
    except ImportError:
        tls_ca = None

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    print(f"\n[1/5] Connecting to MongoDB at {MONGO_URI.split('@')[-1] if '@' in MONGO_URI else MONGO_URI} ...")
    
    try:
        client_kwargs = {"serverSelectionTimeoutMS": 6000}
        if tls_ca and "mongodb+srv" in MONGO_URI:
            client_kwargs["tlsCAFile"] = tls_ca
        client = MongoClient(MONGO_URI, **client_kwargs)
        # Trigger connection check
        client.admin.command('ping')
        print("  ✓ Successfully connected to MongoDB server!")
    except Exception as e:
        print(f"\n[ERROR] Could not connect to MongoDB server at {MONGO_URI}")
        print("  Please make sure MongoDB is running locally:")
        print("  1. Press Win + R, type 'services.msc', and press Enter.")
        print("  2. Locate 'MongoDB Server', right-click, and select 'Start'.")
        print("  3. (Or in Admin Terminal run: 'net start MongoDB')")
        print(f"\n  Details: {e}")
        sys.exit(1)

    db = client["airfare_prediction_db"]

    # 2. Setup Collections & Indexes
    print("\n[2/5] Creating collections and building indexes ...")

    # prediction_logs
    db.prediction_logs.create_index([("session_id", ASCENDING)], name="idx_session")
    db.prediction_logs.create_index([("source_city", ASCENDING), ("destination_city", ASCENDING)], name="idx_route_pair")
    db.prediction_logs.create_index([("airline", ASCENDING)], name="idx_airline")
    db.prediction_logs.create_index([("created_at", DESCENDING)], name="idx_created")
    print("  ✓ Collection 'prediction_logs' ready with composite & search indexes.")

    # saved_comparisons
    db.saved_comparisons.create_index([("session_id", ASCENDING), ("created_at", DESCENDING)], name="idx_saved_session")
    print("  ✓ Collection 'saved_comparisons' ready with session index.")

    # model_benchmarks
    db.model_benchmarks.create_index([("model_name", ASCENDING)], unique=True, name="uniq_model_name")
    db.model_benchmarks.create_index([("r2_score", DESCENDING)], name="idx_r2")
    print("  ✓ Collection 'model_benchmarks' ready with unique model index.")

    # route_fare_statistics
    db.route_fare_statistics.create_index([("source_city", ASCENDING), ("destination_city", ASCENDING)], unique=True, name="uniq_route")
    print("  ✓ Collection 'route_fare_statistics' ready with unique route index.")

    # 3. Seed Benchmark Records
    print("\n[3/5] Seeding ML model benchmarks and training dataset patterns ...")
    
    # Model Benchmarks (Step 8 of Problem Statement)
    benchmarks = [
        {
            "model_name": "Linear Regression (Baseline)",
            "algorithm_category": "Linear",
            "r2_score": 0.6120,
            "rmse": 2740.50,
            "mae": 1980.20,
            "is_active_model": False,
            "hyperparameters": {"fit_intercept": True, "normalize": False},
            "evaluated_at": datetime.now()
        },
        {
            "model_name": "Decision Tree Regressor",
            "algorithm_category": "Tree-based",
            "r2_score": 0.7240,
            "rmse": 2190.80,
            "mae": 1450.40,
            "is_active_model": False,
            "hyperparameters": {"max_depth": 16, "min_samples_split": 10},
            "evaluated_at": datetime.now()
        },
        {
            "model_name": "Random Forest Regressor",
            "algorithm_category": "Tree Ensemble (Bagging)",
            "r2_score": 0.8842,
            "rmse": 1640.25,
            "mae": 1120.10,
            "is_active_model": True,
            "hyperparameters": {"n_estimators": 100, "max_depth": 25, "min_samples_split": 5},
            "evaluated_at": datetime.now()
        },
        {
            "model_name": "Gradient Boosting / XGBoost",
            "algorithm_category": "Tree Ensemble (Boosting)",
            "r2_score": 0.8715,
            "rmse": 1710.60,
            "mae": 1180.40,
            "is_active_model": False,
            "hyperparameters": {"n_estimators": 150, "learning_rate": 0.08, "max_depth": 6},
            "evaluated_at": datetime.now()
        }
    ]
    for b in benchmarks:
        db.model_benchmarks.update_one({"model_name": b["model_name"]}, {"$set": b}, upsert=True)
    print(f"  ✓ Upserted {len(benchmarks)} algorithm benchmarks.")

    # Route Fare Statistics (From 2019 Dataset Analysis)
    routes = [
        {"source_city": "Delhi", "destination_city": "Cochin", "average_fare": 10539.43, "median_fare": 10262.00, "min_observed_fare": 4200.00, "max_observed_fare": 54747.00, "avg_duration_minutes": 795, "popular_airline": "Jet Airways", "sample_count": 4537, "last_updated": datetime.now()},
        {"source_city": "Banglore", "destination_city": "New Delhi", "average_fare": 11919.33, "median_fare": 10844.00, "min_observed_fare": 3359.00, "max_observed_fare": 79512.00, "avg_duration_minutes": 520, "popular_airline": "Air India", "sample_count": 2200, "last_updated": datetime.now()},
        {"source_city": "Banglore", "destination_city": "Delhi", "average_fare": 5143.92, "median_fare": 4823.00, "min_observed_fare": 3359.00, "max_observed_fare": 16655.00, "avg_duration_minutes": 170, "popular_airline": "IndiGo", "sample_count": 1565, "last_updated": datetime.now()},
        {"source_city": "Kolkata", "destination_city": "Banglore", "average_fare": 9158.39, "median_fare": 8355.00, "min_observed_fare": 3480.00, "max_observed_fare": 31783.00, "avg_duration_minutes": 755, "popular_airline": "Air India", "sample_count": 2871, "last_updated": datetime.now()},
        {"source_city": "Mumbai", "destination_city": "Hyderabad", "average_fare": 5059.73, "median_fare": 4053.00, "min_observed_fare": 1965.00, "max_observed_fare": 25139.00, "avg_duration_minutes": 195, "popular_airline": "Jet Airways", "sample_count": 697, "last_updated": datetime.now()}
    ]
    for r in routes:
        db.route_fare_statistics.update_one(
            {"source_city": r["source_city"], "destination_city": r["destination_city"]},
            {"$set": r},
            upsert=True
        )
    print(f"  ✓ Upserted {len(routes)} historical sector patterns.")

    # 4. Seed Sample Prediction Logs & Bookmarks
    print("\n[4/5] Seeding rich prediction inference logs & comparisons ...")
    demo_session = "sess-demo-849201"
    
    # Clean previous demo entries
    db.prediction_logs.delete_many({})
    db.saved_comparisons.delete_many({"session_id": demo_session})

    routes_data = [
        {"source": "Delhi", "dest": "Cochin", "route": "DEL → BOM → COK", "stops": 1, "dur": 375, "base_price": 7500},
        {"source": "Delhi", "dest": "Cochin", "route": "DEL → COK", "stops": 0, "dur": 195, "base_price": 5200},
        {"source": "Delhi", "dest": "Cochin", "route": "DEL → HYD → COK", "stops": 1, "dur": 410, "base_price": 8100},
        {"source": "Banglore", "dest": "New Delhi", "route": "BLR → DEL", "stops": 0, "dur": 170, "base_price": 6800},
        {"source": "Banglore", "dest": "New Delhi", "route": "BLR → BOM → DEL", "stops": 1, "dur": 345, "base_price": 10500},
        {"source": "Banglore", "dest": "Delhi", "route": "BLR → DEL", "stops": 0, "dur": 165, "base_price": 4900},
        {"source": "Kolkata", "dest": "Banglore", "route": "CCU → DEL → BLR", "stops": 1, "dur": 510, "base_price": 8900},
        {"source": "Kolkata", "dest": "Banglore", "route": "CCU → BLR", "stops": 0, "dur": 155, "base_price": 5600},
        {"source": "Mumbai", "dest": "Hyderabad", "route": "BOM → HYD", "stops": 0, "dur": 90, "base_price": 3400},
        {"source": "Chennai", "dest": "Kolkata", "route": "MAA → CCU", "stops": 0, "dur": 145, "base_price": 4100},
        {"source": "Delhi", "dest": "Cochin", "route": "DEL → MAA → COK", "stops": 2, "dur": 620, "base_price": 12800},
        {"source": "Banglore", "dest": "New Delhi", "route": "BLR → NAG → DEL", "stops": 1, "dur": 420, "base_price": 9200}
    ]

    airlines = [
        {"name": "IndiGo", "multiplier": 0.88},
        {"name": "SpiceJet", "multiplier": 0.84},
        {"name": "Air Asia", "multiplier": 0.82},
        {"name": "Air India", "multiplier": 1.15},
        {"name": "Vistara", "multiplier": 1.25},
        {"name": "Jet Airways", "multiplier": 1.35},
        {"name": "GoAir", "multiplier": 0.85}
    ]

    sessions = [
        "sess-demo-849201", "sess-user-102941", "sess-user-381920",
        "sess-user-551029", "sess-user-781923", "sess-user-992014"
    ]

    import random
    random.seed(42)
    now = datetime.now()
    generated_logs = []

    for i in range(35):
        r_choice = random.choice(routes_data)
        a_choice = random.choice(airlines)
        sess = random.choice(sessions)
        
        noise = random.uniform(-0.08, 0.12)
        price = round(r_choice["base_price"] * a_choice["multiplier"] * (1 + noise), 2)
        p_min = round(price * 0.91, 2)
        p_max = round(price * 1.11, 2)
        
        std_dev = (p_max - p_min) / 2
        conf = "High" if std_dev < 800 else ("Moderate" if std_dev < 1800 else "Variable")
        
        d_ago = random.randint(0, 14)
        h_ago = random.randint(1, 23)
        created_dt = now - timedelta(days=d_ago, hours=h_ago)
        
        if d_ago < 3:
            adv_action = "BUY NOW"
            adv_head = "Urgent Booking Window"
        elif price < r_choice["base_price"]:
            adv_action = "BUY NOW"
            adv_head = "Below Average Sector Rate"
        elif (p_max - price) > 1500:
            adv_action = "CONSIDER SHIFTING"
            adv_head = "High Volatility Expected"
        else:
            adv_action = "FAIR PRICE"
            adv_head = "Price is Stable"
            
        m = random.choice([5, 6])
        d = random.randint(1, 28)
        
        generated_logs.append({
            "session_id": sess,
            "airline": a_choice["name"],
            "source_city": r_choice["source"],
            "destination_city": r_choice["dest"],
            "route": r_choice["route"],
            "journey_date": f"2024-0{m}-{d:02d}",
            "duration_minutes": r_choice["dur"],
            "total_stops": r_choice["stops"],
            "predicted_fare": price,
            "fare_range": {"min": p_min, "max": p_max},
            "confidence": conf,
            "advisory": {"action": adv_action, "headline": adv_head},
            "created_at": created_dt
        })

    db.prediction_logs.insert_many(generated_logs)
    print(f"  ✓ Seeded {len(generated_logs)} realistic prediction logs across 7 airlines and 12 routes.")

    sample_comparisons = [
        {
            "session_id": demo_session,
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
            "is_favorite": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "session_id": demo_session,
            "custom_label": "Full Service - Air India",
            "airline": "Air India",
            "source_city": "Delhi",
            "destination_city": "Cochin",
            "route": "DEL → HYD → COK",
            "total_stops": 1,
            "duration_minutes": 405,
            "predicted_fare": 8920.00,
            "fare_range_display": "₹8,100 – ₹9,850",
            "user_note": "Includes check-in baggage, but 1 stop layover",
            "is_favorite": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    db.saved_comparisons.insert_many(sample_comparisons)
    print("  ✓ Seeded sample logs & comparisons for session-based testing.")

    # 5. Run Verification & Aggregation
    print("\n[5/5] Running verification query on seeded data ...")
    top_models = list(db.model_benchmarks.find({}, {"_id": 0, "model_name": 1, "r2_score": 1, "rmse": 1}).sort("r2_score", DESCENDING))
    print("\n  Top Ranked ML Models in MongoDB:")
    for idx, m in enumerate(top_models, 1):
        print(f"    {idx}. {m['model_name']:<32} | R² = {m['r2_score']:.4f} | RMSE = ₹{m['rmse']:,.2f}")

    print("\n==============================================================")
    print("🎉 SUCCESS: MongoDB database 'airfare_prediction_db' is fully")
    print("   initialized and seeded on your local system!")
    print("==============================================================\n")

if __name__ == "__main__":
    main()
