import pandas as pd

from config import CLEAN_DIR, RAW_DIR, SRC_URL
from extractor import extract_stats
from normalizer import normalize_df
from validator import validate_df
from fetcher import fetch_page
from schemas import STAT_FIELDS
from utils import (
    build_clean_csv_path,
    build_issues_csv_path,
    current_timestamp,
    ensure_dir,
)

def main():
    ensure_dir(CLEAN_DIR)

    raw_csv = max(CLEAN_DIR.glob("*.csv"), key=lambda p: p.stat().st_mtime)
    print(f"Loading raw CSV: {raw_csv}")

    df = pd.read_csv(raw_csv)
    df_norm = normalize_df(df)
    df_clean, df_issues = validate_df(df_norm)

    ts = current_timestamp()
    clean_path = build_clean_csv_path(CLEAN_DIR, ts)
    issues_path = build_issues_csv_path(CLEAN_DIR, ts)

    df_clean.to_csv(clean_path, index=False, encoding="utf-8")
    df_issues.to_csv(issues_path, index=False, encoding="utf-8")

    print(f"Input rows: {len(df)}")
    print(f"Cleaned rows: {len(df_clean)}")
    print(f"Issues found: {len(df_issues)}")
    print(f"Saved cleaned CSV to: {clean_path}")
    print(f"Saved issues CSV to: {issues_path}")
    

if __name__ == "__main__":
    main()