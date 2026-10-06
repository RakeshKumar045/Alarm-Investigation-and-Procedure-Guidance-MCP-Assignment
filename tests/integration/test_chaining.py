from fastapi.testclient import TestClient

from alarm_api.main import app

client = TestClient(app)

AUTH = {"Authorization": "Bearer demo-token"}


def test_asset_to_alarm_to_priority_chain():
    assets_response = client.get(
        "/assets/search",
        params={"query": "Boiler Feed Pump 101"},
        headers=AUTH,
    )

    asset_id = assets_response.json()["results"][0]["asset_id"]

    alarms_response = client.get(
        "/alarms",
        params={"asset_id": asset_id},
        headers=AUTH,
    )

    alarm_id = alarms_response.json()["data"][0]["alarm_id"]

    priority_response = client.post(
        "/alarms/priority-score",
        json={"alarm_id": alarm_id},
        headers=AUTH,
    )

    assert priority_response.status_code == 200
    assert priority_response.json()["priority_score"] > 0
