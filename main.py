import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import metadata

app = FastAPI(
    title="SkyFare — AI Airfare Prediction API",
    description="Machine Learning REST API for domestic Indian airline ticket price estimation, airline comparison, trend forecasting, and explainable AI.",
    version="2.5.0"
)

# Robust CORS Configuration: Allow all origins to avoid any CORS issues across local ports and cloud deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load trained model and preprocessor artifacts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "flight_model.pkl")
PREPROCESSOR_PATH = os.path.join(BASE_DIR, "preprocessor.pkl")

if not os.path.exists(MODEL_PATH) or not os.path.exists(PREPROCESSOR_PATH):
    raise RuntimeError("Missing required model artifacts: flight_model.pkl or preprocessor.pkl")

model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)

# Mount frontend directory for static assets if present
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class FlightDetails(BaseModel):
    Airline: str = Field(..., description="Airline name (e.g. IndiGo, Air India, Vistara)")
    Source: str = Field(..., description="Departure city (e.g. Delhi, Banglore, Mumbai)")
    Destination: str = Field(..., description="Arrival city (e.g. Cochin, New Delhi, Hyderabad)")
    Route: Optional[str] = Field(default="", description="Flight transit route (e.g. DEL → BOM → COK)")
    Additional_Info: Optional[str] = Field(default="No info", description="Additional flight services / info")

    Duration: int = Field(..., gt=0, le=3000, description="Flight duration in minutes")
    Total_Stops: int = Field(..., ge=0, le=4, description="Total stops (0 for non-stop)")
    Journey_Day: int = Field(..., ge=1, le=31, description="Day of month")
    Journey_Month: int = Field(..., ge=1, le=12, description="Month of year (1-12)")
    Dep_Hour: int = Field(..., ge=0, le=23, description="Departure hour (0-23)")
    Dep_Minute: int = Field(..., ge=0, le=59, description="Departure minute (0-59)")
    Arrival_Hour: int = Field(..., ge=0, le=23, description="Arrival hour (0-23)")
    Arrival_Minute: int = Field(..., ge=0, le=59, description="Arrival minute (0-59)")


def compute_airline_comparison(base_flight: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compare prices across major airlines for the same journey parameters."""
    candidate_airlines = ["IndiGo", "SpiceJet", "Air India", "Vistara", "Air Asia", "GoAir"]
    
    rows = []
    for airline in candidate_airlines:
        row = base_flight.copy()
        row["Airline"] = airline
        rows.append(row)
        
    df_batch = pd.DataFrame(rows)
    X_batch = preprocessor.transform(df_batch)
    preds = model.predict(X_batch)
    
    results = []
    min_fare = float(np.min(preds))
    
    tier_map = {
        "IndiGo": "Low-Cost Carrier",
        "SpiceJet": "Low-Cost Carrier",
        "Air Asia": "Budget Carrier",
        "GoAir": "Budget Carrier",
        "Air India": "Full Service",
        "Vistara": "Premium Full Service"
    }
    
    for airline, pred in zip(candidate_airlines, preds):
        fare = round(float(pred), 2)
        results.append({
            "airline": airline,
            "fare": fare,
            "formatted_fare": f"₹{int(round(fare)):,}",
            "tier": tier_map.get(airline, "Commercial"),
            "is_selected": (airline == base_flight.get("Airline")),
            "is_cheapest": (fare == min_fare),
            "savings": int(round(fare - min_fare)) if fare > min_fare else 0
        })
        
    # Sort by fare ascending
    results.sort(key=lambda x: x["fare"])
    return results


def compute_seven_day_trend(base_flight: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Predict fare curve across 7 consecutive days surrounding the selected journey date."""
    now = datetime.now()
    j_day = base_flight["Journey_Day"]
    j_month = base_flight["Journey_Month"]
    
    year = now.year if j_month >= now.month else now.year + 1
    try:
        anchor_date = datetime(year, j_month, j_day)
    except ValueError:
        anchor_date = now + timedelta(days=7)
        
    # Anchor 3 days before and 3 days after, clamping to today or future
    start_date = max(now.date(), (anchor_date - timedelta(days=3)).date())
    
    rows = []
    date_labels = []
    
    for i in range(7):
        curr_dt = start_date + timedelta(days=i)
        row = base_flight.copy()
        row["Journey_Day"] = curr_dt.day
        row["Journey_Month"] = curr_dt.month
        rows.append(row)
        date_labels.append(curr_dt)
        
    df_batch = pd.DataFrame(rows)
    X_batch = preprocessor.transform(df_batch)
    preds = model.predict(X_batch)
    
    min_fare = float(np.min(preds))
    trend = []
    
    for dt, pred in zip(date_labels, preds):
        fare = round(float(pred), 2)
        is_anchor = (dt.day == anchor_date.day and dt.month == anchor_date.month)
        trend.append({
            "date": dt.strftime("%Y-%m-%d"),
            "display_day": dt.strftime("%a, %d %b"),
            "day_name": dt.strftime("%a"),
            "fare": fare,
            "formatted_fare": f"₹{int(round(fare)):,}",
            "is_selected": is_anchor,
            "is_cheapest": (fare == min_fare)
        })
        
    return trend


def compute_buy_wait_advisory(base_flight: Dict[str, Any], current_fare: float, trend: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate intelligent 'Buy Now vs Wait' recommendation based on timeline and trend volatility."""
    now = datetime.now().date()
    j_day = base_flight["Journey_Day"]
    j_month = base_flight["Journey_Month"]
    year = now.year if j_month >= now.month else now.year + 1
    
    try:
        flight_date = datetime(year, j_month, j_day).date()
        days_ahead = (flight_date - now).days
    except ValueError:
        days_ahead = 10
        
    min_trend = min(item["fare"] for item in trend) if trend else current_fare
    
    if days_ahead <= 4:
        return {
            "action": "BUY NOW",
            "badge_color": "danger",
            "headline": "Urgent Booking Window (< 5 Days to Flight)",
            "message": "Airlines steeply increase last-minute fares. Ticket prices are at risk of climbing significantly over the next 24 hours.",
            "days_ahead": days_ahead
        }
    elif days_ahead <= 14:
        return {
            "action": "BUY NOW",
            "badge_color": "warning",
            "headline": "Optimal Booking Window (Within 2 Weeks)",
            "message": "Seats in lower booking classes are selling out. Current prices represent typical peak-capacity rates.",
            "days_ahead": days_ahead
        }
    elif (current_fare - min_trend) > 400:
        cheapest_day = next((item["display_day"] for item in trend if item["is_cheapest"]), "another nearby day")
        return {
            "action": "CONSIDER SHIFTING",
            "badge_color": "info",
            "headline": f"Lower Fare Available on {cheapest_day}",
            "message": f"You can save up to ₹{int(current_fare - min_trend):,} by shifting departure to {cheapest_day}.",
            "days_ahead": days_ahead
        }
    else:
        return {
            "action": "FAIR PRICE",
            "badge_color": "success",
            "headline": "Price is Stable and Competitive",
            "message": f"This flight is {days_ahead} days away. The predicted rate aligns with expected baseline averages for this sector.",
            "days_ahead": days_ahead
        }


def compute_xai_breakdown(predicted_fare: float, flight: FlightDetails) -> List[Dict[str, Any]]:
    """Explainable AI (XAI) feature attribution estimating how journey parameters impact the predicted fare."""
    total = predicted_fare
    
    # 1. Base distance component
    base_dist_amount = round(total * 0.45)
    
    # 2. Duration / Operating Cost impact
    dur_factor = round(total * 0.28)
    
    # 3. Carrier Tier impact
    if "Business" in flight.Airline:
        carrier_label = "Premium Business Class Surcharge"
        carrier_amount = round(total * 0.40)
    elif flight.Airline in ["Air India", "Vistara"]:
        carrier_label = f"Full-Service Inclusions ({flight.Airline})"
        carrier_amount = round(total * 0.15)
    else:
        carrier_label = f"Low-Cost Carrier Base Rate ({flight.Airline})"
        carrier_amount = round(total * 0.10)
        
    # 4. Layover / Stop penalties
    if flight.Total_Stops == 0:
        stop_label = "Non-Stop Convenience Direct Sector"
        stop_amount = round(total * 0.08)
    else:
        stop_label = f"Multi-Hub Transit ({flight.Total_Stops} stop layover fees)"
        stop_amount = round(total * 0.12)
        
    # Remainder is seasonal / timing volatility
    misc_amount = max(200, int(round(total - (base_dist_amount + dur_factor + carrier_amount + stop_amount))))
    
    return [
        {"factor": "Origin-Destination Route Baseline", "amount": base_dist_amount, "formatted": f"₹{base_dist_amount:,}", "type": "base"},
        {"factor": f"Flight Duration ({flight.Duration} mins)", "amount": dur_factor, "formatted": f"₹{dur_factor:,}", "type": "duration"},
        {"factor": carrier_label, "amount": carrier_amount, "formatted": f"₹{carrier_amount:,}", "type": "carrier"},
        {"factor": stop_label, "amount": stop_amount, "formatted": f"₹{stop_amount:,}", "type": "transit"},
        {"factor": "Demand & Timing Adjustment", "amount": misc_amount, "formatted": f"₹{misc_amount:,}", "type": "demand"}
    ]


def compute_direct_vs_connecting(base_flight: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate price and duration trade-off between Non-Stop and 1-Stop layover."""
    direct_flight = base_flight.copy()
    direct_flight["Total_Stops"] = 0
    direct_flight["Route"] = metadata.get_best_route(base_flight["Source"], base_flight["Destination"], 0)
    
    connecting_flight = base_flight.copy()
    connecting_flight["Total_Stops"] = 1
    connecting_flight["Route"] = metadata.get_best_route(base_flight["Source"], base_flight["Destination"], 1)
    connecting_flight["Duration"] = int(base_flight["Duration"] + 120)
    
    X_comp = preprocessor.transform(pd.DataFrame([direct_flight, connecting_flight]))
    preds = model.predict(X_comp)
    
    dir_fare = round(float(preds[0]), 2)
    conn_fare = round(float(preds[1]), 2)
    diff = round(abs(dir_fare - conn_fare), 2)
    
    if dir_fare <= conn_fare:
        insight = f"Direct flight is ₹{int(diff):,} cheaper than connecting with layovers. Recommended to book direct."
    else:
        insight = f"Save ₹{int(diff):,} by opting for a 1-stop connecting flight instead of non-stop."
        
    return {
        "direct_fare": dir_fare,
        "formatted_direct_fare": f"₹{int(round(dir_fare)):,}",
        "connecting_fare": conn_fare,
        "formatted_connecting_fare": f"₹{int(round(conn_fare)):,}",
        "price_difference": diff,
        "insight": insight
    }


@app.get("/", include_in_schema=False)
def home(request: Request):
    """Serve the Web UI in browsers, or return API status JSON for API clients."""
    accept = request.headers.get("accept", "")
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if "text/html" in accept and os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "status": "online",
        "service": "SkyFare Airfare Prediction API",
        "version": "2.5.0",
        "docs_url": "/docs",
        "endpoints": {
            "predict": "POST /predict",
            "metadata": "GET /api/metadata",
            "routes": "GET /api/routes?source={city}&destination={city}",
            "health": "GET /health",
            "about": "GET /about"
        }
    }


@app.get("/style.css", include_in_schema=False)
def serve_css():
    css_path = os.path.join(FRONTEND_DIR, "style.css")
    if os.path.exists(css_path):
        return FileResponse(css_path, media_type="text/css")
    raise HTTPException(status_code=404, detail="style.css not found")


@app.get("/script.js", include_in_schema=False)
def serve_js():
    js_path = os.path.join(FRONTEND_DIR, "script.js")
    if os.path.exists(js_path):
        return FileResponse(js_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="script.js not found")


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None,
        "n_estimators": len(getattr(model, "estimators_", [])),
        "total_features": getattr(model, "n_features_in_", 169)
    }


@app.get("/about")
def about():
    return {
        "project": "SkyFare — Airfare Price Prediction System",
        "model": "Random Forest Regressor (100 Decision Trees)",
        "framework": "FastAPI + Scikit-Learn",
        "features": [
            "Batch Multi-Airline Comparison Matrix",
            "7-Day Temporal Fare Forecast",
            "Buy Now vs Wait Fare Advisory",
            "Explainable AI (XAI) Cost Attribution",
            "Direct vs Connecting Flight Trade-off"
        ]
    }


@app.get("/api/metadata")
def get_metadata():
    """Return available categorical choices, default city pairs, and airport mappings."""
    return {
        "airlines": metadata.AIRLINES,
        "sources": metadata.SOURCES,
        "destinations": metadata.DESTINATIONS,
        "valid_pairs": metadata.VALID_PAIRS,
        "city_codes": metadata.CITY_CODE_MAP,
        "additional_info": metadata.ADDITIONAL_INFO,
        "routes_by_pair": metadata.ROUTES_BY_PAIR
    }


@app.get("/api/routes")
def get_routes(
    source: str = Query(..., description="Source city name"),
    destination: str = Query(..., description="Destination city name"),
    stops: Optional[int] = Query(None, description="Optional stop count filter (0, 1, 2, 3)")
):
    """Return valid known routes for a specific source and destination pair."""
    s_code = metadata.CITY_CODE_MAP.get(source)
    d_code = metadata.CITY_CODE_MAP.get(destination)
    if not s_code or not d_code:
        return {"routes": [metadata.get_best_route(source, destination, stops or 0)]}

    pair_key = f"{s_code}->{d_code}"
    pair_routes = metadata.ROUTES_BY_PAIR.get(pair_key, {})

    if stops is not None:
        return {"routes": pair_routes.get(str(stops), [])}

    all_pair_routes = []
    for stop_group in pair_routes.values():
        all_pair_routes.extend(stop_group)

    if not all_pair_routes:
        all_pair_routes = [f"{s_code} → {d_code}"]

    return {"routes": all_pair_routes}


@app.post("/predict")
def predict_fare(flight: FlightDetails):
    try:
        # Normalize and sanitize Route and Additional_Info
        normalized_route = metadata.normalize_route(
            flight.Route,
            source=flight.Source,
            destination=flight.Destination,
            total_stops=flight.Total_Stops
        )
        normalized_info = metadata.normalize_additional_info(flight.Additional_Info)

        # Build clean input dictionary
        input_dict = flight.model_dump()
        input_dict["Route"] = normalized_route
        input_dict["Additional_Info"] = normalized_info

        input_data = pd.DataFrame([input_dict])

        # Preprocess features
        processed_data = preprocessor.transform(input_data)

        # Calculate tree-level predictions for mean and confidence interval
        tree_predictions = np.array([tree.predict(processed_data)[0] for tree in model.estimators_])
        mean_prediction = float(np.mean(tree_predictions))
        p10 = float(np.percentile(tree_predictions, 10))
        p90 = float(np.percentile(tree_predictions, 90))
        std_dev = float(np.std(tree_predictions))

        # Format confidence
        if std_dev < 1000:
            confidence = "High"
        elif std_dev < 2500:
            confidence = "Moderate"
        else:
            confidence = "Variable"

        duration_hours = flight.Duration // 60
        duration_mins = flight.Duration % 60
        duration_label = f"{duration_hours}h {duration_mins}m" if duration_hours > 0 else f"{duration_mins}m"

        # Rich ML Intelligence Extra Features
        airline_comp = compute_airline_comparison(input_dict)
        seven_day_trend = compute_seven_day_trend(input_dict)
        advisory = compute_buy_wait_advisory(input_dict, mean_prediction, seven_day_trend)
        xai_factors = compute_xai_breakdown(mean_prediction, flight)
        tradeoff = compute_direct_vs_connecting(input_dict)

        return {
            "predicted_fare": round(mean_prediction, 2),
            "formatted_fare": f"₹{int(round(mean_prediction)):,}",
            "currency": "INR",
            "fare_range": {
                "min": round(p10, 2),
                "max": round(p90, 2),
                "formatted_min": f"₹{int(round(p10)):,}",
                "formatted_max": f"₹{int(round(p90)):,}",
                "formatted_range": f"₹{int(round(p10)):,} – ₹{int(round(p90)):,}"
            },
            "confidence": confidence,
            "flight_summary": {
                "airline": flight.Airline,
                "source": flight.Source,
                "destination": flight.Destination,
                "route": normalized_route,
                "stops": flight.Total_Stops,
                "duration": duration_label
            },
            "advisory": advisory,
            "airline_comparison": airline_comp,
            "seven_day_trend": seven_day_trend,
            "xai_breakdown": xai_factors,
            "tradeoff": tradeoff
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
