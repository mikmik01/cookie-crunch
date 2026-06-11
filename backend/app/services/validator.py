import pandas as pd
from copy import deepcopy
from app.core.config import DEFAULT_PLAN, ALLOWED_STEPS, ALLOWED_TASK_TYPES, REQUIRED_COLUMNS, ALLOWED_TIERS

def _to_float_or_none(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int_or_default(value, default=10):
    try:
        ivalue = int(value)
        return ivalue if ivalue > 0 else default
    except (TypeError, ValueError):
        return default


def validate_and_repair_plan(plan: dict) -> dict:
    repaired = deepcopy(DEFAULT_PLAN)

    if not isinstance(plan, dict):
        return repaired

    task_type = plan.get("task_type")
    if task_type in ALLOWED_TASK_TYPES:
        repaired["task_type"] = task_type

    steps = plan.get("steps")
    if isinstance(steps, list):
        valid_steps = [s for s in steps if s in ALLOWED_STEPS]
        if valid_steps:
            repaired["steps"] = valid_steps

    filters = plan.get("filters")
    if isinstance(filters, dict):
        repaired["filters"]["lane"] = filters.get("lane") or None
        repaired["filters"]["hero"] = filters.get("hero") or None

        for key in [
            "min_win_rate", "max_win_rate",
            "min_pick_rate", "max_pick_rate",
            "min_ban_rate", "max_ban_rate",
        ]:
            repaired["filters"][key] = _to_float_or_none(filters.get(key))

        repaired["filters"]["top_n"] = _to_int_or_default(filters.get("top_n"), default=10)

    reasoning = plan.get("reasoning_summary")
    if isinstance(reasoning, str) and reasoning.strip():
        repaired["reasoning_summary"] = reasoning.strip()

    for key in [
        "min_win_rate", "max_win_rate",
        "min_pick_rate", "max_pick_rate",
        "min_ban_rate", "max_ban_rate",
    ]:
        value = repaired["filters"][key]
        if value is not None and not (0 <= value <= 100):
            repaired["filters"][key] = None

    f = repaired["filters"]
    if f["min_win_rate"] is not None and f["max_win_rate"] is not None and f["min_win_rate"] > f["max_win_rate"]:
        f["min_win_rate"], f["max_win_rate"] = f["max_win_rate"], f["min_win_rate"]

    if f["min_pick_rate"] is not None and f["max_pick_rate"] is not None and f["min_pick_rate"] > f["max_pick_rate"]:
        f["min_pick_rate"], f["max_pick_rate"] = f["max_pick_rate"], f["min_pick_rate"]

    if f["min_ban_rate"] is not None and f["max_ban_rate"] is not None and f["min_ban_rate"] > f["max_ban_rate"]:
        f["min_ban_rate"], f["max_ban_rate"] = f["max_ban_rate"], f["min_ban_rate"]

    return repaired

def validate_df(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    issues = []

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            issues.append({
                "row_index": None,
                "hero": None,
                "field": col,
                "issue": "missing_column",
                "value": None,
            })
    
    if issues:
        return df.iloc[0:0].copy(), pd.DataFrame(issues)
    
    for i, row in df.iterrows():
        hero = row["hero"]

        if row["rank"] is None or pd.isna(row["rank"]) or row["rank"] < 1:
            issues.append({
                "row_index": i, "hero": hero, "field": "rank",
                "issue": "invalid_rank", "value": row["rank"]
            })
        
        for field in ["win_rate", "ban_rate", "pick_rate"]:
            value = row[field]
            if value is None or pd.isna(value):
                issues.append({
                    "row_index": i, "hero": hero, "field": field,
                    "issue": "missing_value", "value": value
                })
            elif not (0 <= value <= 100):
                issues.append({
                    "row_index": i, "hero": hero, "field": field,
                    "issue": "out_of_range", "value": value
                })
        
        if not str(hero).strip():
            issues.append({
                "row_index": i, "hero": hero, "field": "hero",
                "issue": "empty_hero", "value": hero
            })
        
        tier = str(row["tier"]).strip()
        if tier and tier not in ALLOWED_TIERS:
            issues.append({
                "row_index": i, "hero": hero, "field": "tier",
                "issue": "unexpected_tier", "value": tier
            })
    
    dupes = df[df.duplicated(subset=["hero"], keep=False)]
    for idx, row in dupes.iterrows():
        issues.append({
            "row_index": idx, "hero": row["hero"], "field": "hero",
            "issue": "duplicate_hero", "value": row["hero"]
        })

    issues_df = pd.DataFrame(issues)

    invalid_rows = set(issues_df["row_index"].dropna().astype(int).tolist()) if not issues_df.empty else set()
    cleaned_df = df.drop(index=list(invalid_rows)).copy()

    return cleaned_df, issues_df