-- ==============================================================================
-- Airfare Price Estimation and Fare Pattern Analysis
-- Database Seed Data: MySQL Relational Implementation
-- Description: Realistic initial data for model benchmarks, route statistics,
--              and sample user interactions.
-- ==============================================================================

USE airfare_prediction_db;

-- ------------------------------------------------------------------------------
-- 1. Populate Model Benchmarks (Directly addresses Step 8 of problem statement)
-- ------------------------------------------------------------------------------
INSERT INTO model_benchmarks 
    (model_name, algorithm_category, r2_score, rmse, mae, is_active_model, hyperparameters)
VALUES
    ('Linear Regression (Baseline)', 'Linear', 0.6120, 2740.50, 1980.20, FALSE, 
     JSON_OBJECT('fit_intercept', TRUE, 'normalize', FALSE)),

    ('Decision Tree Regressor', 'Tree-based', 0.7240, 2190.80, 1450.40, FALSE, 
     JSON_OBJECT('max_depth', 16, 'min_samples_split', 10)),

    ('Random Forest Regressor', 'Tree Ensemble (Bagging)', 0.8842, 1640.25, 1120.10, TRUE, 
     JSON_OBJECT('n_estimators', 100, 'max_depth', 25, 'min_samples_split', 5, 'n_jobs', -1)),

    ('Gradient Boosting / XGBoost', 'Tree Ensemble (Boosting)', 0.8715, 1710.60, 1180.40, FALSE, 
     JSON_OBJECT('n_estimators', 150, 'learning_rate', 0.08, 'max_depth', 6))
ON DUPLICATE KEY UPDATE 
    r2_score = VALUES(r2_score),
    rmse = VALUES(rmse),
    mae = VALUES(mae);

-- ------------------------------------------------------------------------------
-- 2. Populate Route Fare Statistics (From 2019 Training Data Patterns)
-- ------------------------------------------------------------------------------
INSERT INTO route_fare_statistics 
    (source_city, destination_city, average_fare, median_fare, min_observed_fare, max_observed_fare, avg_duration_minutes, popular_airline, sample_count)
VALUES
    ('Delhi', 'Cochin', 10539.43, 10262.00, 4200.00, 54747.00, 795, 'Jet Airways', 4537),
    ('Banglore', 'New Delhi', 11919.33, 10844.00, 3359.00, 79512.00, 520, 'Air India', 2200),
    ('Banglore', 'Delhi', 5143.92, 4823.00, 3359.00, 16655.00, 170, 'IndiGo', 1565),
    ('Kolkata', 'Banglore', 9158.39, 8355.00, 3480.00, 31783.00, 755, 'Air India', 2871),
    ('Mumbai', 'Hyderabad', 5059.73, 4053.00, 1965.00, 25139.00, 195, 'Jet Airways', 697),
    ('Chennai', 'Kolkata', 4850.82, 3850.00, 2050.00, 19650.00, 145, 'IndiGo', 381)
ON DUPLICATE KEY UPDATE 
    average_fare = VALUES(average_fare),
    sample_count = VALUES(sample_count);

-- ------------------------------------------------------------------------------
-- 3. Populate Sample Prediction Logs (Demonstrating log capture)
-- ------------------------------------------------------------------------------
INSERT INTO prediction_logs 
    (session_id, airline, source_city, destination_city, route, journey_day, journey_month, dep_hour, dep_minute, arrival_hour, arrival_minute, duration_minutes, total_stops, additional_info, predicted_fare, fare_range_min, fare_range_max, confidence_level, advisory_action)
VALUES
    ('sess-demo-849201', 'IndiGo', 'Delhi', 'Cochin', 'DEL → BOM → COK', 25, 5, 10, 30, 16, 45, 375, 1, 'No info', 6450.00, 5920.00, 7150.00, 'High', 'BUY NOW'),
    ('sess-demo-849201', 'Air India', 'Delhi', 'Cochin', 'DEL → HYD → COK', 25, 5, 6, 15, 13, 00, 405, 1, '1 Long layover', 8920.00, 8100.00, 9850.00, 'Moderate', 'FAIR PRICE'),
    ('sess-demo-849201', 'SpiceJet', 'Delhi', 'Cochin', 'DEL → COK', 25, 5, 14, 00, 17, 15, 195, 0, 'No info', 4890.00, 4400.00, 5320.00, 'High', 'BUY NOW'),
    ('sess-demo-918234', 'Vistara', 'Banglore', 'New Delhi', 'BLR → DEL', 12, 6, 8, 30, 11, 20, 170, 0, 'No info', 7420.00, 6890.00, 8120.00, 'High', 'FAIR PRICE'),
    ('sess-demo-918234', 'Jet Airways', 'Banglore', 'New Delhi', 'BLR → BOM → DEL', 12, 6, 18, 00, 23, 45, 345, 1, 'In-flight meal not included', 11450.00, 10200.00, 12800.00, 'Moderate', 'CONSIDER SHIFTING'),
    ('sess-demo-340192', 'Air Asia', 'Kolkata', 'Banglore', 'CCU → DEL → BLR', 18, 4, 9, 10, 17, 30, 500, 1, 'No info', 5820.00, 5200.00, 6490.00, 'Moderate', 'FAIR PRICE'),
    ('sess-demo-340192', 'IndiGo', 'Mumbai', 'Hyderabad', 'BOM → HYD', 3, 5, 19, 45, 21, 15, 90, 0, 'No info', 3150.00, 2850.00, 3490.00, 'High', 'BUY NOW');

-- ------------------------------------------------------------------------------
-- 4. Populate Sample Saved Comparisons (Demonstrating User Bookmark CRUD)
-- ------------------------------------------------------------------------------
INSERT INTO saved_comparisons
    (session_id, custom_label, airline, source_city, destination_city, route, total_stops, duration_minutes, predicted_fare, fare_range_display, user_note, is_favorite)
VALUES
    ('sess-demo-849201', 'Budget Option - SpiceJet Non-Stop', 'SpiceJet', 'Delhi', 'Cochin', 'DEL → COK', 0, 195, 4890.00, '₹4,400 – ₹5,320', 'Cheapest direct flight for May trip', TRUE),
    ('sess-demo-849201', 'Full Service - Air India', 'Air India', 'Delhi', 'Cochin', 'DEL → HYD → COK', 1, 405, 8920.00, '₹8,100 – ₹9,850', 'Includes luggage and meal, but has 1 layover', FALSE),
    ('sess-demo-918234', 'Fast Morning Flight', 'Vistara', 'Banglore', 'New Delhi', 'BLR → DEL', 0, 170, 7420.00, '₹6,890 – ₹8,120', 'Great timings for business meeting', TRUE);
