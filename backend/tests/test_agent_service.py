import pandas as pd
import pytest

import app.services.agent as agent


@pytest.fixture
def sample_clean_df():
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
        ]
    )


@pytest.fixture
def sample_issues_df():
    return pd.DataFrame(
        columns=["row_index", "hero", "field", "issue", "value"]
    )


def test_answer_query_returns_agent_response(
    monkeypatch,
    sample_clean_df,
    sample_issues_df,
):
    def fake_load_or_create_clean_stats():
        return sample_clean_df, sample_issues_df

    def fake_run_data_agent(user_query, df, max_steps):
        assert user_query == "suyou's best lane"
        assert max_steps == 4
        assert len(df) == 2

        return {
            "answer": "Based on the current stats table, Suyou is listed under Jungle.",
            "confidence": "high",
            "observations": [
                {
                    "step": 1,
                    "model_output": {
                        "type": "tool_call",
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
                    "tool_result": {
                        "tool": "filter_rows",
                        "ok": True,
                        "result": [
                            {
                                "hero": "Suyou",
                                "lane": "Jungle",
                            }
                        ],
                    },
                }
            ],
        }

    monkeypatch.setattr(
        agent,
        "load_or_create_clean_stats",
        fake_load_or_create_clean_stats,
    )
    monkeypatch.setattr(
        agent,
        "run_data_agent",
        fake_run_data_agent,
    )

    result = agent.answer_query(
        "suyou's best lane",
        max_steps=4,
    )

    assert result["query"] == "suyou's best lane"
    assert result["answer"] == (
        "Based on the current stats table, Suyou is listed under Jungle."
    )
    assert result["confidence"] == "high"
    assert result["data"]["hero_count"] == 2
    assert result["data"]["issue_count"] == 0
    assert len(result["observations"]) == 1


def test_answer_query_passes_custom_max_steps(
    monkeypatch,
    sample_clean_df,
    sample_issues_df,
):
    captured = {}

    def fake_load_or_create_clean_stats():
        return sample_clean_df, sample_issues_df

    def fake_run_data_agent(user_query, df, max_steps):
        captured["max_steps"] = max_steps

        return {
            "answer": "ok",
            "confidence": "medium",
            "observations": [],
        }

    monkeypatch.setattr(
        agent,
        "load_or_create_clean_stats",
        fake_load_or_create_clean_stats,
    )
    monkeypatch.setattr(
        agent,
        "run_data_agent",
        fake_run_data_agent,
    )

    result = agent.answer_query(
        "best exp laners",
        max_steps=2,
    )

    assert captured["max_steps"] == 2
    assert result["answer"] == "ok"
    assert result["confidence"] == "medium"


def test_answer_query_counts_validation_issues(
    monkeypatch,
    sample_clean_df,
):
    issues_df = pd.DataFrame(
        [
            {
                "row_index": 0,
                "hero": "Bad Hero",
                "field": "win_rate",
                "issue": "out_of_range",
                "value": 150,
            }
        ]
    )

    def fake_load_or_create_clean_stats():
        return sample_clean_df, issues_df

    def fake_run_data_agent(user_query, df, max_steps):
        return {
            "answer": "ok",
            "confidence": "medium",
            "observations": [],
        }

    monkeypatch.setattr(
        agent,
        "load_or_create_clean_stats",
        fake_load_or_create_clean_stats,
    )
    monkeypatch.setattr(
        agent,
        "run_data_agent",
        fake_run_data_agent,
    )

    result = agent.answer_query("summarize meta")

    assert result["data"]["hero_count"] == 2
    assert result["data"]["issue_count"] == 1


def test_load_or_create_clean_stats_uses_existing_clean_files(
    monkeypatch,
    tmp_path,
    sample_clean_df,
):
    clean_dir = tmp_path / "clean"
    processed_dir = tmp_path / "processed"
    raw_dir = tmp_path / "raw"

    clean_dir.mkdir()
    processed_dir.mkdir()
    raw_dir.mkdir()

    clean_csv = clean_dir / "stats_cleaned_2026-06-05_120000.csv"
    issues_csv = clean_dir / "stats_issues_2026-06-05_120000.csv"

    sample_clean_df.to_csv(clean_csv, index=False)
    pd.DataFrame(
        columns=["row_index", "hero", "field", "issue", "value"]
    ).to_csv(issues_csv, index=False)

    monkeypatch.setattr(agent, "CLEAN_DIR", clean_dir)
    monkeypatch.setattr(agent, "PROCESSED_DIR", processed_dir)
    monkeypatch.setattr(agent, "RAW_DIR", raw_dir)
    monkeypatch.setattr(agent, "get_today", lambda: "2026-06-05")

    def fail_fetch_page(url):
        raise AssertionError("fetch_page should not be called when clean stats exist")

    monkeypatch.setattr(agent, "fetch_page", fail_fetch_page)

    df_clean, df_issues = agent.load_or_create_clean_stats()

    assert len(df_clean) == 2
    assert len(df_issues) == 0
    assert df_clean.iloc[0]["hero"] == "Suyou"


def test_load_or_create_clean_stats_fetches_when_no_files_exist(
    monkeypatch,
    tmp_path,
):
    clean_dir = tmp_path / "clean"
    processed_dir = tmp_path / "processed"
    raw_dir = tmp_path / "raw"

    monkeypatch.setattr(agent, "CLEAN_DIR", clean_dir)
    monkeypatch.setattr(agent, "PROCESSED_DIR", processed_dir)
    monkeypatch.setattr(agent, "RAW_DIR", raw_dir)
    monkeypatch.setattr(agent, "get_today", lambda: "2026-06-05")
    monkeypatch.setattr(agent, "current_timestamp", lambda: "2026-06-05_120000")

    def fake_fetch_page(url):
        return "<html>fake</html>"

    def fake_extract_stats(html):
        assert html == "<html>fake</html>"
        return [
            {
                "rank": "1",
                "lane": "Jungle",
                "hero": "Suyou",
                "tier": "S",
                "win_rate": "52.1%",
                "ban_rate": "18.4%",
                "pick_rate": "9.2%",
                "roles": "Assassin / Fighter",
            }
        ]

    monkeypatch.setattr(agent, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(agent, "extract_stats", fake_extract_stats)

    df_clean, df_issues = agent.load_or_create_clean_stats()

    assert len(df_clean) == 1
    assert df_clean.iloc[0]["hero"] == "Suyou"
    assert df_clean.iloc[0]["lane"] == "Jungle"
    assert df_clean.iloc[0]["win_rate"] == 52.1
    assert len(df_issues) == 0

    assert (processed_dir / "stats_2026-06-05_120000.csv").exists()
    assert (clean_dir / "stats_cleaned_2026-06-05_120000.csv").exists()
    assert (clean_dir / "stats_issues_2026-06-05_120000.csv").exists()