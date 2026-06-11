from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.db import Base
import app.services.pipeline as pipeline


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
    fake_stats = {
        "heroes": [
            {
                "rank": 1,
                "lane": "Mid",
                "hero": "Alice",
                "tier": "S",
                "win_rate": 53.2,
                "ban_rate": 12.1,
                "pick_rate": 8.4,
                "roles": "Mage",
            }
        ],
        "issue_count": 0,
    }

    monkeypatch.setattr(
        pipeline,
        "get_stats_for_date",
        lambda db, today: fake_stats,
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
                "top_n": 5,
            },
            "steps": [],
            "reasoning_summary": "test plan",
        },
    )

    events = list(pipeline.run_pipeline("strongest heroes", db=None))

    step, message, result = events[-1]

    assert step == "done"
    assert result["recommendations"][0]["hero"] == "Alice"