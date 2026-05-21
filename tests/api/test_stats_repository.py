from datetime import date

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db.db import Base
from backend.app.db.repositories.stats import (
    save_scrape_run_with_stats,
    get_latest_stats,
    get_stats_for_date,
)


def make_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def sample_clean_stats():
    return pd.DataFrame([
        {
            "rank": 1,
            "lane": "Mid",
            "hero": "Cecilion",
            "tier": "S",
            "win_rate": 53.2,
            "ban_rate": 12.5,
            "pick_rate": 8.1,
            "roles": "Mage",
        },
        {
            "rank": 2,
            "lane": "Gold",
            "hero": "Granger",
            "tier": "A",
            "win_rate": 51.0,
            "ban_rate": 20.0,
            "pick_rate": 10.0,
            "roles": "Marksman",
        },
    ])


def test_save_scrape_run_with_stats_and_load_by_date():
    db = make_db()

    save_scrape_run_with_stats(
        db=db,
        source="mlbb.gg/statistics",
        scraped_for_date=date(2026, 5, 8),
        df_clean=sample_clean_stats(),
        issue_count=1,
    )

    stats = get_stats_for_date(db, date(2026, 5, 8))

    assert stats is not None
    assert stats["date"] == "2026-05-08"
    assert stats["hero_count"] == 2
    assert stats["issue_count"] == 1
    assert stats["heroes"][0]["hero"] == "Cecilion"
    assert stats["heroes"][0]["win_rate"] == 53.2
    assert stats["heroes"][1]["hero"] == "Granger"


def test_get_latest_stats_returns_most_recent_scrape_date():
    db = make_db()

    save_scrape_run_with_stats(
        db=db,
        source="mlbb.gg/statistics",
        scraped_for_date=date(2026, 5, 7),
        df_clean=sample_clean_stats(),
        issue_count=0,
    )

    newer_df = sample_clean_stats()
    newer_df.loc[0, "hero"] = "Lylia"

    save_scrape_run_with_stats(
        db=db,
        source="mlbb.gg/statistics",
        scraped_for_date=date(2026, 5, 8),
        df_clean=newer_df,
        issue_count=2,
    )

    stats = get_latest_stats(db)

    assert stats is not None
    assert stats["date"] == "2026-05-08"
    assert stats["issue_count"] == 2
    assert stats["heroes"][0]["hero"] == "Lylia"