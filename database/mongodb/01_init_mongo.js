// ==============================================================================
// Airfare Price Estimation and Fare Pattern Analysis
// MongoDB Initialization Script (Compatible with mongosh & MongoDB Compass)
// Target Database: airfare_prediction_db
// Description: Initializes collections with strict JSON schema validators and indexes.
// ==============================================================================

// Switch to the project database
db = db.getSiblingDB("airfare_prediction_db");

print("--- Initializing airfare_prediction_db in MongoDB ---");

// ------------------------------------------------------------------------------
// 1. Collection: prediction_logs
// Logs every ML inference request along with input parameters and results
// ------------------------------------------------------------------------------
db.createCollection("prediction_logs", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "session_id",
        "airline",
        "source_city",
        "destination_city",
        "duration_minutes",
        "total_stops",
        "predicted_fare",
        "created_at"
      ],
      properties: {
        session_id: {
          bsonType: "string",
          description: "Must be a string (anonymous session / device token)"
        },
        airline: {
          bsonType: "string",
          description: "Airline name (e.g. IndiGo, Air India, Vistara)"
        },
        source_city: {
          bsonType: "string",
          description: "Departure city"
        },
        destination_city: {
          bsonType: "string",
          description: "Arrival city"
        },
        route: {
          bsonType: ["string", "null"],
          description: "Flight transit sequence e.g. DEL → BOM → COK"
        },
        journey_date: {
          bsonType: ["string", "date"],
          description: "Date of travel (ISO date string or Date object)"
        },
        duration_minutes: {
          bsonType: "int",
          minimum: 1,
          maximum: 3000,
          description: "Total flight duration in minutes"
        },
        total_stops: {
          bsonType: "int",
          minimum: 0,
          maximum: 4,
          description: "Transit stops (0 for non-stop)"
        },
        predicted_fare: {
          bsonType: ["double", "int", "decimal"],
          minimum: 0,
          description: "Predicted fare in INR"
        },
        fare_range: {
          bsonType: "object",
          properties: {
            min: { bsonType: ["double", "int", "decimal"] },
            max: { bsonType: ["double", "int", "decimal"] }
          }
        },
        confidence: {
          enum: ["High", "Moderate", "Variable"],
          description: "Confidence bucket based on tree standard deviation"
        },
        advisory: {
          bsonType: "object",
          description: "Buy Now vs Wait advisory recommendation"
        },
        created_at: {
          bsonType: "date",
          description: "Timestamp of prediction"
        }
      }
    }
  }
});

// Indexes for prediction_logs
db.prediction_logs.createIndex({ session_id: 1 }, { name: "idx_session_id" });
db.prediction_logs.createIndex({ source_city: 1, destination_city: 1 }, { name: "idx_route_pair" });
db.prediction_logs.createIndex({ airline: 1 }, { name: "idx_airline" });
db.prediction_logs.createIndex({ created_at: -1 }, { name: "idx_created_desc" });

print("✓ Created 'prediction_logs' collection with validator and indexes.");

// ------------------------------------------------------------------------------
// 2. Collection: saved_comparisons
// Allows bookmarking flights to compare side-by-side without user login
// ------------------------------------------------------------------------------
db.createCollection("saved_comparisons", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "session_id",
        "airline",
        "source_city",
        "destination_city",
        "predicted_fare",
        "created_at"
      ],
      properties: {
        session_id: { bsonType: "string" },
        custom_label: { bsonType: ["string", "null"] },
        airline: { bsonType: "string" },
        source_city: { bsonType: "string" },
        destination_city: { bsonType: "string" },
        route: { bsonType: ["string", "null"] },
        total_stops: { bsonType: "int" },
        duration_minutes: { bsonType: "int" },
        predicted_fare: { bsonType: ["double", "int", "decimal"] },
        fare_range_display: { bsonType: ["string", "null"] },
        user_note: { bsonType: ["string", "null"] },
        is_favorite: { bsonType: "bool" },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" }
      }
    }
  }
});

db.saved_comparisons.createIndex({ session_id: 1, created_at: -1 }, { name: "idx_saved_session_date" });
print("✓ Created 'saved_comparisons' collection with validator and indexes.");

// ------------------------------------------------------------------------------
// 3. Collection: model_benchmarks
// Algorithm evaluation metrics for the UI dashboard and viva presentation
// ------------------------------------------------------------------------------
db.createCollection("model_benchmarks");
db.model_benchmarks.createIndex({ model_name: 1 }, { unique: true, name: "uniq_model_name" });
db.model_benchmarks.createIndex({ r2_score: -1 }, { name: "idx_r2_score" });
print("✓ Created 'model_benchmarks' collection with unique index.");

// ------------------------------------------------------------------------------
// 4. Collection: route_fare_statistics
// Summary statistics per route pair derived from historical training data
// ------------------------------------------------------------------------------
db.createCollection("route_fare_statistics");
db.route_fare_statistics.createIndex(
  { source_city: 1, destination_city: 1 }, 
  { unique: true, name: "uniq_source_destination" }
);
print("✓ Created 'route_fare_statistics' collection with unique index.");

print("--- MongoDB schema initialization complete! ---");
