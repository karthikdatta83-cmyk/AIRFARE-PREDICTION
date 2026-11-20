from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import joblib
import pandas as pd
import calendar

from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


# ==========================================
# 1. INITIALIZE FASTAPI
# ==========================================

app = FastAPI(
    title="SkyFare Airfare Prediction API",
    version="2.1"
)


# ==========================================
# 2. CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# 3. LOAD MODEL AND PREPROCESSOR
# ==========================================

try:
    model = joblib.load("flight_model.pkl")
    preprocessor = joblib.load("preprocessor.pkl")

except Exception as e:
    raise RuntimeError(f"Unable to load ML files: {e}")


# ==========================================
# 4. EXTRACT VALID CATEGORIES
# ==========================================

def extract_categories(obj, columns=None):

    categories_dict = {}

    if isinstance(obj, OneHotEncoder):

        if hasattr(obj, "feature_names_in_"):
            feature_names = list(obj.feature_names_in_)

        elif columns is not None:
            feature_names = list(columns)

        else:
            feature_names = []

        if len(feature_names) == len(obj.categories_):

            for column, categories in zip(
                feature_names,
                obj.categories_
            ):

                categories_dict[column] = {
                    str(value).strip()
                    for value in categories
                }

    elif isinstance(obj, Pipeline):

        for _, step in obj.steps:

            categories_dict.update(
                extract_categories(step, columns)
            )

    elif isinstance(obj, ColumnTransformer):

        for _, transformer, selected_columns in obj.transformers_:

            if transformer in ("drop", "passthrough"):
                continue

            categories_dict.update(
                extract_categories(
                    transformer,
                    selected_columns
                )
            )

    return categories_dict


VALID_CATEGORIES = extract_categories(preprocessor)


REQUIRED_CATEGORICAL_FIELDS = [
    "Airline",
    "Source",
    "Destination",
    "Route",
    "Additional_Info"
]

for field in REQUIRED_CATEGORICAL_FIELDS:

    if field not in VALID_CATEGORIES:

        raise RuntimeError(
            f"Could not extract valid categories for {field}. "
            "Check your preprocessor.pkl."
        )


# ==========================================
# 5. AIRPORT CODE MAPPING
# ==========================================

AIRPORT_CODES = {

    "Banglore": "BLR",
    "Chennai": "MAA",
    "Delhi": "DEL",
    "Kolkata": "CCU",
    "Mumbai": "BOM",
    "Cochin": "COK",
    "Hyderabad": "HYD",
    "New Delhi": "DEL"

}


# ==========================================
# 6. REQUEST MODEL
# ==========================================

class FlightDetails(BaseModel):

    Airline: str = Field(min_length=1)
    Source: str = Field(min_length=1)
    Destination: str = Field(min_length=1)
    Route: str = Field(min_length=1)
    Additional_Info: str = Field(min_length=1)

    Duration: int = Field(ge=5, le=2860)

    Total_Stops: int = Field(ge=0, le=4)

    Journey_Day: int = Field(ge=1, le=31)

    Journey_Month: int = Field(ge=1, le=12)

    Dep_Hour: int = Field(ge=0, le=23)

    Dep_Minute: int = Field(ge=0, le=59)

    Arrival_Hour: int = Field(ge=0, le=23)

    Arrival_Minute: int = Field(ge=0, le=59)


# ==========================================
# 7. NORMALIZE ROUTE
# ==========================================

def normalize_route(route):

    route = route.strip()

    route = route.replace("->", "→")
    route = route.replace("/", "→")

    parts = [
        part.strip()
        for part in route.split("→")
    ]

    return " → ".join(parts)


# ==========================================
# 8. VALIDATE FLIGHT
# ==========================================

def validate_flight(flight):

    if flight.Airline not in VALID_CATEGORIES["Airline"]:

        raise HTTPException(
            status_code=400,
            detail=f"Invalid airline: {flight.Airline}"
        )

    if flight.Source not in VALID_CATEGORIES["Source"]:

        raise HTTPException(
            status_code=400,
            detail=f"Invalid source: {flight.Source}"
        )

    if flight.Destination not in VALID_CATEGORIES["Destination"]:

        raise HTTPException(
            status_code=400,
            detail=f"Invalid destination: {flight.Destination}"
        )

    if flight.Source == flight.Destination:

        raise HTTPException(
            status_code=400,
            detail="Source and destination cannot be the same."
        )

    if flight.Additional_Info not in VALID_CATEGORIES["Additional_Info"]:

        raise HTTPException(
            status_code=400,
            detail="Invalid additional flight information."
        )

    route = normalize_route(flight.Route)

    if route not in VALID_CATEGORIES["Route"]:

        raise HTTPException(
            status_code=400,
            detail=f"Invalid route: {flight.Route}"
        )

    if flight.Source not in AIRPORT_CODES:

        raise HTTPException(
            status_code=400,
            detail="Unknown source airport."
        )

    if flight.Destination not in AIRPORT_CODES:

        raise HTTPException(
            status_code=400,
            detail="Unknown destination airport."
        )

    route_parts = [
        part.strip()
        for part in route.split("→")
    ]

    if len(route_parts) < 2:

        raise HTTPException(
            status_code=400,
            detail="Invalid route format."
        )

    expected_source = AIRPORT_CODES[flight.Source]
    expected_destination = AIRPORT_CODES[flight.Destination]

    if route_parts[0] != expected_source:

        raise HTTPException(
            status_code=400,
            detail="Route does not match the selected source."
        )

    if route_parts[-1] != expected_destination:

        raise HTTPException(
            status_code=400,
            detail="Route does not match the selected destination."
        )

    actual_stops = len(route_parts) - 2

    if flight.Total_Stops != actual_stops:

        raise HTTPException(
            status_code=400,
            detail="Number of stops does not match the selected route."
        )

    max_day = calendar.monthrange(
        2024,
        flight.Journey_Month
    )[1]

    if flight.Journey_Day > max_day:

        raise HTTPException(
            status_code=400,
            detail="Invalid day for the selected month."
        )

    if not 5 <= flight.Duration <= 2860:

        raise HTTPException(
            status_code=400,
            detail="Flight duration must be between 5 and 2860 minutes."
        )


# ==========================================
# 9. HOME & HEALTH ENDPOINTS
# ==========================================

@app.get("/")
def home():
    return {
        "message": "SkyFare Airfare Prediction API is running",
        "status": "success"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None
    }


# ==========================================
# 10. VERSION ENDPOINT
# ==========================================

@app.get("/version")
def version():

    return {
        "version": "dropdown-validation-v3",
        "validation_enabled": True,
        "dropdown_api": True
    }


# ==========================================
# 11. ABOUT ENDPOINT
# ==========================================

@app.get("/about")
def about():

    return {
        "project": "Airfare Price Estimation and Fare Pattern Analysis",
        "model": "Random Forest Regression",
        "validation": "Enabled"
    }


# ==========================================
# 12. DROPDOWN OPTIONS ENDPOINT
# ==========================================

@app.get("/options")
def get_options():

    airlines = sorted(VALID_CATEGORIES["Airline"])

    sources = sorted(VALID_CATEGORIES["Source"])

    destinations = sorted(VALID_CATEGORIES["Destination"])

    additional_info = sorted(
        VALID_CATEGORIES["Additional_Info"]
    )

    valid_routes = sorted(VALID_CATEGORIES["Route"])

    route_options = []

    for route in valid_routes:

        normalized = normalize_route(route)

        parts = [
            part.strip()
            for part in normalized.split("→")
        ]

        if len(parts) < 2:
            continue

        start_code = parts[0]
        end_code = parts[-1]

        stops = len(parts) - 2

        for source in sources:

            if AIRPORT_CODES.get(source) != start_code:
                continue

            for destination in destinations:

                if source == destination:
                    continue

                if AIRPORT_CODES.get(destination) != end_code:
                    continue

                route_options.append({

                    "source": source,

                    "destination": destination,

                    "route": normalized,

                    "stops": stops

                })

    return {

        "airlines": airlines,

        "sources": sources,

        "destinations": destinations,

        "additional_info": additional_info,

        "routes": route_options

    }


# ==========================================
# 13. PREDICTION ENDPOINT
# ==========================================

@app.post("/predict")
def predict_fare(flight: FlightDetails):

    # Validate inputs

    validate_flight(flight)

    # Prepare input data

    input_data = pd.DataFrame([
        flight.model_dump()
    ])

    input_data["Route"] = normalize_route(flight.Route)

    # Preprocess

    try:

        processed_data = preprocessor.transform(input_data)

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=f"Unable to process flight details: {str(e)}"
        )

    # Predict

    try:

        prediction = model.predict(processed_data)

        fare = float(prediction[0])

        if not pd.notna(fare) or fare <= 0:

            raise HTTPException(
                status_code=500,
                detail="Invalid fare prediction generated."
            )

    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Fare prediction failed."
        )

    # Return result

    return {

        "predicted_fare": round(fare, 2),

        "formatted_fare": f"₹{fare:,.0f}",

        "currency": "INR"

    }
