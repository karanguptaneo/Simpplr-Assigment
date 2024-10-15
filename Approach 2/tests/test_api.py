from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ask_policy():
    response = client.post("/ask_policy/", json={"user_query": "How many personal leaves do I have?"})
    assert response.status_code == 200
    assert "response" in response.json()
    assert "sources" in response.json()
