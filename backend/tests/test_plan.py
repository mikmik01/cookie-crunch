from app.services.validator import validate_and_repair_plan


def test_plan_repair_returns_safe_plan_from_bad_llm_output():
    bad_plan = {
        "task_type": "nonsense_task",
        "steps": ["fetch_extract", "hack_database", "build_report"],
        "filters": {
            "min_win_rate": 80,
            "max_win_rate": 50,
            "min_pick_rate": -10,
            "top_n": "abc",
        },
        "reasoning_summary": "bad plan from LLM",
    }

    repaired = validate_and_repair_plan(bad_plan)

    assert repaired["task_type"] == "summarize_meta"
    assert repaired["steps"] == ["fetch_extract", "build_report"]

    assert repaired["filters"]["min_win_rate"] == 50
    assert repaired["filters"]["max_win_rate"] == 80
    assert repaired["filters"]["min_pick_rate"] is None
    assert repaired["filters"]["top_n"] == 10