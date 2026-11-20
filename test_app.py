import pytest
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["preprocessor_loaded"] is True


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()


def test_about():
    response = client.get("/about")
    assert response.status_code == 200
    assert "project" in response.json()


def test_options_endpoint():
    response = client.get("/options")
    assert response.status_code == 200
    data = response.json()
    assert "airlines" in data
    assert "sources" in data
    assert "destinations" in data
    assert "additional_info" in data
    assert "routes" in data
    assert len(data["airlines"]) > 0
    assert len(data["sources"]) > 0
    assert len(data["routes"]) > 0


def test_predict_valid_flight():
    # Fetch valid route from options
    opts = client.get("/options").json()
    sample_route = opts["routes"][0]

    payload = {
        "Airline": "IndiGo",
        "Source": sample_route["source"],
        "Destination": sample_route["destination"],
        "Route": sample_route["route"],
        "Additional_Info": opts["additional_info"][0],
        "Duration": 150,
        "Total_Stops": sample_route["stops"],
        "Journey_Day": 15,
        "Journey_Month": 5,
        "Dep_Hour": 10,
        "Dep_Minute": 30,
        "Arrival_Hour": 13,
        "Arrival_Minute": 0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_fare" in data
    assert "formatted_fare" in data
    assert "currency" in data
    assert data["predicted_fare"] > 0
    assert data["currency"] == "INR"


def test_predict_arrow_normalization():
    opts = client.get("/options").json()
    # Find a 1-stop route
    one_stop_routes = [r for r in opts["routes"] if r["stops"] == 1]
    sample = one_stop_routes[0]

    payload_unicode = {
        "Airline": "IndiGo",
        "Source": sample["source"],
        "Destination": sample["destination"],
        "Route": sample["route"],
        "Additional_Info": opts["additional_info"][0],
        "Duration": 180,
        "Total_Stops": sample["stops"],
        "Journey_Day": 10,
        "Journey_Month": 4,
        "Dep_Hour": 9,
        "Dep_Minute": 0,
        "Arrival_Hour": 12,
        "Arrival_Minute": 0
    }
    r_uni = client.post("/predict", json=payload_unicode)
    assert r_uni.status_code == 200

    payload_ascii = payload_unicode.copy()
    payload_ascii["Route"] = sample["route"].replace("→", "->")
    r_ascii = client.post("/predict", json=payload_ascii)
    assert r_ascii.status_code == 200

    assert r_uni.json()["predicted_fare"] == r_ascii.json()["predicted_fare"]


def test_predict_validation_errors():
    opts = client.get("/options").json()
    sample = opts["routes"][0]

    # Invalid Airline
    payload_bad_airline = {
        "Airline": "NonExistentAirline",
        "Source": sample["source"],
        "Destination": sample["destination"],
        "Route": sample["route"],
        "Additional_Info": opts["additional_info"][0],
        "Duration": 150,
        "Total_Stops": sample["stops"],
        "Journey_Day": 15,
        "Journey_Month": 5,
        "Dep_Hour": 10,
        "Dep_Minute": 30,
        "Arrival_Hour": 13,
        "Arrival_Minute": 0
    }
    r1 = client.post("/predict", json=payload_bad_airline)
    assert r1.status_code == 400

    # Same Source and Destination
    payload_same_src_dst = payload_bad_airline.copy()
    payload_same_src_dst["Airline"] = "IndiGo"
    payload_same_src_dst["Destination"] = payload_same_src_dst["Source"]
    r2 = client.post("/predict", json=payload_same_src_dst)
    assert r2.status_code == 400

    # Pydantic duration validation failure (Duration = 0)
    payload_zero_dur = payload_bad_airline.copy()
    payload_zero_dur["Airline"] = "IndiGo"
    payload_zero_dur["Duration"] = 0
    r3 = client.post("/predict", json=payload_zero_dur)
    assert r3.status_code == 422
