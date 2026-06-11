import pandas as pd
import pytest

from backend.app.services.data_tools import filter_rows, get_schema, aggregate_rows


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


def test_get_schema_returns_columns():
    schema = get_schema()

    assert "columns" in schema
    assert "hero" in schema["columns"]
    assert "win_rate" in schema["columns"]


def test_filter_rows_by_hero_contains(sample_df):
    rows = filter_rows(
        sample_df,
        filters=[
            {
                "column": "hero",
                "operator": "contains",
                "value": "suyou",
            }
        ],
        limit=5,
    )

    assert len(rows) == 1
    assert rows[0]["hero"] == "Suyou"
    assert rows[0]["lane"] == "Jungle"


def test_filter_rows_by_lane_equals(sample_df):
    rows = filter_rows(
        sample_df,
        filters=[
            {
                "column": "lane",
                "operator": "equals",
                "value": "Exp",
            }
        ],
        limit=5,
    )

    assert len(rows) == 1
    assert rows[0]["hero"] == "Yu Zhong"


def test_filter_rows_by_numeric_operator(sample_df):
    rows = filter_rows(
        sample_df,
        filters=[
            {
                "column": "win_rate",
                "operator": ">=",
                "value": 51,
            }
        ],
        sort=[
            {
                "column": "win_rate",
                "direction": "desc",
            }
        ],
        limit=10,
    )

    assert len(rows) == 2
    assert rows[0]["hero"] == "Suyou"
    assert rows[1]["hero"] == "Yu Zhong"


def test_filter_rows_sorts_by_pick_rate_desc(sample_df):
    rows = filter_rows(
        sample_df,
        sort=[
            {
                "column": "pick_rate",
                "direction": "desc",
            }
        ],
        limit=3,
    )

    assert rows[0]["hero"] == "Bruno"
    assert rows[1]["hero"] == "Suyou"
    assert rows[2]["hero"] == "Yu Zhong"


def test_filter_rows_rejects_unsupported_column(sample_df):
    with pytest.raises(ValueError, match="Unsupported column"):
        filter_rows(
            sample_df,
            filters=[
                {
                    "column": "damage",
                    "operator": ">=",
                    "value": 100,
                }
            ],
        )


def test_filter_rows_rejects_unsupported_operator(sample_df):
    with pytest.raises(ValueError, match="Unsupported operator"):
        filter_rows(
            sample_df,
            filters=[
                {
                    "column": "hero",
                    "operator": "starts_with",
                    "value": "Su",
                }
            ],
        )


def test_filter_rows_caps_limit_at_50(sample_df):
    rows = filter_rows(sample_df, limit=100)

    assert len(rows) == 3


def test_aggregate_rows_mean_win_rate_by_lane(sample_df):
    rows = aggregate_rows(
        sample_df,
        group_by="lane",
        metrics=[
            {
                "column": "win_rate",
                "function": "mean",
            }
        ],
        sort=[
            {
                "column": "win_rate_mean",
                "direction": "desc",
            }
        ],
        limit=10,
    )

    assert rows[0]["lane"] == "Jungle"
    assert rows[0]["win_rate_mean"] == 52.1


def test_aggregate_rows_count_heroes_by_lane(sample_df):
    rows = aggregate_rows(
        sample_df,
        group_by="lane",
        metrics=[
            {
                "column": "hero",
                "function": "count",
            }
        ],
        sort=[
            {
                "column": "hero_count",
                "direction": "desc",
            }
        ],
        limit=10,
    )

    assert len(rows) == 3
    assert rows[0]["hero_count"] == 1


def test_aggregate_rows_rejects_unsupported_group_by(sample_df):
    with pytest.raises(ValueError, match="Unsupported group_by column"):
        aggregate_rows(
            sample_df,
            group_by="damage",
            metrics=[
                {
                    "column": "win_rate",
                    "function": "mean",
                }
            ],
        )


def test_aggregate_rows_rejects_unsupported_function(sample_df):
    with pytest.raises(ValueError, match="Unsupported aggregation function"):
        aggregate_rows(
            sample_df,
            group_by="lane",
            metrics=[
                {
                    "column": "win_rate",
                    "function": "sum",
                }
            ],
        )