from datetime import date, datetime

import pandas as pd
from sqlalchemy.orm import Session

from app.db.repositories.stats import get_stats_for_date
from app.services.planner import get_plan
from app.services.query_filters import infer_lane_from_query, normalize_lane
from app.services.validator import validate_and_repair_plan
from app.services.stats_processor import has_valid_cached_stats
from app.services.recommender import select_recommendations, build_output


def get_pipeline_plan(user_query: str) -> dict:
    raw_plan = get_plan(user_query=user_query)
    plan = validate_and_repair_plan(raw_plan)
    
    inferred_lane = infer_lane_from_query(user_query)

    if inferred_lane:
        plan["filters"]["lane"] = inferred_lane
    elif plan["filters"].get("lane"):
        plan["filters"]["lane"] = normalize_lane(plan["filters"]["lane"])

    return plan


def load_today_stats(db: Session) -> tuple[pd.DataFrame, int]:
    today = date.today()
    stats = get_stats_for_date(db, today)

    if not has_valid_cached_stats(stats):
        raise ValueError(
            "No valid hero stats found in DB for today. "
            "Restart the backend or trigger a stats refresh first."
        )
    
    df_clean = pd.DataFrame(stats["heroes"])
    issue_count = int(stats["issue_count"])

    return df_clean, issue_count


def run_pipeline(user_query: str, db: Session):
    plan = get_pipeline_plan(user_query=user_query)
    df_clean, issue_count = load_today_stats(db)

    df_recommendations, df_role_pool = select_recommendations(df_clean, plan)

    if df_recommendations.empty:
        raise ValueError(
            f"Filters returned 0 heroes. Try relaxing your query. "
            f"Plan filters: {plan['filters']}"
        )
    
    output = build_output(
        df_recommendations=df_recommendations,
        df_role_pool=df_role_pool,
        task_type=plan["task_type"],
        heroes_per_lane=3
    )

    result = {
        "query": user_query,
        "plan": plan,
        "recommendations": output["recommendations"],
        "role_summary": output["role_summary"],
        "issue_count": issue_count,
        "hero_count": int(len(df_recommendations)),
        "generated_at": datetime.utcnow().isoformat(),
    }

    yield ("done", "Recommendations ready.", result)

