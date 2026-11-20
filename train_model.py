"""
SkyFare — Machine Learning Model Training & Evaluation Pipeline
This script documents the complete data science pipeline used to clean,
preprocess, train, evaluate, and serialize the Airfare Prediction model.
"""

import os
import argparse
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


def create_preprocessor():
    """Build the ColumnTransformer for categorical and numerical features."""
    categorical_features = ['Airline', 'Source', 'Destination', 'Route', 'Additional_Info']
    numerical_features = [
        'Duration', 'Total_Stops', 'Journey_Day', 'Journey_Month',
        'Dep_Hour', 'Dep_Minute', 'Arrival_Hour', 'Arrival_Minute'
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=True), categorical_features),
            ('num', 'passthrough', numerical_features)
        ]
    )
    return preprocessor


def clean_flight_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess and engineer features from raw flight dataset."""
    df = df.copy()

    # Drop missing values
    df.dropna(inplace=True)

    # Clean stops mapping if string
    if df['Total_Stops'].dtype == object:
        stops_map = {
            'non-stop': 0,
            '1 stop': 1,
            '2 stops': 2,
            '3 stops': 3,
            '4 stops': 4
        }
        df['Total_Stops'] = df['Total_Stops'].map(stops_map).fillna(0).astype(int)

    # Parse Date of Journey if needed
    if 'Date_of_Journey' in df.columns:
        df['Journey_Day'] = pd.to_datetime(df['Date_of_Journey'], format='%d/%m/%Y').dt.day
        df['Journey_Month'] = pd.to_datetime(df['Date_of_Journey'], format='%d/%m/%Y').dt.month

    # Parse Dep_Time if needed
    if 'Dep_Time' in df.columns and df['Dep_Time'].dtype == object:
        df['Dep_Hour'] = pd.to_datetime(df['Dep_Time'], format='%H:%M').dt.hour
        df['Dep_Minute'] = pd.to_datetime(df['Dep_Time'], format='%H:%M').dt.minute

    # Parse Arrival_Time if needed
    if 'Arrival_Time' in df.columns and df['Arrival_Time'].dtype == object:
        df['Arrival_Hour'] = pd.to_datetime(df['Arrival_Time'].str.split(' ').str[0], format='%H:%M').dt.hour
        df['Arrival_Minute'] = pd.to_datetime(df['Arrival_Time'].str.split(' ').str[0], format='%H:%M').dt.minute

    # Normalize Additional_Info
    if 'Additional_Info' in df.columns:
        df['Additional_Info'] = df['Additional_Info'].replace({'No Info': 'No info'})

    return df


def generate_sample_training_data(n_samples: int = 500) -> pd.DataFrame:
    """Generate realistic demonstration flight data for testing the pipeline."""
    np.random.seed(42)
    airlines = ['IndiGo', 'Air India', 'Jet Airways', 'SpiceJet', 'Multiple carriers', 'GoAir', 'Vistara', 'Air Asia']
    pairs = [
        ('Delhi', 'Cochin', 'DEL → BOM → COK', 1, 160),
        ('Banglore', 'New Delhi', 'BLR → DEL', 0, 170),
        ('Mumbai', 'Hyderabad', 'BOM → HYD', 0, 85),
        ('Kolkata', 'Banglore', 'CCU → DEL → BLR', 1, 310),
        ('Chennai', 'Kolkata', 'MAA → CCU', 0, 135)
    ]

    records = []
    for _ in range(n_samples):
        carrier = np.random.choice(airlines)
        src, dst, route, stops, base_dur = pairs[np.random.choice(len(pairs))]
        dur = int(base_dur + np.random.randint(-15, 45))
        j_day = np.random.randint(1, 29)
        j_month = np.random.choice([3, 4, 5, 6])
        dep_h = np.random.randint(5, 23)
        dep_m = np.random.choice([0, 15, 30, 45])
        arr_h = (dep_h + (dur // 60)) % 24
        arr_m = (dep_m + (dur % 60)) % 60

        # Base price formula
        price = 3000 + (dur * 18) + (stops * 1800)
        if 'Jet Airways' in carrier:
            price += 3500
        elif carrier in ['IndiGo', 'SpiceJet', 'Air Asia']:
            price -= 600
        price += np.random.normal(0, 400)

        records.append({
            'Airline': carrier,
            'Source': src,
            'Destination': dst,
            'Route': route,
            'Additional_Info': 'No info',
            'Duration': dur,
            'Total_Stops': stops,
            'Journey_Day': j_day,
            'Journey_Month': j_month,
            'Dep_Hour': dep_h,
            'Dep_Minute': dep_m,
            'Arrival_Hour': arr_h,
            'Arrival_Minute': arr_m,
            'Price': max(1800.0, round(price, 2))
        })

    return pd.DataFrame(records)


def train_and_evaluate(data_path: str = None, save_artifacts: bool = False):
    """Execute model training and evaluation."""
    print("=" * 60)
    print("SkyFare — Model Training & Evaluation Pipeline")
    print("=" * 60)

    if data_path and os.path.exists(data_path):
        print(f"Loading dataset from: {data_path}")
        if data_path.endswith('.xlsx') or data_path.endswith('.xls'):
            df = pd.read_excel(data_path)
        else:
            df = pd.read_csv(data_path)
        df = clean_flight_data(df)
    else:
        print("No raw dataset path provided. Running demonstration pipeline with synthesized flight data...")
        df = generate_sample_training_data(1000)

    print(f"Dataset shape: {df.shape}")

    feature_cols = [
        'Airline', 'Source', 'Destination', 'Route', 'Additional_Info',
        'Duration', 'Total_Stops', 'Journey_Day', 'Journey_Month',
        'Dep_Hour', 'Dep_Minute', 'Arrival_Hour', 'Arrival_Minute'
    ]
    target_col = 'Price'

    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Training set: {X_train.shape[0]} samples | Test set: {X_test.shape[0]} samples")

    print("\n1. Fitting Feature Preprocessor (ColumnTransformer)...")
    preprocessor = create_preprocessor()
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    n_features = X_train_processed.shape[1]
    print(f"-> Generated {n_features} total features after encoding.")

    print("\n2. Training Random Forest Regressor (100 Trees)...")
    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_processed, y_train)

    print("\n3. Evaluating Model Performance...")
    y_pred = model.predict(X_test_processed)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)

    print(f"  • R² Score:               {r2:.4f}")
    print(f"  • Root Mean Squared Error: ₹{rmse:.2f}")
    print(f"  • Mean Absolute Error:     ₹{mae:.2f}")

    if save_artifacts:
        print("\n4. Serializing Artifacts...")
        joblib.dump(preprocessor, "preprocessor.pkl")
        joblib.dump(model, "flight_model.pkl")
        print("-> Saved preprocessor.pkl and flight_model.pkl successfully!")

    print("=" * 60)
    print("Training Pipeline Execution Completed Successfully.")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train SkyFare ML Model")
    parser.add_argument("--data", type=str, default=None, help="Path to raw dataset (CSV or Excel)")
    parser.add_argument("--save", action="store_true", help="Save serialized pkl artifacts")
    args = parser.parse_args()

    train_and_evaluate(data_path=args.data, save_artifacts=args.save)
