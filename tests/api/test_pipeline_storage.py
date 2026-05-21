from datetime import date

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db.db import Base
from backend.app.db.repositories.stats import save_scrape_run_with_stats
import backend.app.services.pipeline as pipeline


def make_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    return SessionLocal()


def test_pipeline_uses_existing_db_stats_without_fetching(monkeypatch):
    db = make_db()

    save_scrape_run_with_stats(
        db=db,
        source="mlbb.gg/statistics",
        scraped_for_date=date.today(),
        df_clean=pd.DataFrame([
            {
                "rank": 1,
                "lane": "Mid",
                "hero": "Cecilion",
                "tier": "S",
                "win_rate": 53.2,
                "ban_rate": 12.5,
                "pick_rate": 8.1,
                "roles": "Mage",
            }
        ]),
        issue_count=0,
    )

    monkeypatch.setattr(
        pipeline,
        "get_pipeline_plan",
        lambda user_query: {
            "task_type": "summarize_meta",
            "filters": {
                "lane": None,
                "hero": None,
                "min_win_rate": None,
                "max_win_rate": None,
                "min_pick_rate": None,
                "max_pick_rate": None,
                "min_ban_rate": None,
                "max_ban_rate": None,
                "top_n": 10,
            },
            "steps": [],
            "reasoning_summary": "test",
        },
    )

    monkeypatch.setattr(pipeline, "fetch_page", lambda url: pytest.fail("Should not fetch when DB stats exist."))

    monkeypatch.setattr(
        pipeline,
        "run_analyst",
        lambda user_query, df_clean, issue_count: {
            "headline": "Meta Watch",
            "key_findings": [],
            "meta_summary": "Cecilion is available from DB stats.",
            "caveats": [],
        },
    )

    events = list(pipeline.run_pipeline("summarize the current meta", db=db))
    step, message, result = events[-1]

    assert step == "done"
    assert result["hero_count"] == 1
    assert result["report_md"].startswith("# Meta Watch")