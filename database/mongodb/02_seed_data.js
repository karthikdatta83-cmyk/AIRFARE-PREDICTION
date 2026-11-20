// ==============================================================================
// Airfare Price Estimation and Fare Pattern Analysis
// MongoDB Seed Data Script
// Target Database: airfare_prediction_db
// Description: Populates realistic benchmark data, route averages, and sample logs.
// ==============================================================================

db = db.getSiblingDB("airfare_prediction_db");

print("--- Seeding airfare_prediction_db in MongoDB ---");

// ------------------------------------------------------------------------------
// 1. Seed Model Benchmarks (Step 8 of Problem Statement)
// ------------------------------------------------------------------------------
db.model_benchmarks.deleteMany({});
db.model_benchmarks.insertMany([
  {
    model_name: "Linear Regression (Baseline)",
    algorithm_category: "Linear",
    r2_score: 0.6120,
    rmse: 2740.50,
    mae: 1980.20,
    is_active_model: false,
    hyperparameters: { fit_intercept: true, normalize: false },
    evaluated_at: new Date()
  },
  {
    model_name: "Decision Tree Regressor",
    algorithm_category: "Tree-based",
    r2_score: 0.7240,
    rmse: 2190.80,
    mae: 1450.40,
    is_active_model: false,
    hyperparameters: { max_depth: 16, min_samples_split: 10 },
    evaluated_at: new Date()
  },
  {
    model_name: "Random Forest Regressor",
    algorithm_category: "Tree Ensemble (Bagging)",
    r2_score: 0.8842,
    rmse: 1640.25,
    mae: 1120.10,
    is_active_model: true,
    hyperparameters: { n_estimators: 100, max_depth: 25, min_samples_split: 5 },
    evaluated_at: new Date()
  },
  {
    model_name: "Gradient Boosting / XGBoost",
    algorithm_category: "Tree Ensemble (Boosting)",
    r2_score: 0.8715,
    rmse: 1710.60,
    mae: 1180.40,
    is_active_model: false,
    hyperparameters: { n_estimators: 150, learning_rate: 0.08, max_depth: 6 },
    evaluated_at: new Date()
  }
]);
print("✓ Seeded model_benchmarks.");

// ------------------------------------------------------------------------------
// 2. Seed Route Fare Statistics (From 2019 Dataset Analysis)
// ------------------------------------------------------------------------------
db.route_fare_statistics.deleteMany({});
db.route_fare_statistics.insertMany([
  {
    source_city: "Delhi",
    destination_city: "Cochin",
    average_fare: 10539.43,
    median_fare: 10262.00,
    min_observed_fare: 4200.00,
    max_observed_fare: 54747.00,
    avg_duration_minutes: 795,
    popular_airline: "Jet Airways",
    sample_count: 4537,
    last_updated: new Date()
  },
  {
    source_city: "Banglore",
    destination_city: "New Delhi",
    average_fare: 11919.33,
    median_fare: 10844.00,
    min_observed_fare: 3359.00,
    max_observed_fare: 79512.00,
    avg_duration_minutes: 520,
    popular_airline: "Air India",
    sample_count: 2200,
    last_updated: new Date()
  },
  {
    source_city: "Banglore",
    destination_city: "Delhi",
    average_fare: 5143.92,
    median_fare: 4823.00,
    min_observed_fare: 3359.00,
    max_observed_fare: 16655.00,
    avg_duration_minutes: 170,
    popular_airline: "IndiGo",
    sample_count: 1565,
    last_updated: new Date()
  },
  {
    source_city: "Kolkata",
    destination_city: "Banglore",
    average_fare: 9158.39,
    median_fare: 8355.00,
    min_observed_fare: 3480.00,
    max_observed_fare: 31783.00,
    avg_duration_minutes: 755,
    popular_airline: "Air India",
    sample_count: 2871,
    last_updated: new Date()
  },
  {
    source_city: "Mumbai",
    destination_city: "Hyderabad",
    average_fare: 5059.73,
    median_fare: 4053.00,
    min_observed_fare: 1965.00,
    max_observed_fare: 25139.00,
    avg_duration_minutes: 195,
    popular_airline: "Jet Airways",
    sample_count: 697,
    last_updated: new Date()
  }
]);
print("✓ Seeded route_fare_statistics.");

// ------------------------------------------------------------------------------
// 3. Seed Prediction Logs
// ------------------------------------------------------------------------------
db.prediction_logs.deleteMany({});
db.prediction_logs.insertMany([
  {
    session_id: "sess-demo-849201",
    airline: "IndiGo",
    source_city: "Delhi",
    destination_city: "Cochin",
    route: "DEL → BOM → COK",
    journey_date: "2024-05-25",
    duration_minutes: 375,
    total_stops: 1,
    predicted_fare: 6450.00,
    fare_range: { min: 5920.00, max: 7150.00 },
    confidence: "High",
    advisory: { action: "BUY NOW", headline: "Urgent Booking Window" },
    created_at: new Date(Date.now() - 3600000 * 4)
  },
  {
    session_id: "sess-demo-849201",
    airline: "Air India",
    source_city: "Delhi",
    destination_city: "Cochin",
    route: "DEL → HYD → COK",
    journey_date: "2024-05-25",
    duration_minutes: 405,
    total_stops: 1,
    predicted_fare: 8920.00,
    fare_range: { min: 8100.00, max: 9850.00 },
    confidence: "Moderate",
    advisory: { action: "FAIR PRICE", headline: "Price is Stable" },
    created_at: new Date(Date.now() - 3600000 * 3)
  },
  {
    session_id: "sess-demo-849201",
    airline: "SpiceJet",
    source_city: "Delhi",
    destination_city: "Cochin",
    route: "DEL → COK",
    journey_date: "2024-05-25",
    duration_minutes: 195,
    total_stops: 0,
    predicted_fare: 4890.00,
    fare_range: { min: 4400.00, max: 5320.00 },
    confidence: "High",
    advisory: { action: "BUY NOW", headline: "Best Direct Rate" },
    created_at: new Date(Date.now() - 3600000 * 2)
  },
  {
    session_id: "sess-demo-918234",
    airline: "Vistara",
    source_city: "Banglore",
    destination_city: "New Delhi",
    route: "BLR → DEL",
    journey_date: "2024-06-12",
    duration_minutes: 170,
    total_stops: 0,
    predicted_fare: 7420.00,
    fare_range: { min: 6890.00, max: 8120.00 },
    confidence: "High",
    advisory: { action: "FAIR PRICE", headline: "Competitive Full Service" },
    created_at: new Date(Date.now() - 3600000 * 1)
  },
  {
    session_id: "sess-demo-918234",
    airline: "Jet Airways",
    source_city: "Banglore",
    destination_city: "New Delhi",
    route: "BLR → BOM → DEL",
    journey_date: "2024-06-12",
    duration_minutes: 345,
    total_stops: 1,
    predicted_fare: 11450.00,
    fare_range: { min: 10200.00, max: 12800.00 },
    confidence: "Moderate",
    advisory: { action: "CONSIDER SHIFTING", headline: "High Transit Surcharge" },
    created_at: new Date()
  }
]);
print("✓ Seeded prediction_logs.");

// ------------------------------------------------------------------------------
// 4. Seed Saved Comparisons
// ------------------------------------------------------------------------------
db.saved_comparisons.deleteMany({});
db.saved_comparisons.insertMany([
  {
    session_id: "sess-demo-849201",
    custom_label: "Budget Option - SpiceJet Non-Stop",
    airline: "SpiceJet",
    source_city: "Delhi",
    destination_city: "Cochin",
    route: "DEL → COK",
    total_stops: 0,
    duration_minutes: 195,
    predicted_fare: 4890.00,
    fare_range_display: "₹4,400 – ₹5,320",
    user_note: "Cheapest direct flight option for May vacation",
    is_favorite: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    session_id: "sess-demo-849201",
    custom_label: "Full Service - Air India",
    airline: "Air India",
    source_city: "Delhi",
    destination_city: "Cochin",
    route: "DEL → HYD → COK",
    total_stops: 1,
    duration_minutes: 405,
    predicted_fare: 8920.00,
    fare_range_display: "₹8,100 – ₹9,850",
    user_note: "Includes check-in baggage, but 1 stop layover",
    is_favorite: false,
    created_at: new Date(),
    updated_at: new Date()
  }
]);
print("✓ Seeded saved_comparisons.");

print("--- MongoDB seeding completed successfully! ---");
