-- ==============================================================================
-- Airfare Price Estimation and Fare Pattern Analysis
-- Database Schema: MySQL Relational Implementation
-- Target Database: airfare_prediction_db
-- Description: Supports prediction logging, saved comparisons, model benchmarks,
--              and route analytics without requiring user authentication.
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS airfare_prediction_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE airfare_prediction_db;

-- ------------------------------------------------------------------------------
-- 1. Table: prediction_logs
-- Stores every inference request made to the ML model (inputs + predicted outputs)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS prediction_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL COMMENT 'Anonymous browser/device session token',
    airline VARCHAR(60) NOT NULL COMMENT 'Airline carrier name',
    source_city VARCHAR(50) NOT NULL COMMENT 'Departure origin city',
    destination_city VARCHAR(50) NOT NULL COMMENT 'Arrival destination city',
    route VARCHAR(150) DEFAULT NULL COMMENT 'Flight path transit sequence e.g. DEL → BOM → COK',
    journey_day TINYINT UNSIGNED NOT NULL COMMENT 'Day of travel (1-31)',
    journey_month TINYINT UNSIGNED NOT NULL COMMENT 'Month of travel (1-12)',
    dep_hour TINYINT UNSIGNED NOT NULL COMMENT 'Departure hour (0-23)',
    dep_minute TINYINT UNSIGNED NOT NULL COMMENT 'Departure minute (0-59)',
    arrival_hour TINYINT UNSIGNED NOT NULL COMMENT 'Arrival hour (0-23)',
    arrival_minute TINYINT UNSIGNED NOT NULL COMMENT 'Arrival minute (0-59)',
    duration_minutes INT UNSIGNED NOT NULL COMMENT 'Flight duration in minutes',
    total_stops TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Number of transit stops (0, 1, 2, etc.)',
    additional_info VARCHAR(100) DEFAULT 'No info' COMMENT 'Service/baggage notes',
    predicted_fare DECIMAL(10, 2) NOT NULL COMMENT 'Model predicted price in INR',
    fare_range_min DECIMAL(10, 2) DEFAULT NULL COMMENT '10th percentile tree price bound',
    fare_range_max DECIMAL(10, 2) DEFAULT NULL COMMENT '90th percentile tree price bound',
    confidence_level ENUM('High', 'Moderate', 'Variable') DEFAULT 'Moderate',
    advisory_action VARCHAR(50) DEFAULT NULL COMMENT 'Advisory e.g. BUY NOW, FAIR PRICE, CONSIDER SHIFTING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_session (session_id),
    INDEX idx_route_pair (source_city, destination_city),
    INDEX idx_airline (airline),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 2. Table: saved_comparisons
-- Full CRUD support for users bookmarking flights to compare without an account
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS saved_comparisons (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL COMMENT 'Session identifier for bookmark ownership',
    custom_label VARCHAR(100) DEFAULT NULL COMMENT 'User-defined tag e.g. Option A - Morning Flight',
    airline VARCHAR(60) NOT NULL,
    source_city VARCHAR(50) NOT NULL,
    destination_city VARCHAR(50) NOT NULL,
    route VARCHAR(150) DEFAULT NULL,
    total_stops TINYINT UNSIGNED NOT NULL DEFAULT 0,
    duration_minutes INT UNSIGNED NOT NULL,
    predicted_fare DECIMAL(10, 2) NOT NULL,
    fare_range_display VARCHAR(60) DEFAULT NULL COMMENT 'Formatted range e.g. ₹4,500 – ₹5,200',
    user_note TEXT DEFAULT NULL COMMENT 'Custom user note/budget remarks',
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_saved_session (session_id),
    INDEX idx_saved_created (created_at)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 3. Table: model_benchmarks
-- Stores algorithm performance comparisons to feed project analytics and charts
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS model_benchmarks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(80) NOT NULL COMMENT 'Algorithm name e.g. Random Forest Regressor',
    algorithm_category VARCHAR(50) NOT NULL COMMENT 'Linear, Tree Ensemble, Boosting, etc.',
    r2_score DECIMAL(6, 4) NOT NULL COMMENT 'Coefficient of Determination R^2',
    rmse DECIMAL(10, 2) NOT NULL COMMENT 'Root Mean Squared Error (INR)',
    mae DECIMAL(10, 2) NOT NULL COMMENT 'Mean Absolute Error (INR)',
    is_active_model BOOLEAN DEFAULT FALSE COMMENT 'Currently deployed model in API',
    hyperparameters JSON DEFAULT NULL COMMENT 'Tuned parameters (n_estimators, max_depth, etc.)',
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_model_name (model_name)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 4. Table: route_fare_statistics
-- Aggregated baseline statistics derived from training data for quick dashboard lookups
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS route_fare_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_city VARCHAR(50) NOT NULL,
    destination_city VARCHAR(50) NOT NULL,
    average_fare DECIMAL(10, 2) NOT NULL,
    median_fare DECIMAL(10, 2) NOT NULL,
    min_observed_fare DECIMAL(10, 2) NOT NULL,
    max_observed_fare DECIMAL(10, 2) NOT NULL,
    avg_duration_minutes INT UNSIGNED NOT NULL,
    popular_airline VARCHAR(60) DEFAULT NULL,
    sample_count INT UNSIGNED NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uq_city_pair (source_city, destination_city)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 5. Views for Quick Reporting and Viva Demonstrations
-- ------------------------------------------------------------------------------

-- View: Recent prediction history with formatted date and duration
CREATE OR REPLACE VIEW vw_recent_predictions AS
SELECT 
    id,
    session_id,
    airline,
    CONCAT(source_city, ' → ', destination_city) AS journey,
    route,
    CONCAT(FLOOR(duration_minutes / 60), 'h ', MOD(duration_minutes, 60), 'm') AS duration_formatted,
    total_stops,
    CONCAT('₹', FORMAT(predicted_fare, 2)) AS formatted_price,
    confidence_level,
    advisory_action,
    DATE_FORMAT(created_at, '%Y-%m-%d %H:%i') AS predicted_on
FROM prediction_logs
ORDER BY created_at DESC;

-- View: Airline price performance breakdown
CREATE OR REPLACE VIEW vw_airline_price_analysis AS
SELECT 
    airline,
    COUNT(*) AS total_predictions_requested,
    ROUND(AVG(predicted_fare), 2) AS avg_fare,
    ROUND(MIN(predicted_fare), 2) AS min_fare,
    ROUND(MAX(predicted_fare), 2) AS max_fare,
    ROUND(AVG(duration_minutes), 0) AS avg_duration_mins
FROM prediction_logs
GROUP BY airline;
