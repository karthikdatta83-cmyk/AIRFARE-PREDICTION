import pytest
from fastapi.testclient import TestClient
import main
import metadata

client = TestClient(main.app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["preprocessor_loaded"] is True
    assert data["n_estimators"] == 100


def test_api_metadata():
    response = client.get("/api/metadata")
    assert response.status_code == 200
    data = response.json()
    assert "airlines" in data
    assert "sources" in data
    assert "destinations" in data
    assert "valid_pairs" in data
    assert len(data["airlines"]) == 12
    assert "IndiGo" in data["airlines"]
    assert "Delhi" in data["sources"]


def test_api_routes():
    # Direct 0 stops
    r0 = client.get("/api/routes?source=Delhi&destination=Cochin&stops=0")
    assert r0.status_code == 200
    assert "DEL → COK" in r0.json()["routes"]

    # 1 stop
    r1 = client.get("/api/routes?source=Delhi&destination=Cochin&stops=1")
    assert r1.status_code == 200
    assert len(r1.json()["routes"]) > 0
    assert any("BOM" in route for route in r1.json()["routes"])


def test_predict_standard_flight():
    payload = {
        "Airline": "IndiGo",
        "Source": "Delhi",
        "Destination": "Cochin",
        "Route": "DEL → BOM → COK",
        "Additional_Info": "No info",
        "Duration": 150,
        "Total_Stops": 1,
        "Journey_Day": 25,
        "Journey_Month": 11,
        "Dep_Hour": 10,
        "Dep_Minute": 30,
        "Arrival_Hour": 13,
        "Arrival_Minute": 0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "predicted_fare" in data
    assert isinstance(data["predicted_fare"], float)
    assert data["predicted_fare"] > 0
    assert "fare_range" in data
    assert data["fare_range"]["min"] <= data["predicted_fare"] <= data["fare_range"]["max"]
    assert "confidence" in data
    assert "formatted_fare" in data
    assert data["flight_summary"]["route"] == "DEL → BOM → COK"


def test_predict_ascii_arrow_normalization():
    """Verify that user typing ascii -> produces the same prediction as unicode →."""
    payload_unicode = {
        "Airline": "IndiGo",
        "Source": "Delhi",
        "Destination": "Cochin",
        "Route": "DEL → BOM → COK",
        "Additional_Info": "No info",
        "Duration": 150,
        "Total_Stops": 1,
        "Journey_Day": 25,
        "Journey_Month": 11,
        "Dep_Hour": 10,
        "Dep_Minute": 30,
        "Arrival_Hour": 13,
        "Arrival_Minute": 0
    }
    r_unicode = client.post("/predict", json=payload_unicode)
    assert r_unicode.status_code == 200

    payload_ascii = payload_unicode.copy()
    payload_ascii["Route"] = "DEL -> BOM -> COK"
    r_ascii = client.post("/predict", json=payload_ascii)
    assert r_ascii.status_code == 200

    # Predictions must match exactly because route is normalized
    assert r_unicode.json()["predicted_fare"] == r_ascii.json()["predicted_fare"]
    assert r_ascii.json()["flight_summary"]["route"] == "DEL → BOM → COK"


def test_predict_auto_inferred_route():
    """Verify that omitting route auto-infers direct route."""
    payload = {
        "Airline": "SpiceJet",
        "Source": "Mumbai",
        "Destination": "Hyderabad",
        "Route": "",
        "Additional_Info": "No info",
        "Duration": 85,
        "Total_Stops": 0,
        "Journey_Day": 15,
        "Journey_Month": 12,
        "Dep_Hour": 14,
        "Dep_Minute": 20,
        "Arrival_Hour": 15,
        "Arrival_Minute": 45
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["flight_summary"]["route"] == "BOM → HYD"
    assert data["predicted_fare"] > 0


def test_predict_validation_errors():
    """Verify that invalid duration or stops return 422 Unprocessable Entity."""
    # Negative duration
    payload = {
        "Airline": "IndiGo",
        "Source": "Delhi",
        "Destination": "Cochin",
        "Duration": -50,
        "Total_Stops": 1,
        "Journey_Day": 25,
        "Journey_Month": 11,
        "Dep_Hour": 10,
        "Dep_Minute": 30,
        "Arrival_Hour": 13,
        "Arrival_Minute": 0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_metadata_route_helpers():
    assert metadata.normalize_route("del -> bom -> cok") == "DEL → BOM → COK"
    assert metadata.normalize_route("del to cok") == "DEL → COK"
    assert metadata.normalize_route("BLR-DEL") == "BLR → DEL"
    assert metadata.get_best_route("Delhi", "Cochin", 0) == "DEL → COK"
    assert metadata.get_best_route("Mumbai", "Hyderabad", 0) == "BOM → HYD"
    assert metadata.normalize_additional_info("no info") == "No info"
