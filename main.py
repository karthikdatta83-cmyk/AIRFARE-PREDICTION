```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import calendar

app = FastAPI()

# CORS Configuration
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

# Load ML Model and Preprocessor
model = joblib.load("flight_model.pkl")
preprocessor = joblib.load("preprocessor.pkl")


# Valid values extracted from Data_Train.xlsx

VALID_AIRLINES = {
    "Air Asia",
    "Air India",
    "GoAir",
    "IndiGo",
    "Jet Airways",
    "Jet Airways Business",
    "Multiple carriers",
    "Multiple carriers Premium economy",
    "SpiceJet",
    "Trujet",
    "Vistara",
    "Vistara Premium economy"
}

VALID_SOURCES = {
    "Banglore",
    "Chennai",
    "Delhi",
    "Kolkata",
    "Mumbai"
}

VALID_DESTINATIONS = {
    "Banglore",
    "Cochin",
    "Delhi",
    "Hyderabad",
    "Kolkata",
    "New Delhi"
}

VALID_PAIRS = {
    ("Banglore", "Delhi"),
    ("Banglore", "New Delhi"),
    ("Chennai", "Kolkata"),
    ("Delhi", "Cochin"),
    ("Kolkata", "Banglore"),
    ("Mumbai", "Hyderabad")
}

VALID_INFO = {
    "1 Long layover",
    "1 Short layover",
    "2 Long layover",
    "Business class",
    "Change airports",
    "In-flight meal not included",
    "No Info",
    "No check-in baggage included",
    "No info",
    "Red-eye flight"
}

VALID_ROUTES = {
    'BLR → AMD → DEL',
    'BLR → BBI → DEL',
    'BLR → BDQ → DEL',
    'BLR → BOM → AMD → DEL',
    'BLR → BOM → BHO → DEL',
    'BLR → BOM → DEL',
    'BLR → BOM → IDR → DEL',
    'BLR → BOM → IDR → GWL → DEL',
    'BLR → BOM → IXC → DEL',
    'BLR → BOM → JDH → DEL',
    'BLR → BOM → NAG → DEL',
    'BLR → BOM → UDR → DEL',
    'BLR → CCU → BBI → DEL',
    'BLR → CCU → BBI → HYD → DEL',
    'BLR → CCU → BBI → HYD → VGA → DEL',
    'BLR → CCU → DEL',
    'BLR → CCU → GAU → DEL',
    'BLR → COK → DEL',
    'BLR → DEL',
    'BLR → GAU → DEL',
    'BLR → GOI → DEL',
    'BLR → HBX → BOM → AMD → DEL',
    'BLR → HBX → BOM → BHO → DEL',
    'BLR → HBX → BOM → NAG → DEL',
    'BLR → HYD → DEL',
    'BLR → HYD → VGA → DEL',
    'BLR → IDR → DEL',
    'BLR → LKO → DEL',
    'BLR → MAA → DEL',
    'BLR → NAG → DEL',
    'BLR → PNQ → DEL',
    'BLR → STV → DEL',
    'BLR → TRV → COK → DEL',
    'BLR → VGA → DEL',
    'BLR → VGA → HYD → DEL',
    'BLR → VGA → VTZ → DEL',
    'BOM → AMD → ISK → HYD',
    'BOM → BBI → HYD',
    'BOM → BDQ → DEL → HYD',
    'BOM → BHO → DEL → HYD',
    'BOM → BLR → CCU → BBI → HYD',
    'BOM → BLR → HYD',
    'BOM → CCU → HYD',
    'BOM → COK → MAA → HYD',
    'BOM → DED → DEL → HYD',
    'BOM → DEL → HYD',
    'BOM → GOI → HYD',
    'BOM → GOI → PNQ → HYD',
    'BOM → HYD',
    'BOM → IDR → DEL → HYD',
    'BOM → JAI → DEL → HYD',
    'BOM → JDH → DEL → HYD',
    'BOM → JDH → JAI → DEL → HYD',
    'BOM → JLR → HYD',
    'BOM → MAA → HYD',
    'BOM → NDC → HYD',
    'BOM → RPR → VTZ → HYD',
    'BOM → UDR → DEL → HYD',
    'BOM → VNS → DEL → HYD',
    'CCU → AMD → BLR',
    'CCU → BBI → BLR',
    'CCU → BBI → BOM → BLR',
    'CCU → BBI → HYD → BLR',
    'CCU → BBI → IXR → DEL → BLR',
    'CCU → BLR',
    'CCU → BOM → AMD → BLR',
    'CCU → BOM → BLR',
    'CCU → BOM → COK → BLR',
    'CCU → BOM → GOI → BLR',
    'CCU → BOM → HBX → BLR',
    'CCU → BOM → PNQ → BLR',
    'CCU → BOM → TRV → BLR',
    'CCU → DEL → AMD → BLR',
    'CCU → DEL → BLR',
    'CCU → DEL → COK → BLR',
    'CCU → DEL → COK → TRV → BLR',
    'CCU → DEL → VGA → BLR',
    'CCU → GAU → BLR',
    'CCU → GAU → DEL → BLR',
    'CCU → GAU → IMF → DEL → BLR',
    'CCU → HYD → BLR',
    'CCU → IXA → BLR',
    'CCU → IXB → BLR',
    'CCU → IXB → DEL → BLR',
    'CCU → IXR → BBI → BLR',
    'CCU → IXR → DEL → BLR',
    'CCU → IXZ → MAA → BLR',
    'CCU → JAI → BOM → BLR',
    'CCU → JAI → DEL → BLR',
    'CCU → KNU → BLR',
    'CCU → MAA → BLR',
    'CCU → NAG → BLR',
    'CCU → PAT → BLR',
    'CCU → PNQ → BLR',
    'CCU → RPR → HYD → BLR',
    'CCU → VNS → DEL → BLR',
    'CCU → VTZ → BLR',
    'DEL → AMD → BOM → COK',
    'DEL → AMD → COK',
    'DEL → ATQ → BOM → COK',
    'DEL → BBI → COK',
    'DEL → BDQ → BOM → COK',
    'DEL → BHO → BOM → COK',
    'DEL → BLR → COK',
    'DEL → BOM → COK',
    'DEL → CCU → BOM → COK',
    'DEL → COK',
    'DEL → DED → BOM → COK',
    'DEL → GOI → BOM → COK',
    'DEL → GWL → IDR → BOM → COK',
    'DEL → HYD → BOM → COK',
    'DEL → HYD → COK',
    'DEL → HYD → MAA → COK',
    'DEL → IDR → BOM → COK',
    'DEL → IXC → BOM → COK',
    'DEL → IXU → BOM → COK',
    'DEL → JAI → BOM → COK',
    'DEL → JDH → BOM → COK',
    'DEL → LKO → BOM → COK',
    'DEL → LKO → COK',
    'DEL → MAA → BOM → COK',
    'DEL → MAA → COK',
    'DEL → NAG → BOM → COK',
    'DEL → PNQ → COK',
    'DEL → RPR → NAG → BOM → COK',
    'DEL → TRV → COK',
    'DEL → UDR → BOM → COK',
    'MAA → CCU'
}


# Request Model
class FlightDetails(BaseModel):
    Airline: str
    Source: str
    Destination: str
    Route: str
    Additional_Info: str

    Duration: int
    Total_Stops: int
    Journey_Day: int
    Journey_Month: int
    Dep_Hour: int
    Dep_Minute: int
    Arrival_Hour: int
    Arrival_Minute: int


# Home
@app.get("/")
def home():
    return {
        "message": "Airfare Prediction API is running"
    }


# About
@app.get("/about")
def about():
    return {
        "project": "Airfare Price Prediction",
        "model": "Random Forest Regression"
    }


# Prediction
@app.post("/predict")
def predict_fare(flight: FlightDetails):

    # Airline validation
    if flight.Airline not in VALID_AIRLINES:
        raise HTTPException(
            status_code=400,
            detail="Invalid airline selected."
        )

    # Source validation
    if flight.Source not in VALID_SOURCES:
        raise HTTPException(
            status_code=400,
            detail="Invalid source city."
        )

    # Destination validation
    if flight.Destination not in VALID_DESTINATIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid destination city."
        )

    # Source and destination combination
    if (flight.Source, flight.Destination) not in VALID_PAIRS:
        raise HTTPException(
            status_code=400,
            detail="This source and destination combination is not available in the dataset."
        )

    # Same city validation
    if flight.Source == flight.Destination:
        raise HTTPException(
            status_code=400,
            detail="Source and destination cannot be the same."
        )

    # Route validation
    route = flight.Route.strip()

    if route not in VALID_ROUTES:
        raise HTTPException(
            status_code=400,
            detail="Invalid route. Please enter a route from the training dataset."
        )

    # Route endpoint validation
    airport_codes = {
        "Banglore": "BLR",
        "Chennai": "MAA",
        "Delhi": "DEL",
        "Kolkata": "CCU",
        "Mumbai": "BOM",
        "Cochin": "COK",
        "Hyderabad": "HYD",
        "New Delhi": "DEL"
    }

    route_parts = [part.strip() for part in route.split("→")]

    if (
        route_parts[0] != airport_codes[flight.Source]
        or route_parts[-1] != airport_codes[flight.Destination]
    ):
        raise HTTPException(
            status_code=400,
            detail="Route does not match the selected source and destination."
        )

    # Additional information validation
    if flight.Additional_Info not in VALID_INFO:
        raise HTTPException(
            status_code=400,
            detail="Invalid additional flight information."
        )

    # Stops validation
    if flight.Total_Stops not in range(5):
        raise HTTPException(
            status_code=400,
            detail="Total stops must be between 0 and 4."
        )

    # Route and stops consistency
    actual_stops = len(route_parts) - 2

    if flight.Total_Stops != actual_stops:
        raise HTTPException(
            status_code=400,
            detail="Total stops do not match the selected route."
        )

    # Duration validation (minutes)
    if not 5 <= flight.Duration <= 2860:
        raise HTTPException(
            status_code=400,
            detail="Duration must be between 5 and 2860 minutes."
        )

    # Journey day validation
    if not 1 <= flight.Journey_Day <= 31:
        raise HTTPException(
            status_code=400,
            detail="Journey day must be between 1 and 31."
        )

    # Journey month validation
    if not 1 <= flight.Journey_Month <= 12:
        raise HTTPException(
            status_code=400,
            detail="Journey month must be between 1 and 12."
        )

    max_day = calendar.monthrange(
        2020, flight.Journey_Month
    )[1]

    if flight.Journey_Day > max_day:
        raise HTTPException(
            status_code=400,
            detail="Invalid day for the selected month."
        )

    # Departure time validation
    if not 0 <= flight.Dep_Hour <= 23:
        raise HTTPException(
            status_code=400,
            detail="Departure hour must be between 0 and 23."
        )

    if not 0 <= flight.Dep_Minute <= 59:
        raise HTTPException(
            status_code=400,
            detail="Departure minute must be between 0 and 59."
        )

    # Arrival time validation
    if not 0 <= flight.Arrival_Hour <= 23:
        raise HTTPException(
            status_code=400,
            detail="Arrival hour must be between 0 and 23."
        )

    if not 0 <= flight.Arrival_Minute <= 59:
        raise HTTPException(
            status_code=400,
            detail="Arrival minute must be between 0 and 59."
        )

    # Prepare input data
    input_data = pd.DataFrame([flight.model_dump()])

    # Preprocessing
    processed_data = preprocessor.transform(input_data)

    # Prediction
    prediction = model.predict(processed_data)

    return {
        "predicted_fare": round(float(prediction[0]), 2)
    }
```
