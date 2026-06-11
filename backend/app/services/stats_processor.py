import pandas as pd
from datetime import date, datetime

import re
from sqlalchemy.orm import Session

from app.core.config import SRC_URL, RANK_FILTERS, build_stats_url
from app.schemas.schemas import STAT_FIELDS, STAT_OUTPUT_FIELDS
from app.services.fetcher import fetch_page
from app.services.extractor import extract_stats
from app.services.normalizer import normalize_df
from app.services.validator import validate_df
from app.db.repositories.stats import (
    get_stats_for_date,
    save_scrape_run_with_stats,
)


def has_valid_cached_stats(stats: dict | None) -> bool:
    if stats is None:
        return False

    heroes = stats.get("heroes") or []
    return len(heroes) > 0


def scrape_and_store_today_stats(db: Session) -> dict:
    today = date.today()

    print("Scraping MLBB stats...")
    html = fetch_page(SRC_URL)
    rows = extract_stats(html)

    print(f"Extracted rows: {len(rows)}")

    df_raw = pd.DataFrame(rows, columns=STAT_FIELDS)
    df_norm = normalize_df(df_raw)

    # Important: prevent duplicated scraped rows from causing all heroes to be rejected.
    df_norm = df_norm.drop_duplicates(subset=["hero"], keep="first")

    df_clean, df_issues = validate_df(df_norm)
    issue_count = int(len(df_issues))

    print(f"Clean rows: {len(df_clean)}")
    print(f"Issue count: {issue_count}")

    if not df_clean.empty and "lane" in df_clean.columns:
        print("Lane counts:")
        print(df_clean["lane"].value_counts(dropna=False).to_string())

    if df_clean.empty:
        raise RuntimeError(
            "Scrape produced 0 clean heroes. Not saving to DB. "
            f"Issue count: {issue_count}. "
            f"Issue sample: {df_issues.head(10).to_dict(orient='records')}"
        )

    save_scrape_run_with_stats(
        db=db,
        source=SRC_URL,
        scraped_for_date=today,
        df_clean=df_clean,
        issue_count=issue_count,
    )

    return {
        "date": today.isoformat(),
        "hero_count": int(len(df_clean)),
        "issue_count": issue_count,
        "heroes": df_clean.where(pd.notna(df_clean), None).to_dict(orient="records"),
    }


def ensure_today_stats(db: Session) -> dict:
    today = date.today()
    stats = get_stats_for_date(db, today)

    if has_valid_cached_stats(stats):
        print("Using valid cached stats from DB.")
        return stats

    print("No valid stats found for today. Scraping on startup...")
    return scrape_and_store_today_stats(db)


def fetch_stats_for_rank_filter(rank_filter: str) -> pd.DataFrame:
    url = build_stats_url(rank_filter)
    html = fetch_page(url)
    rows = extract_stats(html)
    
    for row in rows:
        row["rank_filter"] = rank_filter
    
    return pd.DataFrame(rows, columns=STAT_OUTPUT_FIELDS)


def fetch_all_rank_stats() -> pd.DataFrame:
    frames = []
    for rank_filter in RANK_FILTERS:
        df = fetch_stats_for_rank_filter(rank_filter=rank_filter)
        frames.append(df)

    return pd.concat(frames, ignore_index=True)


def cached_stats_have_rank_filter(stats: dict | None) -> bool:
    if stats is None:
        return False

    heroes = stats.get("heroes") or []

    if not heroes:
        return False

    return "rank_filter" in heroes[0]