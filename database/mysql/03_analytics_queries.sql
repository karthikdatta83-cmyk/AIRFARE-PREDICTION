-- ==============================================================================
-- Airfare Price Estimation and Fare Pattern Analysis
-- MySQL Analytical & Viva Queries
-- Description: Core SQL queries to demonstrate data analysis, aggregations,
--              and pattern mining as requested in the problem statement.
-- ==============================================================================

USE airfare_prediction_db;

-- ------------------------------------------------------------------------------
-- Query 1: Algorithm Performance Comparison Benchmark (Problem Statement Step 8)
-- Ranks ML regression models by R² score and error metrics
-- ------------------------------------------------------------------------------
SELECT 
    model_name,
    algorithm_category,
    r2_score,
    rmse AS rmse_inr,
    mae AS mae_inr,
    CASE 
        WHEN is_active_model = TRUE THEN 'ACTIVE IN DEPLOYMENT'
        ELSE 'CANDIDATE'
    END AS deployment_status
FROM model_benchmarks
ORDER BY r2_score DESC;

-- ------------------------------------------------------------------------------
-- Query 2: Fare Variation Across Stop Counts (Direct vs 1-Stop vs Multi-Stop)
-- Analyzes how layovers increase average ticket cost
-- ------------------------------------------------------------------------------
SELECT 
    total_stops,
    CASE 
        WHEN total_stops = 0 THEN 'Non-Stop (Direct)'
        WHEN total_stops = 1 THEN '1 Stop Layover'
        WHEN total_stops = 2 THEN '2 Stops Transit'
        ELSE '3+ Stops Multi-Transit'
    END AS stop_category,
    COUNT(*) AS total_estimates,
    ROUND(AVG(predicted_fare), 2) AS avg_fare_inr,
    ROUND(MIN(predicted_fare), 2) AS min_fare_inr,
    ROUND(MAX(predicted_fare), 2) AS max_fare_inr,
    ROUND(AVG(duration_minutes), 0) AS avg_duration_mins
FROM prediction_logs
GROUP BY total_stops
ORDER BY total_stops ASC;

-- ------------------------------------------------------------------------------
-- Query 3: Airline Pricing Tier Comparison (Budget vs Premium Carriers)
-- Identifies premium markup across airlines on identical or similar routes
-- ------------------------------------------------------------------------------
SELECT 
    airline,
    COUNT(*) AS search_count,
    ROUND(AVG(predicted_fare), 2) AS avg_predicted_fare,
    ROUND(MIN(predicted_fare), 2) AS lowest_fare,
    ROUND(MAX(predicted_fare), 2) AS highest_fare,
    CASE 
        WHEN AVG(predicted_fare) >= 10000 THEN 'Premium / Full Service'
        WHEN AVG(predicted_fare) BETWEEN 6000 AND 9999 THEN 'Mid-Tier Commercial'
        ELSE 'Budget / Low-Cost Carrier'
    END AS carrier_classification
FROM prediction_logs
GROUP BY airline
ORDER BY avg_predicted_fare DESC;

-- ------------------------------------------------------------------------------
-- Query 4: Most Requested Routes & Fare Distribution
-- Tracks which origin-destination sectors are most frequently queried
-- ------------------------------------------------------------------------------
SELECT 
    source_city,
    destination_city,
    COUNT(*) AS search_frequency,
    ROUND(AVG(predicted_fare), 2) AS avg_queried_fare,
    ROUND(AVG(duration_minutes) / 60, 1) AS avg_flight_hours
FROM prediction_logs
GROUP BY source_city, destination_city
ORDER BY search_frequency DESC;

-- ------------------------------------------------------------------------------
-- Query 5: User Saved Flights Comparison (CRUD Demonstration)
-- Fetches side-by-side comparison for an anonymous session ID
-- ------------------------------------------------------------------------------
SELECT 
    custom_label,
    airline,
    CONCAT(source_city, ' → ', destination_city) AS sector,
    CONCAT(FLOOR(duration_minutes / 60), 'h ', MOD(duration_minutes, 60), 'm') AS flight_duration,
    CONCAT('₹', FORMAT(predicted_fare, 2)) AS price,
    fare_range_display,
    user_note,
    is_favorite
FROM saved_comparisons
WHERE session_id = 'sess-demo-849201'
ORDER BY predicted_fare ASC;

-- ------------------------------------------------------------------------------
-- Query 6: Prediction Confidence & Advisory Distribution
-- Analyzes stability of model inference and user booking advice
-- ------------------------------------------------------------------------------
SELECT 
    advisory_action,
    confidence_level,
    COUNT(*) AS count_predictions,
    ROUND(AVG(predicted_fare), 2) AS avg_fare
FROM prediction_logs
GROUP BY advisory_action, confidence_level
ORDER BY count_predictions DESC;
