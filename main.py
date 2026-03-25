import pandas as pd
import sys

from config import SRC_URL, CLEAN_DIR, RAW_DIR
from fetcher import fetch_page
from extractor import extract_stats
from normalizer import normalize_df
from planner import get_plan_from_llm
from validator import validate_df, validate_and_repair_plan
from insights import run_insight_task
from report import build_report
from schemas import STAT_FIELDS
from utils import (
    build_csv_path,
    build_clean_csv_path,
    build_issues_csv_path,
    current_timestamp,
    ensure_dir,
)

def save_report(text: str, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def main() -> None:
    user_query = " ".join(sys.argv[1:]).strip() or "summarize the current meta"

    raw_plan = get_plan_from_llm(user_query)
    plan = validate_and_repair_plan(raw_plan)

    ensure_dir(CLEAN_DIR)
    ensure_dir(RAW_DIR)

    ts = current_timestamp()

    print(f"Fetching from {SRC_URL}")
    html = fetch_page(SRC_URL)

    rows = extract_stats(html)
    df_raw = pd.DataFrame(rows, columns=STAT_FIELDS)

    raw_csv_path = build_csv_path(CLEAN_DIR, ts)
    df_raw.to_csv(raw_csv_path, index=False, encoding="utf-8")
    print(f"Saved raw CSV to: {raw_csv_path}")
    print(f"Raw rows: {len(df_raw)}")

    df_norm = normalize_df(df_raw)
    df_clean, df_issues = validate_df(df_norm)

    clean_csv_path = build_clean_csv_path(CLEAN_DIR, ts)
    issues_csv_path = build_issues_csv_path(CLEAN_DIR, ts)

    df_clean.to_csv(clean_csv_path, index=False, encoding="utf-8")
    df_issues.to_csv(issues_csv_path, index=False, encoding="utf-8")

    df_insights = run_insight_task(df_clean, plan=plan)

    report = build_report(
        task_type=plan["task_type"],
        raw_rows=len(df_raw),
        cleaned_rows=len(df_clean),
        issue_count=len(df_issues),
        insight_df=df_insights,
    )

    report_path = CLEAN_DIR / f"report_{ts}.md"
    save_report(report, report_path)


if __name__ == "__main__":
    main()