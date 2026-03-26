# tests/test_api.py
import pytest
from app import create_app

VALID_PAYLOAD = {
    "sensor_id": "sensor-001",
    "timestamp": "2026-01-15T10:00:00Z",
    "metrics": {
        "temperature": 22.5,
        "humidity": 60.0
    }
}

@pytest.fixture
def client():
    """
    Questo setup crea un client di test Flask.
    Viene eseguita prima di ogni test che la richiede.
    Usa un DB in memoria (testing=True) così ogni test parte pulito.
    """
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client


# --- Test 1: inserimento con payload valido ---
def test_insert_valid_measure(client):
    response = client.post("/measures", json=VALID_PAYLOAD)
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data


# --- Test 2: inserimento con payload non valido ---
def test_insert_missing_sensor_id(client):
    payload = {**VALID_PAYLOAD, "sensor_id": None}
    response = client.post("/measures", json=payload)
    assert response.status_code == 400

def test_insert_missing_timestamp(client):
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "timestamp"}
    response = client.post("/measures", json=payload)
    assert response.status_code == 400

def test_insert_empty_metrics(client):
    payload = {**VALID_PAYLOAD, "metrics": {}}
    response = client.post("/measures", json=payload)
    assert response.status_code == 400

def test_insert_non_numeric_metric(client):
    payload = {**VALID_PAYLOAD, "metrics": {"temperature": "caldo"}}
    response = client.post("/measures", json=payload)
    assert response.status_code == 400


# --- Test 3: statistiche su dati noti ---
def test_stats_on_known_data(client):
    # Prima inseriamo dati noti
    client.post("/measures", json={
        "sensor_id": "sensor-test",
        "timestamp": "2026-01-01T10:00:00Z",
        "metrics": {"temperature": 10.0}
    })
    client.post("/measures", json={
        "sensor_id": "sensor-test",
        "timestamp": "2026-01-01T11:00:00Z",
        "metrics": {"temperature": 20.0}
    })
    client.post("/measures", json={
        "sensor_id": "sensor-test",
        "timestamp": "2026-01-01T12:00:00Z",
        "metrics": {"temperature": 30.0}
    })

    # Ora chiediamo le statistiche
    response = client.get("/stats?sensor_id=sensor-test&metric=temperature")
    assert response.status_code == 200

    stats = response.get_json()
    assert "temperature" in stats
    assert stats["temperature"]["min"] == 10.0
    assert stats["temperature"]["max"] == 30.0
    assert stats["temperature"]["avg"] == 20.0
    assert stats["temperature"]["count"] == 3