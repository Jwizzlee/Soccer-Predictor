import pytest

from app.core.config import get_settings

pytestmark = pytest.mark.skipif(
    get_settings().use_mock_sports_data,
    reason="Live API tests require USE_MOCK_SPORTS_DATA=false and valid keys",
)


@pytest.fixture
def live_player_id(client):
    """Resolve a real player via search (Haaland / similar)."""
    response = client.get("/api/v1/players/search?q=Haaland&league_id=39")
    assert response.status_code == 200
    players = response.json()
    if not players:
        pytest.skip("No live players returned from API-Football")
    return players[0]["id"]


def test_predict_info(client):
    response = client.get("/api/v1/predict/info")
    assert response.status_code == 200
    data = response.json()
    assert data["endpoint"] == "POST /api/v1/predict"
    assert "mock_sports_data" in data


def test_predict_live_player(client, live_player_id):
    response = client.post(
        "/api/v1/predict",
        json={
            "player_id": live_player_id,
            "prop_type": "shots_on_target",
            "line": 1.5,
            "last_n_games": 5,
            "league_id": 39,
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["recommendation"] in ("OVER", "UNDER")
    assert 0 <= data["confidence"] <= 1
    assert data["supporting_stats"]["last_n"] >= 3
