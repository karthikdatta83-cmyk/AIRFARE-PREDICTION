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
    version="2.0"
)


# ==========================================
# 2. CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://airfare-price-estimation-z3wm.onrender.com"
    ],
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
# 4. EXTRACT VALID CATEGORIES FROM PREPROCESSOR
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

            if transformer == "drop" or transformer == "passthrough":
                continue

            categories_dict.update(
                extract_categories(
                    transformer,
                    selected_columns
                )
            )

    return categories_dict


VALID_CATEGORIES = extract_categories(preprocessor)


# Check that categorical validation is available.

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
            f"Could not extract valid categories for {field} "
            "from preprocessor.pkl. Check your trained preprocessor."
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

    Duration: int = Field(ge=1, le=2860)

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
# 8. VALIDATE FLIGHT INPUT
# ==========================================

def validate_flight(flight):

    # --------------------------------------
    # Airline validation
    # --------------------------------------

    if flight.Airline not in VALID_CATEGORIES["Airline"]:

        raise HTTPException(
            status_code=400,
            detail=f"Invalid airline: {flight.Airline}"
        )


    # --------------------------------------
    # Source validation
    # --------------------------------------

    if flight.Source not in VALID_CATEGORIES["Source"]:

        raise HTTPException(
            status_code=400,
            detail=f"Invalid source: {flight.Source}"
        )


    # --------------------------------------
    # Destination validation
    # --------------------------------------

    if flight.Destination not in VALID_CATEGORIES["Destination"]:

        raise HTTPException(
            status_code=400,
            detail=f"Invalid destination: {flight.Destination}"
        )


    # --------------------------------------
    # Same city validation
    # --------------------------------------

    if flight.Source == flight.Destination:

        raise HTTPException(
            status_code=400,
            detail="Source and destination cannot be the same."
        )


    # --------------------------------------
    # Additional information validation
    # --------------------------------------

    if flight.Additional_Info not in VALID_CATEGORIES["Additional_Info"]:

        raise HTTPException(
            status_code=400,
            detail="Invalid additional flight information."
        )


    # --------------------------------------
    # Route validation
    # --------------------------------------

    route = normalize_route(flight.Route)

    if route not in VALID_CATEGORIES["Route"]:

        raise HTTPException(
            status_code=400,
            detail=f"Invalid route: {flight.Route}"
        )


    # --------------------------------------
    # Route endpoint validation
    # --------------------------------------

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


    # --------------------------------------
    # Stop validation
    # --------------------------------------

    actual_stops = len(route_parts) - 2

    if flight.Total_Stops != actual_stops:

        raise HTTPException(
            status_code=400,
            detail="Number of stops does not match the selected route."
        )


    # --------------------------------------
    # Date validation
    # --------------------------------------

    max_day = calendar.monthrange(
        2021,
        flight.Journey_Month
    )[1]

    if flight.Journey_Day > max_day:

        raise HTTPException(
            status_code=400,
            detail="Invalid day for the selected month."
        )


    # --------------------------------------
    # Duration validation
    # --------------------------------------

    if not 5 <= flight.Duration <= 2860:

        raise HTTPException(
            status_code=400,
            detail="Flight duration must be between 5 and 2860 minutes."
        )


# ==========================================
# 9. HOME ENDPOINT
# ==========================================

@app.get("/")
def home():

    return {
        "message": "SkyFare Airfare Prediction API is running",
        "status": "success"
    }


# ==========================================
# 10. VERSION ENDPOINT
# ==========================================

@app.get("/version")
def version():

    return {
        "version": "validation-v2",
        "validation_enabled": True
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
# 12. PREDICTION ENDPOINT
# ==========================================

@app.post("/predict")
def predict_fare(flight: FlightDetails):

    # Step 1: Validate all inputs

    validate_flight(flight)


    # Step 2: Prepare input data

    input_data = pd.DataFrame([
        flight.model_dump()
    ])

    # Ensure the normalized route is used

    input_data["Route"] = normalize_route(flight.Route)


    # Step 3: Preprocess input

    try:

        processed_data = preprocessor.transform(input_data)

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=f"Unable to process flight details: {str(e)}"
        )


    # Step 4: Predict fare

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


    # Step 5: Return prediction

    return {

        "predicted_fare": round(fare, 2),

        "formatted_fare": f"₹{fare:,.0f}",

        "currency": "INR"

    }
