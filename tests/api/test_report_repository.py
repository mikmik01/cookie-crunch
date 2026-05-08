import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

from api.db import Base
from api.repositories.reports import save_query_report, get_report_by_id, list_reports


def make_db():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_save_and_load_query_report():
    db = make_db()

    result = {
        "report_id": "report_2026-05-08_120000",
        "query": "summarize the current meta",
        "plan": {"task_type": "summarize_meta"},
        "analyst_output": {"headline": "Meta Watch"},
        "report_md": "# Meta Watch\n\nReport body.",
        "hero_count": 10,
        "issue_count": 1,
    }

    saved = save_query_report(db, result)
    loaded = get_report_by_id(db, saved.id)

    assert loaded is not None
    assert loaded.id == "report_2026-05-08_120000"
    assert loaded.query == "summarize the current meta"
    assert json.loads(loaded.plan_json)["task_type"] == "summarize_meta"
    assert json.loads(loaded.analyst_output_json)["headline"] == "Meta Watch"
    assert loaded.report_md.startswith("# Meta Watch")
    assert loaded.hero_count == 10
    assert loaded.issue_count == 1


from datetime import datetime, timezone


def test_list_reports_returns_latest_first():
    db = make_db()

    save_query_report(db, {
        "report_id": "report_old",
        "query": "old query",
        "plan": {},
        "analyst_output": {},
        "report_md": "# Old",
        "hero_count": 1,
        "issue_count": 0,
        "generated_at": datetime(2026, 5, 8, 10, 0, 0, tzinfo=timezone.utc),
    })

    save_query_report(db, {
        "report_id": "report_new",
        "query": "new query",
        "plan": {},
        "analyst_output": {},
        "report_md": "# New",
        "hero_count": 2,
        "issue_count": 0,
        "generated_at": datetime(2026, 5, 8, 11, 0, 0, tzinfo=timezone.utc),
    })

    reports = list_reports(db)

    assert len(reports) == 2
    assert reports[0].id == "report_new"
    assert reports[1].id == "report_old"