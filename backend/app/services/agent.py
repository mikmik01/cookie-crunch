import pandas as pd

from app.core.config import CLEAN_DIR, PROCESSED_DIR, RAW_DIR, SRC_URL
from app.services.data_agent import run_data_agent
from app.services.extractor import extract_stats
from app.services.fetcher import fetch_pages_by_rank
from app.services.normalizer import normalize_df
from app.schemas.schemas import STAT_FIELDS
from app.utils.utils import (
    build_clean_csv_path,
    build_csv_path,
    build_issues_csv_path,
    current_timestamp,
    ensure_dir,
    get_today,
)
from app.services.validator import validate_df


def find_latest_csv_for_day(folder, prefix: str, day: str):
    matches = list(folder.glob(f"{prefix}_{day}_*.csv"))
    if not matches:
        return None
    return max(matches, key=lambda p: p.stat().st_mtime)


def load_or_create_clean_stats() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load today's cleaned stats, or fetch and build them if missing."""
    ensure_dir(CLEAN_DIR)
    ensure_dir(PROCESSED_DIR)
    ensure_dir(RAW_DIR)

    ts = current_timestamp()
    today = get_today()

    raw_csv = find_latest_csv_for_day(PROCESSED_DIR, "stats", today)
    clean_csv = find_latest_csv_for_day(CLEAN_DIR, "stats_cleaned", today)
    issues_csv = find_latest_csv_for_day(CLEAN_DIR, "stats_issues", today)

    if clean_csv is not None and issues_csv is not None:
        df_clean = pd.read_csv(clean_csv)
        try:
            df_issues = pd.read_csv(issues_csv)
        except pd.errors.EmptyDataError:
            df_issues = pd.DataFrame(
                columns=["row_index", "hero", "field", "issue", "value"]
            )
        return df_clean, df_issues

    if raw_csv is None:
        print(f"No stats found for {today}. fetching new stats for all rank divisions...")

        pages_by_rank = fetch_pages_by_rank(SRC_URL)

        rows = []

        for rank_filter, html in pages_by_rank.items():
            print(f"Extracting stats for {rank_filter}...")
            rows.extend(extract_stats(html, rank_filter=rank_filter))

        print("done!")

        df_raw = pd.DataFrame(rows, columns=STAT_FIELDS)
        raw_csv_path = build_csv_path(PROCESSED_DIR, ts)
        df_raw.to_csv(raw_csv_path, index=False, encoding="utf-8")
    else:
        raw_csv_path = raw_csv
    df_raw = pd.read_csv(raw_csv_path)

    df_norm = normalize_df(df_raw)
    df_clean, df_issues = validate_df(df_norm)

    clean_csv_path = build_clean_csv_path(CLEAN_DIR, ts)
    issues_csv_path = build_issues_csv_path(CLEAN_DIR, ts)

    df_clean.to_csv(clean_csv_path, index=False, encoding="utf-8")
    df_issues.to_csv(issues_csv_path, index=False, encoding="utf-8")

    return df_clean, df_issues


def answer_query(user_query: str, max_steps: int = 4) -> dict:
    df_clean, df_issues = load_or_create_clean_stats()

    agent_result = run_data_agent(
        user_query=user_query,
        df=df_clean,
        max_steps=max_steps,
    )

    return {
        "query": user_query,
        "answer": agent_result["answer"],
        "confidence": agent_result["confidence"],
        "observations": agent_result["observations"],
        "data": {
            "hero_count": int(len(df_clean)),
            "issue_count": int(len(df_issues)),
        },
    }