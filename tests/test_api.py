from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["service"] == "ticket-memory-rag"


def test_list_and_action():
    r = client.get("/api/memories")
    assert r.status_code == 200
    assert "memories" in r.json()

    r2 = client.post("/api/similar", json={"prompt": "smoke test"})
    assert r2.status_code == 200
    body = r2.json()
    assert body["ok"] is True
    assert "result" in body
