from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_respond_to_question():
    payload = {
        "question": "What is the Central Limit Theorem?"
    }
    response = client.post("/api/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "links" in data
    assert isinstance(data["links"], list)
