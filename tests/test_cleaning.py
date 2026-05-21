import pandas as pd

from backend.app.services.normalizer import normalize_df
from backend.app.services.validator import validate_df, validate_and_repair_plan

def test_cleaning_pipeline_converts_valid_rows_and_separates_invalid_rows():
    raw = pd.DataFrame([
        {
            "rank": "1",
            "lane": " Mid ",
            "hero": "  Cecilion ",
            "tier": " S ",
            "win_rate": "53.2%",
            "ban_rate": "12.5%",
            "pick_rate": "8.1%",
            "roles": "Mage / Burst",
        },
        {
            "rank": "2",
            "lane": "Gold",
            "hero": "Bad Hero",
            "tier": "S",
            "win_rate": "120%",
            "ban_rate": "5%",
            "pick_rate": "3%",
            "roles": "Marksman",
        },
    ])

    normalized = normalize_df(raw)
    cleaned, issues = validate_df(normalized)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["hero"] == "Cecilion"
    assert cleaned.iloc[0]["rank"] == 1
    assert cleaned.iloc[0]["win_rate"] == 53.2
    assert cleaned.iloc[0]["roles"] == "Mage, Burst"

    assert len(issues) == 1
    assert issues.iloc[0]["hero"] == "Bad Hero"
    assert issues.iloc[0]["field"] == "win_rate"
    assert issues.iloc[0]["issue"] == "out_of_range"

def test_plan_repair_preserves_valid_llm_output():
    valid_plan = {
        "task_type": "find_underrated_heroes",
        "steps": ["fetch_extract", "normalize", "validate", "generate_insights", "build_report"],
        "filters": {
            "lane": "Mid",
            "hero": None,
            "min_win_rate": 52,
            "max_win_rate": None,
            "min_pick_rate": None,
            "max_pick_rate": 10,
            "min_ban_rate": None,
            "max_ban_rate": None,
            "top_n": 5,
        },
        "reasoning_summary": "Find high win-rate, lower pick-rate Mid heroes.",
    }

    repaired = validate_and_repair_plan(valid_plan)

    assert repaired["task_type"] == "find_underrated_heroes"
    assert repaired["steps"] == valid_plan["steps"]
    assert repaired["filters"]["lane"] == "Mid"
    assert repaired["filters"]["min_win_rate"] == 52
    assert repaired["filters"]["max_pick_rate"] == 10
    assert repaired["filters"]["top_n"] == 5