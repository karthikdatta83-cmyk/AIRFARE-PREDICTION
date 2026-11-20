// ==============================================================================
// Airfare Price Estimation and Fare Pattern Analysis
// MongoDB Aggregation & Analytical Queries
// Description: Mongosh aggregation pipelines matching the problem statement
//              requirements for pattern analysis and algorithm comparisons.
// ==============================================================================

db = db.getSiblingDB("airfare_prediction_db");

print("\n--- Pipeline 1: Algorithm Performance Benchmark Ranking ---");
// Rank ML regression models by R² score and error metrics
var benchmarkResults = db.model_benchmarks.aggregate([
  { $sort: { r2_score: -1 } },
  {
    $project: {
      _id: 0,
      model_name: 1,
      algorithm_category: 1,
      r2_score: 1,
      rmse: 1,
      mae: 1,
      status: {
        $cond: { if: "$is_active_model", then: "ACTIVE MODEL", else: "BENCHMARK" }
      }
    }
  }
]).toArray();
printjson(benchmarkResults);

print("\n--- Pipeline 2: Fare Variation Across Stop Counts ---");
// Analyze how stops impact average predicted ticket fares
var stopsAnalysis = db.prediction_logs.aggregate([
  {
    $group: {
      _id: "$total_stops",
      total_predictions: { $sum: 1 },
      avg_predicted_fare: { $avg: "$predicted_fare" },
      min_fare: { $min: "$predicted_fare" },
      max_fare: { $max: "$predicted_fare" },
      avg_duration_minutes: { $avg: "$duration_minutes" }
    }
  },
  {
    $project: {
      _id: 0,
      stops: "$_id",
      stop_category: {
        $switch: {
          branches: [
            { case: { $eq: ["$_id", 0] }, then: "Non-Stop (Direct)" },
            { case: { $eq: ["$_id", 1] }, then: "1 Stop Layover" },
            { case: { $eq: ["$_id", 2] }, then: "2 Stops Transit" }
          ],
          default: "3+ Stops Multi-Transit"
        }
      },
      total_predictions: 1,
      avg_fare_inr: { $round: ["$avg_predicted_fare", 2] },
      min_fare_inr: "$min_fare",
      max_fare_inr: "$max_fare",
      avg_duration_mins: { $round: ["$avg_duration_minutes", 0] }
    }
  },
  { $sort: { stops: 1 } }
]).toArray();
printjson(stopsAnalysis);

print("\n--- Pipeline 3: Airline Pricing Tier Comparison ---");
// Analyze average fare and pricing spread per carrier
var airlineTierAnalysis = db.prediction_logs.aggregate([
  {
    $group: {
      _id: "$airline",
      query_count: { $sum: 1 },
      avg_fare: { $avg: "$predicted_fare" },
      lowest_fare: { $min: "$predicted_fare" },
      highest_fare: { $max: "$predicted_fare" }
    }
  },
  {
    $project: {
      _id: 0,
      airline: "$_id",
      query_count: 1,
      avg_fare: { $round: ["$avg_fare", 2] },
      lowest_fare: 1,
      highest_fare: 1,
      carrier_category: {
        $cond: {
          if: { $gte: ["$avg_fare", 10000] },
          then: "Premium Carrier",
          else: {
            $cond: {
              if: { $gte: ["$avg_fare", 6000] },
              then: "Mid-Tier Commercial",
              else: "Budget / Low-Cost"
            }
          }
        }
      }
    }
  },
  { $sort: { avg_fare: -1 } }
]).toArray();
printjson(airlineTierAnalysis);

print("\n--- Pipeline 4: User Saved Flights by Session ID ---");
// Retrieve bookmarked flights for a user session
var sessionSaved = db.saved_comparisons.find(
  { session_id: "sess-demo-849201" },
  { _id: 0, custom_label: 1, airline: 1, source_city: 1, destination_city: 1, predicted_fare: 1, is_favorite: 1 }
).sort({ predicted_fare: 1 }).toArray();
printjson(sessionSaved);
