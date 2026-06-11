import pandas as pd

from datetime import date
from sqlalchemy.orm import Session

from app.core.config import SRC_URL
from app.schemas.schemas import STAT_FIELDS
from app.services.fetcher import fetch_pages_by_rank
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
    pages_by_rank = fetch_pages_by_rank(SRC_URL)

    print("Fetched rank filters:")
    for rank_filter in pages_by_rank:
        print(rank_filter)

    rows = []

    for rank_filter, html in pages_by_rank.items():
        print(f"Extracting stats for rank filter: {rank_filter}")
        extracted = extract_stats(html, rank_filter=rank_filter)
        print(f"{rank_filter}: {len(extracted)} rows")
        rows.extend(extracted)

    print(f"Extracted rows: {len(rows)}")

    df_raw = pd.DataFrame(rows, columns=STAT_FIELDS)

    print("Raw columns:", df_raw.columns.tolist())

    if not df_raw.empty and "rank_filter" in df_raw.columns:
        print("Raw rank filter counts:")
        print(df_raw["rank_filter"].value_counts(dropna=False).to_string())

    df_norm = normalize_df(df_raw)

    if not df_norm.empty and "rank_filter" in df_norm.columns:
        print("Normalized rank filter counts before dedupe:")
        print(df_norm["rank_filter"].value_counts(dropna=False).to_string())

    df_norm = df_norm.drop_duplicates(
        subset=["rank_filter", "hero"],
        keep="first",
    )

    if not df_norm.empty and "rank_filter" in df_norm.columns:
        print("Normalized rank filter counts after dedupe:")
        print(df_norm["rank_filter"].value_counts(dropna=False).to_string())

    df_clean, df_issues = validate_df(df_norm)
    issue_count = int(len(df_issues))

    print(f"Clean rows: {len(df_clean)}")
    print(f"Issue count: {issue_count}")

    if not df_clean.empty and "rank_filter" in df_clean.columns:
        print("Clean rank filter counts:")
        print(df_clean["rank_filter"].value_counts(dropna=False).to_string())

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


def ensure_today_stats(db: Session) -> dict:
    today = date.today()
    stats = get_stats_for_date(db, today)

    if has_valid_cached_stats(stats):
        print("Using valid cached stats from DB.")
        return stats

    print("No valid stats found for today. Scraping on startup...")
    return scrape_and_store_today_stats(db)


def cached_stats_have_rank_filter(stats: dict | None) -> bool:
    if stats is None:
        return False

    heroes = stats.get("heroes") or []

    if not heroes:
        return False

    return "rank_filter" in heroes[0]