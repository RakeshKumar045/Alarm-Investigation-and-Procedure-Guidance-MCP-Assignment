from fastapi.testclient import TestClient

from alarm_api.main import app

client = TestClient(app)

AUTH = {"Authorization": "Bearer demo-token"}


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_asset_search_requires_authentication():
    response = client.get(
        "/assets/search",
        params={"query": "Boiler Feed Pump 101"},
    )

    assert response.status_code == 401


def test_asset_search():
    response = client.get(
        "/assets/search",
        params={"query": "Boiler Feed Pump 101"},
        headers={"Authorization": "Bearer demo-token"},
    )

    assert response.status_code == 200
    assert response.json()["results"]




def test_trends_endpoint():
    response = client.post(
        "/alarms/trends",
        json={
            "asset_ids": ["asset-bfp-101"],
            "bucket": "daily",
            "metrics": ["alarm_count"],
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert "points" in response.json()


def test_flood_analysis_endpoint():
    response = client.post(
        "/alarms/flood-analysis",
        json={
            "unit": "Unit 1",
            "threshold_count": 1,
            "rolling_window_minutes": 10,
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert "flood_windows" in response.json()


def test_rationalization_endpoint():
    response = client.post(
        "/alarms/rationalization-candidates",
        json={
            "asset_ids": ["asset-bfp-101"],
            "recurrence_threshold": 5,
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert "candidates" in response.json()


def test_calculation_generate_and_execute():
    generate_response = client.post(
        "/calculation-code/generate",
        json={
            "calculation_type": "alarm_flood_index",
            "filters": {"unit": "Unit 1"},
        },
        headers=AUTH,
    )

    assert generate_response.status_code == 200

    calculation_id = generate_response.json()["calculation_id"]

    execute_response = client.post(
        "/calculation-code/execute",
        json={
            "calculation_id": calculation_id,
            "filters": {"unit": "Unit 1"},
        },
        headers=AUTH,
    )

    assert execute_response.status_code == 200
    assert execute_response.json()["status"] == "executed"


def test_kpi_definitions_endpoint():
    response = client.get(
        "/analytics/kpi-definitions",
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["definitions"]
