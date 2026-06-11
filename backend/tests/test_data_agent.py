import pandas as pd
import pytest

from backend.app.services.data_agent import ToolExecutionError, execute_tool_call, execute_tool_calls


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        [
            {
                "rank": 1,
                "lane": "Jungle",
                "hero": "Suyou",
                "tier": "S",
                "win_rate": 52.1,
                "ban_rate": 18.4,
                "pick_rate": 9.2,
                "roles": "Assassin, Fighter",
            },
            {
                "rank": 2,
                "lane": "Exp",
                "hero": "Yu Zhong",
                "tier": "S",
                "win_rate": 51.4,
                "ban_rate": 12.1,
                "pick_rate": 8.8,
                "roles": "Fighter",
            },
            {
                "rank": 3,
                "lane": "Gold",
                "hero": "Bruno",
                "tier": "A",
                "win_rate": 50.2,
                "ban_rate": 4.3,
                "pick_rate": 11.5,
                "roles": "Marksman",
            },
        ]
    )


def test_execute_get_schema(sample_df):
    response = execute_tool_call(
        sample_df,
        {
            "tool": "get_schema",
            "args": {},
        },
    )

    assert response["ok"] is True
    assert response["tool"] == "get_schema"
    assert "columns" in response["result"]
    assert "hero" in response["result"]["columns"]


def test_execute_filter_rows_for_hero(sample_df):
    response = execute_tool_call(
        sample_df,
        {
            "tool": "filter_rows",
            "args": {
                "filters": [
                    {
                        "column": "hero",
                        "operator": "contains",
                        "value": "suyou",
                    }
                ],
                "limit": 5,
            },
        },
    )

    assert response["ok"] is True
    assert response["tool"] == "filter_rows"
    assert len(response["result"]) == 1
    assert response["result"][0]["hero"] == "Suyou"
    assert response["result"][0]["lane"] == "Jungle"


def test_execute_filter_rows_with_sort(sample_df):
    response = execute_tool_call(
        sample_df,
        {
            "tool": "filter_rows",
            "args": {
                "sort": [
                    {
                        "column": "pick_rate",
                        "direction": "desc",
                    }
                ],
                "limit": 2,
            },
        },
    )

    assert response["ok"] is True
    assert len(response["result"]) == 2
    assert response["result"][0]["hero"] == "Bruno"
    assert response["result"][1]["hero"] == "Suyou"


def test_execute_aggregate_rows(sample_df):
    response = execute_tool_call(
        sample_df,
        {
            "tool": "aggregate_rows",
            "args": {
                "group_by": "lane",
                "metrics": [
                    {
                        "column": "win_rate",
                        "function": "mean",
                    }
                ],
                "sort": [
                    {
                        "column": "win_rate_mean",
                        "direction": "desc",
                    }
                ],
                "limit": 10,
            },
        },
    )

    assert response["ok"] is True
    assert response["tool"] == "aggregate_rows"
    assert response["result"][0]["lane"] == "Jungle"
    assert response["result"][0]["win_rate_mean"] == 52.1


def test_execute_tool_call_rejects_unknown_tool(sample_df):
    with pytest.raises(ToolExecutionError, match="Unsupported tool"):
        execute_tool_call(
            sample_df,
            {
                "tool": "best_lane_for_hero",
                "args": {
                    "hero": "Suyou",
                },
            },
        )


def test_execute_tool_call_returns_error_for_bad_args(sample_df):
    response = execute_tool_call(
        sample_df,
        {
            "tool": "filter_rows",
            "args": {
                "filters": [
                    {
                        "column": "damage",
                        "operator": ">=",
                        "value": 100,
                    }
                ],
            },
        },
    )

    assert response["ok"] is False
    assert response["tool"] == "filter_rows"
    assert "Unsupported column" in response["error"]


def test_execute_tool_call_requires_dict(sample_df):
    with pytest.raises(ToolExecutionError, match="tool_call must be a dictionary"):
        execute_tool_call(sample_df, "filter_rows")


def test_execute_tool_call_requires_args_dict(sample_df):
    with pytest.raises(ToolExecutionError, match="args must be a dictionary"):
        execute_tool_call(
            sample_df,
            {
                "tool": "filter_rows",
                "args": [],
            },
        )


def test_execute_multiple_tool_calls(sample_df):
    responses = execute_tool_calls(
        sample_df,
        [
            {
                "tool": "filter_rows",
                "args": {
                    "filters": [
                        {
                            "column": "hero",
                            "operator": "contains",
                            "value": "Suyou",
                        }
                    ],
                    "limit": 5,
                },
            },
            {
                "tool": "aggregate_rows",
                "args": {
                    "group_by": "lane",
                    "metrics": [
                        {
                            "column": "hero",
                            "function": "count",
                        }
                    ],
                    "limit": 10,
                },
            },
        ],
    )

    assert len(responses) == 2
    assert responses[0]["ok"] is True
    assert responses[1]["ok"] is True
    assert responses[0]["result"][0]["hero"] == "Suyou"


def test_execute_multiple_tool_calls_requires_list(sample_df):
    with pytest.raises(ToolExecutionError, match="tool_calls must be a list"):
        execute_tool_calls(sample_df, {"tool": "get_schema", "args": {}})