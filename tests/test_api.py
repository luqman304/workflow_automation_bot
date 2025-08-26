from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_summarize():
    r = client.post("/summarize", json={"text":"Action: email client. We discussed budget and timeline."})
    assert r.status_code == 200
    assert "summary" in r.json()

def test_actions():
    r = client.post("/actions", json={"text":"Action: send deck to client\nNext: schedule call"})
    assert r.status_code == 200
    body = r.json()["actions"]
    assert "Due:" in body
