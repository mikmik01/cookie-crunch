import re
import sys
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SRC_URL, CLEAN_DIR, PROCESSED_DIR, RAW_DIR, REPORT_DIR
from fetcher import fetch_page
from extractor import extract_stats
from normalizer import normalize_df
from planner import get_plan
from validator import validate_df, validate_and_repair_plan
from analyst import analyze_meta
from report import build_report
from schemas import STAT_FIELDS
from utils import (
    build_csv_path,
    build_clean_csv_path,
    build_issues_csv_path,
    current_timestamp,
    ensure_dir,
    get_today
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


def run_pipeline(user_query: str):
    raw_plan = get_plan(user_query=user_query)
    plan = validate_and_repair_plan(raw_plan)

    for d in (RAW_DIR, CLEAN_DIR, PROCESSED_DIR, REPORT_DIR):
        ensure_dir(d)
    
    ts = current_timestamp()
    today = get_today()

    raw_csv = find_latest_csv_for_day(PROCESSED_DIR, "stats", today)

    if raw_csv is None:
        html = fetch_page(SRC_URL)
        rows = extract_stats(html)
        df_raw = pd.DataFrame(rows, columns=STAT_FIELDS)
        raw_csv_path = build_csv_path(PROCESSED_DIR, ts)
        df_raw.to_csv(raw_csv_path, index=False, encoding="utf-8")
    else:
        df_raw = pd.read_csv(raw_csv)
    
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
    else:
        df_norm = normalize_df(df_raw)
        df_clean, df_issues = validate_df(df_norm)
        df_clean.to_csv(build_clean_csv_path(CLEAN_DIR, ts), index=False, encoding="utf-8")
        df_issues.to_csv(build_issues_csv_path(CLEAN_DIR, ts), index=False, encoding="utf-8")
    
    df_filtered = apply_filters(df_clean.copy(), plan["filters"])
 
    if df_filtered.empty:
        raise ValueError(
            f"Filters returned 0 heroes. Try relaxing your query. "
            f"Plan filters: {plan['filters']}"
        )

    analyst_output = analyze_meta(
        user_query=user_query,
        df_clean=df_filtered,
        issue_count=len(df_issues),
    )

    report_markdown = build_report(analyst_output=analyst_output)
 
    report_id = f"report_{ts}"
    report_path = REPORT_DIR / f"{report_id}.md"
    save_report(report_markdown, report_path)

    result = {
        "report_id": report_id,
        "query": user_query,
        "plan": plan,
        "analyst_output": analyst_output,
        "report_markdown": report_markdown,
        "issue_count": int(len(df_issues)),
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