import os
import joblib
import numpy as np
import pandas as pd
from typing import Optional
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import metadata

app = FastAPI(
    title="SkyFare — AI Airfare Prediction API",
    description="Machine Learning REST API for estimating domestic Indian airline ticket prices using Random Forest Regression.",
    version="2.0.0"
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
        "version": "2.0.0",
        "docs_url": "/docs",
        "endpoints": {
            "predict": "POST /predict",
            "metadata": "GET /api/metadata",
            "routes": "GET /api/routes?source={city}&destination={city}",
            "health": "GET /health",
            "about": "GET /about"
        }
    }


# Static file fallbacks for direct relative root fetches (style.css, script.js)
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
        "project": "SkyFare — Airfare Price Prediction",
        "model": "Random Forest Regressor (100 Decision Trees)",
        "framework": "FastAPI + Scikit-Learn",
        "features_engineered": [
            "Airline", "Source", "Destination", "Normalized Route", "Additional Info",
            "Duration (Minutes)", "Total Stops", "Journey Day", "Journey Month",
            "Departure Timing", "Arrival Timing"
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

        # Build single-row DataFrame for preprocessing
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
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
