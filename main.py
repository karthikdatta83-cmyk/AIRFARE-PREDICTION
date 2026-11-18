from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://airfare-price-estimation-z3wm.onrender.com/predictor"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Load trained model and preprocessor
model = joblib.load("flight_model.pkl")
preprocessor = joblib.load("preprocessor.pkl")


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


@app.get("/")
def home():
    return {"message": "Airfare Prediction API is running"}


@app.get("/about")
def about():
    return {
        "project": "Airfare Price Prediction",
        "model": "Random Forest Regression"
    }


@app.post("/predict")
def predict_fare(flight: FlightDetails):

    input_data = pd.DataFrame([flight.model_dump()])

    processed_data = preprocessor.transform(input_data)

    prediction = model.predict(processed_data)

    return {
        "predicted_fare": round(float(prediction[0]), 2)
    }
