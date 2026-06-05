import pandas as pd

from backend.app.services.ranker import rank_candidates
from backend.app.services.query_filters import apply_filters


def select_recommendations(
    df_clean: pd.DataFrame,
    plan: dict,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    filters = plan["filters"]

    df_pool = apply_filters(
        df_clean.copy(),
        {**filters, "top_n": None},
    )

    df_recommendations = rank_candidates(
        df_pool,
        task_type=plan["task_type"],
        top_n=filters.get("top_n", 5),
    )

    return df_recommendations, df_pool


RECOMMENDATION_COLUMNS = [
    "hero",
    "lane",
    "tier",
    "win_rate",
    "pick_rate",
    "ban_rate",
]

ROLE_HERO_COLUMNS = [
    "hero",
    "tier",
    "win_rate",
    "pick_rate",
    "ban_rate",
]

LANE_ORDER = ["Exp", "Gold", "Jungle", "Mid", "Roam"]


def df_to_text(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "No results found"
    return df.to_string(index=False)


def clean_value(value):
    if pd.isna(value):
        return None
    
    if isinstance(value, (int, float)):
        return round(float(value), 2)
    
    return value


def df_to_records(df: pd.DataFrame, columns: list[str]) -> list[dict]:
    if df is None or df.empty:
        return []
    
    available_columns = [col for col in columns if col in df.columns]
    records = df[available_columns].to_dict(orient="records")

    return [
        {key: clean_value(value) for key, value in record.items()}
        for record in records
    ]


def build_recommendations(df: pd.DataFrame) -> list[dict]:
    return df_to_records(df, RECOMMENDATION_COLUMNS)


def build_role_summary(
    df: pd.DataFrame,
    task_type: str = "summarize meta",
    heroes_per_lane: int = 3
) -> list[dict]:
    if df is None or df.empty or "lane" not in df.columns:
        return []
    role_summary = []

    # remove duplicates
    existing_lanes = {
        str(lane).strip()
        for lane in df["lane"].dropna().unique()
        if str(lane).strip()
    }

    ordered_lanes = [lane for lane in LANE_ORDER if lane in existing_lanes]
    remaining_lanes = sorted(existing_lanes - set(ordered_lanes))
    all_lanes = ordered_lanes + remaining_lanes

    for lane in all_lanes:
        lane_df = df[df["lane"].astype(str).str.lower() == lane.lower()].copy()

        ranked_lane_df = rank_candidates(
            lane_df,
            task_type=task_type,
            top_n=heroes_per_lane,
        )

        heroes = df_to_records(ranked_lane_df, ROLE_HERO_COLUMNS)

        if heroes:
            role_summary.append({
                "lane": lane,
                "heroes": heroes,
            })

    return role_summary


def build_output(
    df_recommendations: pd.DataFrame,
    df_role_pool: pd.DataFrame | None = None,
    task_type: str = "summarize_meta",
    heroes_per_lane: int = 3,
) -> dict:
    if df_role_pool is None:
        df_role_pool = df_recommendations

    return {
        "recommendations": build_recommendations(df_recommendations),
        "role_summary": build_role_summary(
            df=df_role_pool,
            task_type=task_type,
            heroes_per_lane=heroes_per_lane,
        ),
    }