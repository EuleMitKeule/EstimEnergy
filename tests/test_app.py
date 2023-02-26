
from fastapi.testclient import TestClient

from estimenergy.models import Settings
from estimenergy.dependencies import get_settings
from estimenergy.main import app


client = TestClient(app)


def get_settings_override():
    return Settings(

    )

app.dependency_overrides[get_settings] = get_settings_override


def test_app():
    response = client.get("/settings")
    data = response.json()
    assert data == {
        "glow_host": "localhost",
        "glow_port": 6053,
        "glow_password": ""
    }

