import pandas as pd
import sys

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

def save_report(text: str, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def find_latest_csv_for_day(folder, prefix: str, day: str):
    matches = list(folder.glob(f"{prefix}_{day}_*.csv"))
    if not matches:
        return None
    return max(matches, key=lambda p: p.stat().st_mtime)

def main() -> None:
    user_query = " ".join(sys.argv[1:]).strip() or "summarize the current meta"

    raw_plan = get_plan(user_query)
    plan = validate_and_repair_plan(raw_plan)

    ensure_dir(CLEAN_DIR)
    ensure_dir(PROCESSED_DIR)
    ensure_dir(RAW_DIR)

    ts = current_timestamp()
    today = get_today()

    raw_csv = find_latest_csv_for_day(PROCESSED_DIR, "stats", today)
    clean_csv = find_latest_csv_for_day(CLEAN_DIR, "stats_cleaned", today)
    issues_csv = find_latest_csv_for_day(CLEAN_DIR, "stats_issues", today)

    if raw_csv is None:
        print(f"No stats found for {today}. fetching new stats...")
        html = fetch_page(SRC_URL)
        print("done!")
        rows = extract_stats(html)
        df_raw = pd.DataFrame(rows, columns=STAT_FIELDS)
        raw_csv_path = build_csv_path(PROCESSED_DIR, ts)
        df_raw.to_csv(raw_csv_path, index=False, encoding="utf-8")
    else:
        raw_csv_path = raw_csv
        df_raw = pd.read_csv(raw_csv_path)
    
    if clean_csv is not None and issues_csv is not None:
        clean_csv_path = clean_csv
        issues_csv_path = issues_csv
        df_clean = pd.read_csv(clean_csv_path)
        try:
            df_issues = pd.read_csv(issues_csv_path)
        except pd.errors.EmptyDataError:
            df_issues = pd.DataFrame(columns=["row_index", "hero", "field", "issue", "value"])
    else:
        df_norm = normalize_df(df_raw)
        df_clean, df_issues = validate_df(df_norm)
        clean_csv_path = build_clean_csv_path(CLEAN_DIR, ts)
        issues_csv_path = build_issues_csv_path(CLEAN_DIR, ts)
        df_clean.to_csv(clean_csv_path, index=False, encoding="utf-8")
        df_issues.to_csv(issues_csv_path, index=False, encoding="utf-8")

    analyst_output = analyze_meta(user_query=user_query, df_clean=df_clean, issue_count=len(df_issues))

    report = build_report(
        analyst_output=analyst_output
    )

    report_path = REPORT_DIR / f"report_{ts}.md"
    save_report(report, report_path)


if __name__ == "__main__":
    main()