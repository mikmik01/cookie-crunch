import pandas as pd

from backend.app.services.report import build_report


def test_report_returns_empty_structured_payload_when_dataframe_is_empty():
    result = build_report(
        df_recommendations=pd.DataFrame(),
        df_role_pool=pd.DataFrame(),
    )

    assert result == {
        "recommendations": [],
        "role_summary": [],
    }


def test_report_returns_recommendations_as_structured_payload():
    df = pd.DataFrame([
        {
            "hero": "Alice",
            "lane": "Mid",
            "tier": "S",
            "win_rate": 53.2,
            "pick_rate": 8.4,
            "ban_rate": 12.1,
        },
        {
            "hero": "Bruno",
            "lane": "Gold",
            "tier": "A",
            "win_rate": 51.7,
            "pick_rate": 10.5,
            "ban_rate": 6.3,
        },
    ])

    result = build_report(
        df_recommendations=df,
        df_role_pool=df,
        task_type="summarize_meta",
        heroes_per_lane=3,
    )

    assert "recommendations" in result
    assert "role_summary" in result

    assert result["recommendations"][0] == {
        "hero": "Alice",
        "lane": "Mid",
        "tier": "S",
        "win_rate": 53.2,
        "pick_rate": 8.4,
        "ban_rate": 12.1,
    }

    assert any(group["lane"] == "Mid" for group in result["role_summary"])
    assert any(group["lane"] == "Gold" for group in result["role_summary"])