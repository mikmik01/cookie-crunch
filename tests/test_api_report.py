from fastapi.testclient import TestClient
from api.main import app

def test_report_endpoint_returns_latest(tmp_path, monkeypatch):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()

    older = reports_dir / "report_2026-05-08_100000.md"
    newer = reports_dir / "report_2026-05-08_110000.md"

    older.write_text("# Old Report\n\nOld content", encoding="utf-8")
    newer.write_text("# Latest Report\n\nLatest content", encoding="utf-8")

    monkeypatch.setattr(api, "REPORT_DIR", reports_dir)

    client = TestClient(api.app)

    response = client.post(
        "/api/report",
        json={"query": "summarize the current meta"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["query"] == "summarize the current meta"
    assert body["filename"] == "report_2026-05-08_110000.md"
    assert body["report"].startswith("# Latest Report")
    assert "Latest content" in body["report"]

def test_report_endpoint_returns_404(tmp_path, monkeypatch):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()

    monkeypatch.setattr(api, "REPORT_DIR", reports_dir)

    client = TestClient(api.app)

    response = client.post(
        "/api/report",
        json={"query": "summarize the current meta"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "No local reports found."
