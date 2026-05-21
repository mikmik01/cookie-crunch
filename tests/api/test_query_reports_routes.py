from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db.db import Base, get_db
from backend.app.services.main import app
from backend.app.db.repositories.reports import get_report_by_id, save_query_report
from backend.app.routes import query as query_route


@pytest.fixture()
def client_and_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app), TestingSessionLocal

    app.dependency_overrides.clear()


def test_query_route_saves_pipeline_result_to_db(client_and_db, monkeypatch):
    client, TestingSessionLocal = client_and_db

    def fake_execute_pipeline(user_query: str, db):
        yield (
            "done",
            "Report ready.",
            {
                "report_id": "report_test_001",
                "query": user_query,
                "plan": {"task_type": "summarize_meta"},
                "analyst_output": {
                    "headline": "Meta Watch",
                    "key_findings": [
                        {
                            "claim": "Cecilion is strong.",
                            "evidence": "53.2% win rate.",
                            "confidence": "high",
                        }
                    ],
                    "meta_summary": "Scaling mages are performing well.",
                    "caveats": [],
                },
                "report_md": "# Meta Watch\n\nReport body.",
                "hero_count": 10,
                "issue_count": 1,
                "generated_at": datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc).isoformat(),
            },
        )

    monkeypatch.setattr(query_route, "execute_pipeline", fake_execute_pipeline)

    response = client.post("/query", json={"query": "summarize the current meta"})

    assert response.status_code == 200
    body = response.json()

    assert body["report_id"] == "report_test_001"
    assert body["report_md"].startswith("# Meta Watch")

    db = TestingSessionLocal()
    stored = get_report_by_id(db, "report_test_001")

    assert stored is not None
    assert stored.query == "summarize the current meta"
    assert stored.report_md.startswith("# Meta Watch")

    db.close()


def test_reports_routes_read_from_db(client_and_db):
    client, TestingSessionLocal = client_and_db

    db = TestingSessionLocal()

    save_query_report(db, {
        "report_id": "report_old",
        "query": "old query",
        "plan": {},
        "analyst_output": {},
        "report_md": "# Old",
        "hero_count": 1,
        "issue_count": 0,
        "generated_at": datetime(2026, 5, 8, 10, 0, tzinfo=timezone.utc),
    })

    save_query_report(db, {
        "report_id": "report_new",
        "query": "new query",
        "plan": {},
        "analyst_output": {},
        "report_md": "# New",
        "hero_count": 2,
        "issue_count": 0,
        "generated_at": datetime(2026, 5, 8, 11, 0, tzinfo=timezone.utc),
    })

    db.close()

    list_response = client.get("/reports")

    assert list_response.status_code == 200
    reports = list_response.json()["reports"]

    assert reports[0]["report_id"] == "report_new"
    assert reports[1]["report_id"] == "report_old"

    detail_response = client.get("/reports/report_new")

    assert detail_response.status_code == 200
    detail = detail_response.json()

    assert detail["report_id"] == "report_new"
    assert detail["content"] == "# New"