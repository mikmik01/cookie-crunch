import pandas as pd
import pytest

import app.services.data_agent as data_agent
from app.services.data_agent import AgentLoopError, parse_model_json, run_data_agent


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
        ]
    )


def test_parse_model_json_accepts_plain_json():
    parsed = parse_model_json(
        '{"type": "final_answer", "answer": "ok", "confidence": "high"}'
    )

    assert parsed["type"] == "final_answer"
    assert parsed["answer"] == "ok"


def test_parse_model_json_accepts_fenced_json():
    parsed = parse_model_json(
        """```json
        {"type": "final_answer", "answer": "ok", "confidence": "high"}
        ```"""
    )

    assert parsed["type"] == "final_answer"
    assert parsed["confidence"] == "high"


def test_parse_model_json_rejects_invalid_json():
    with pytest.raises(AgentLoopError, match="valid JSON"):
        parse_model_json("not json")


def test_run_data_agent_tool_call_then_final_answer(monkeypatch, sample_df):
    outputs = [
        {
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
            "reason": "Inspect Suyou row.",
        },
        {
            "type": "final_answer",
            "answer": (
                "Based on the current stats table, Suyou is listed under Jungle."
            ),
            "confidence": "high",
        },
    ]

    def fake_call_agent_model(user_query, observations):
        return outputs.pop(0)

    monkeypatch.setattr(data_agent, "call_agent_model", fake_call_agent_model)

    result = run_data_agent(
        user_query="suyou's best lane",
        df=sample_df,
        max_steps=4,
    )

    assert result["confidence"] == "high"
    assert "Jungle" in result["answer"]
    assert len(result["observations"]) == 1
    assert result["observations"][0]["tool_result"]["ok"] is True
    assert result["observations"][0]["tool_result"]["result"][0]["hero"] == "Suyou"


def test_run_data_agent_returns_low_confidence_after_step_limit(
    monkeypatch,
    sample_df,
):
    def fake_call_agent_model(user_query, observations):
        return {
            "type": "tool_call",
            "tool": "get_schema",
            "args": {},
            "reason": "Inspect schema.",
        }

    monkeypatch.setattr(data_agent, "call_agent_model", fake_call_agent_model)

    result = run_data_agent(
        user_query="what can you answer?",
        df=sample_df,
        max_steps=2,
    )

    assert result["confidence"] == "low"
    assert "step limit" in result["answer"]
    assert len(result["observations"]) == 2


def test_run_data_agent_rejects_unknown_model_output_type(
    monkeypatch,
    sample_df,
):
    def fake_call_agent_model(user_query, observations):
        return {
            "type": "unknown",
        }

    monkeypatch.setattr(data_agent, "call_agent_model", fake_call_agent_model)

    with pytest.raises(AgentLoopError, match="Unsupported model output type"):
        run_data_agent(
            user_query="suyou's best lane",
            df=sample_df,
            max_steps=2,
        )