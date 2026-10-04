from fastapi.testclient import TestClient
from ragobs.main import app

client = TestClient(app)


def test_summary():
    payload = client.post("/analyze", json={"rows": [{'pipeline': 'hybrid', 'hit': 1}, {'pipeline': 'hybrid', 'hit': 1}, {'pipeline': 'bm25', 'hit': 1}]}).json()
    assert payload["mean"] == 1.0
    assert payload["by_pipeline"]["hybrid"]


def test_empty_is_refused():
    assert client.post("/analyze", json={"rows": []}).status_code == 422
