# import re
# import sys
# import os
# import pandas as pd
# from datetime import datetime
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from config import SRC_URL, CLEAN_DIR, PROCESSED_DIR, RAW_DIR, REPORT_DIR
# from fetcher import fetch_page
# from extractor import extract_stats
# from normalizer import normalize_df
# from planner import get_plan
# from validator import validate_df, validate_and_repair_plan
# from analyst import analyze_meta
# from report import build_report
# from schemas import STAT_FIELDS
# from ranker import rank_candidates
# from utils import (
#     build_csv_path,
#     build_clean_csv_path,
#     build_issues_csv_path,
#     current_timestamp,
#     ensure_dir,
#     get_today
# )

from datetime import date, datetime

import pandas as pd
from sqlalchemy.orm import Session

from config import SRC_URL
from fetcher import fetch_page
from extractor import extract_stats
from normalizer import normalize_df
from planner import get_plan
from validator import validate_df, validate_and_repair_plan
from analyst import analyze_meta
from report import build_report
from schemas import STAT_FIELDS
from ranker import rank_candidates

from api.repositories.stats import (
    get_stats_for_date,
    save_scrape_run_with_stats,
)

def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    f = filters
    if f.get("lane"):
        df = df[df["lane"].str.lower() == f["lane"].lower()]
    if f.get("hero"):
        df = df[df["hero"].str.lower() == f["hero"].lower()]
    if f.get("min_win_rate") is not None:
        df = df[df["win_rate"] >= f["min_win_rate"]]
    if f.get("max_win_rate") is not None:
        df = df[df["win_rate"] <= f["max_win_rate"]]
    if f.get("min_pick_rate") is not None:
        df = df[df["pick_rate"] >= f["min_pick_rate"]]
    if f.get("max_pick_rate") is not None:
        df = df[df["pick_rate"] <= f["max_pick_rate"]]
    if f.get("min_ban_rate") is not None:
        df = df[df["ban_rate"] >= f["min_ban_rate"]]
    if f.get("max_ban_rate") is not None:
        df = df[df["ban_rate"] <= f["max_ban_rate"]]
    return df.head(f.get("top_n", 10)) if f.get("top_n") else df


def save_report(text: str, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def find_latest_csv_for_day(folder, prefix: str, day: str):
    matches = list(folder.glob(f"{prefix}_{day}_*.csv"))
    if not matches:
        return None
    return max(matches, key=lambda p: p.stat().st_mtime)


def run_pipeline(user_query: str, db: Session):
    raw_plan = get_plan(user_query=user_query)
    plan = validate_and_repair_plan(raw_plan)

    today = date.today()
    stats = get_stats_for_date(db, today)

    if stats is None:
        html = fetch_page(SRC_URL)
        rows = extract_stats(html)

        df_raw = pd.DataFrame(rows, columns=STAT_FIELDS)
        df_norm = normalize_df(df_raw)
        df_clean, df_issues = validate_df(df_norm)

        issue_count = int(len(df_issues))

        save_scrape_run_with_stats(
            db=db,
            source=SRC_URL,
            scraped_for_date=today,
            df_clean=df_clean,
            issue_count=issue_count,
        )
    else:
        df_clean = pd.DataFrame(stats["heroes"])
        issue_count = int(stats["issue_count"])

    df_filtered = apply_filters(df_clean.copy(), {**plan["filters"], "top_n": None})

    df_filtered = rank_candidates(
        df_filtered,
        task_type=plan["task_type"],
        top_n=plan["filters"].get("top_n", 10),
    )

    if df_filtered.empty:
        raise ValueError(
            f"Filters returned 0 heroes. Try relaxing your query. "
            f"Plan filters: {plan['filters']}"
        )

    analyst_output = analyze_meta(
        user_query=user_query,
        df_clean=df_filtered,
        issue_count=issue_count,
    )

    report_md = build_report(analyst_output=analyst_output)

    ts = datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
    report_id = f"report_{ts}"

    result = {
        "report_id": report_id,
        "query": user_query,
        "plan": plan,
        "analyst_output": analyst_output,
        "report_md": report_md,
        "issue_count": issue_count,
        "hero_count": int(len(df_filtered)),
        "generated_at": datetime.utcnow().isoformat(),
    }

    yield ("done", "Report ready.", result)


def load_latest_stats() -> dict | None:
    today = get_today()
    clean_csv = find_latest_csv_for_day(CLEAN_DIR, "stats_cleaned", today)
    issues_csv = find_latest_csv_for_day(CLEAN_DIR, "stats_issues", today)
 
    if clean_csv is None:
        return None
 
    df_clean = pd.read_csv(clean_csv)
 
    issue_count = 0
    if issues_csv is not None:
        try:
            issue_count = len(pd.read_csv(issues_csv))
        except pd.errors.EmptyDataError:
            pass
 
    return {
        "date": today,
        "hero_count": len(df_clean),
        "issue_count": issue_count,
        "heroes": df_clean.where(pd.notna(df_clean), None).to_dict(orient="records"),
    }