import os, tempfile
from fastapi.testclient import TestClient

def test_api_smoke(monkeypatch):
    fd,path=tempfile.mkstemp(); os.close(fd)
    monkeypatch.setenv("ATLAS_DB",path)
    monkeypatch.setenv("ATLAS_DISABLE_SCHEDULER","1")
    from atlas import store
    store.DB_PATH=path
    from atlas.main import app
    with TestClient(app) as client:
        assert client.get("/api/health").json()["live_orders_enabled"] is False
        assert client.get("/api/signals").status_code==200
        assert client.get("/api/portfolio").json()["initial_balance"]==10000
        assert client.get("/api/performance").json()["trade_count"]==0
        assert len(client.get("/api/agents").json())==6
    os.unlink(path)
