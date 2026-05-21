from datetime import date, datetime

import pandas as pd
from sqlalchemy.orm import Session

from backend.app.core.config import SRC_URL, RANK_FILTERS, build_stats_url
from backend.app.schemas.schemas import STAT_OUTPUT_FIELDS
from backend.app.services.fetcher import fetch_page
from backend.app.services.extractor import extract_stats
from backend.app.services.normalizer import normalize_df
from backend.app.services.validator import validate_df, validate_and_repair_plan
from backend.app.services.report import build_report
from backend.app.services.ranker import rank_candidates

from backend.app.db.repositories.stats import (
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
    if f.get("rank_filter") and "rank_filter" in df.columns:
        df = df[
            df["rank_filter"].astype(str).str.lower()
            == f["rank_filter"].lower()
        ]
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


def get_pipeline_plan(user_query: str) -> dict:
    from backend.app.services.planner import get_plan

    return get_plan(user_query=user_query)


def run_analyst(user_query: str, df_clean: pd.DataFrame, issue_count: int) -> dict:
    from backend.app.services.analyst import analyze_meta

    return analyze_meta(
        user_query=user_query,
        df_clean=df_clean,
        issue_count=issue_count,
    )


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


def run_pipeline(user_query: str, db: Session):
    raw_plan = get_pipeline_plan(user_query)
    plan = validate_and_repair_plan(raw_plan)

    today = date.today()
    stats = get_stats_for_date(db, today)

    if stats is None:
        df_raw = fetch_all_rank_stats()

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

    df_pool = apply_filters(df_clean.copy(), {**plan["filters"], "top_n": None})

    df_filtered = rank_candidates(
        df_pool,
        task_type=plan["task_type"],
        top_n=plan["filters"].get("top_n", 10),
    )

    if df_filtered.empty:
        raise ValueError(
            f"Filters returned 0 heroes. Try relaxing your query. "
            f"Plan filters: {plan['filters']}"
        )

    report_payload = build_report(
        df_recommendations=df_filtered,
        df_role_pool=df_pool,
        task_type=plan["task_type"],
        heroes_per_lane=3,
    )

    ts = datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
    report_id = f"report_{ts}"

    result = {
        "report_id": report_id,
        "query": user_query,
        "plan": plan,
        "recommendations": report_payload["recommendations"],
        "role_summary": report_payload["role_summary"],
        "issue_count": issue_count,
        "hero_count": int(len(df_filtered)),
        "generated_at": datetime.utcnow().isoformat(),
    }

    yield ("done", "Report ready.", result)
