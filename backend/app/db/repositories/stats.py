from datetime import date, datetime, timezone
from math import isnan
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session, selectinload

from backend.app.models.models_db import HeroStatRow, ScrapeRun


def _none_if_nan(value: Any):
    if value is None:
        return None

    if isinstance(value, float) and isnan(value):
        return None

    if pd.isna(value):
        return None

    return value


def save_scrape_run_with_stats(
    db: Session,
    source: str,
    scraped_for_date: date,
    df_clean: pd.DataFrame,
    issue_count: int,
) -> ScrapeRun:
    scrape_run = ScrapeRun(
        source=source,
        scraped_for_date=scraped_for_date,
        finished_at=datetime.now(timezone.utc),
        status="success",
        hero_count=int(len(df_clean)),
        issue_count=int(issue_count),
    )

    for row in df_clean.to_dict(orient="records"):
        scrape_run.hero_stats.append(
            HeroStatRow(
                hero=str(row["hero"]),
                rank=_none_if_nan(row.get("rank")),
                lane=_none_if_nan(row.get("lane")),
                tier=_none_if_nan(row.get("tier")),
                win_rate=_none_if_nan(row.get("win_rate")),
                ban_rate=_none_if_nan(row.get("ban_rate")),
                pick_rate=_none_if_nan(row.get("pick_rate")),
                roles=_none_if_nan(row.get("roles")),
            )
        )

    db.add(scrape_run)
    db.commit()
    db.refresh(scrape_run)

    return scrape_run


def _scrape_run_to_response(scrape_run: ScrapeRun) -> dict:
    heroes = sorted(
        scrape_run.hero_stats,
        key=lambda row: row.rank if row.rank is not None else 999999,
    )

    return {
        "date": scrape_run.scraped_for_date.isoformat(),
        "hero_count": scrape_run.hero_count,
        "issue_count": scrape_run.issue_count,
        "heroes": [
            {
                "rank": row.rank,
                "lane": row.lane,
                "hero": row.hero,
                "tier": row.tier,
                "win_rate": row.win_rate,
                "ban_rate": row.ban_rate,
                "pick_rate": row.pick_rate,
                "roles": row.roles,
            }
            for row in heroes
        ],
    }


def get_stats_for_date(db: Session, target_date: date) -> dict | None:
    scrape_run = (
        db.query(ScrapeRun)
        .options(selectinload(ScrapeRun.hero_stats))
        .filter(ScrapeRun.scraped_for_date == target_date)
        .order_by(ScrapeRun.finished_at.desc(), ScrapeRun.started_at.desc())
        .first()
    )

    if scrape_run is None:
        return None

    return _scrape_run_to_response(scrape_run)


def get_latest_stats(db: Session) -> dict | None:
    scrape_run = (
        db.query(ScrapeRun)
        .options(selectinload(ScrapeRun.hero_stats))
        .order_by(
            ScrapeRun.scraped_for_date.desc(),
            ScrapeRun.finished_at.desc(),
            ScrapeRun.started_at.desc(),
        )
        .first()
    )

    if scrape_run is None:
        return None

    return _scrape_run_to_response(scrape_run)