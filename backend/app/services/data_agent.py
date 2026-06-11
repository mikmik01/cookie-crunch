from typing import Any

import pandas as pd

import json
import os
import re

import google.generativeai as genai
from dotenv import load_dotenv

from app.services.data_tools import aggregate_rows, filter_rows, get_schema
from app.schemas.schemas import TOOL_NAMES

from app.services.agent_prompts import build_agent_prompt
from app.schemas.schemas import build_tool_context

load_dotenv()


class ToolExecutionError(Exception):
    """Raised when a tool call cannot be safely executed."""


def execute_tool_call(
    df: pd.DataFrame,
    tool_call: dict[str, Any],
) -> dict[str, Any]:
    """Execute a single safe data-agent tool call.

    Expected tool_call shape:
    {
        "tool": "filter_rows",
        "args": {
            "filters": [...],
            "sort": [...],
            "limit": 10
        }
    }

    Returns:
    {
        "tool": "filter_rows",
        "ok": true,
        "result": [...]
    }

    If execution fails, this returns ok=false instead of raising, so the
    future LLM agent can observe the error and recover.
    """
    if not isinstance(tool_call, dict):
        raise ToolExecutionError("tool_call must be a dictionary")

    tool_name = tool_call.get("tool")
    args = tool_call.get("args", {})

    if tool_name not in TOOL_NAMES:
        raise ToolExecutionError(f"Unsupported tool: {tool_name}")

    if not isinstance(args, dict):
        raise ToolExecutionError("tool_call args must be a dictionary")

    try:
        if tool_name == "get_schema":
            result = get_schema()

        elif tool_name == "filter_rows":
            result = filter_rows(
                df=df,
                filters=args.get("filters"),
                sort=args.get("sort"),
                limit=args.get("limit", 10),
            )

        elif tool_name == "aggregate_rows":
            result = aggregate_rows(
                df=df,
                group_by=args["group_by"],
                metrics=args["metrics"],
                sort=args.get("sort"),
                limit=args.get("limit", 10),
            )

        else:
            raise ToolExecutionError(f"No executor implemented for tool: {tool_name}")

        return {
            "tool": tool_name,
            "ok": True,
            "result": result,
        }

    except Exception as exc:
        return {
            "tool": tool_name,
            "ok": False,
            "error": str(exc),
            "result": None,
        }


def execute_tool_calls(
    df: pd.DataFrame,
    tool_calls: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Execute multiple tool calls sequentially.

    This is useful later when the LLM returns several tool calls in one step.
    """
    if not isinstance(tool_calls, list):
        raise ToolExecutionError("tool_calls must be a list")

    return [
        execute_tool_call(df=df, tool_call=tool_call)
        for tool_call in tool_calls
    ]


class AgentLoopError(Exception):
    """Raised when the data agent loop cannot continue safely."""


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def parse_model_json(text: str) -> dict[str, Any]:
    """Parse model output as JSON."""
    try:
        return json.loads(_strip_json_fences(text))
    except json.JSONDecodeError as exc:
        raise AgentLoopError(f"Model did not return valid JSON: {exc}") from exc


def call_agent_model(
    user_query: str,
    observations: list[dict],
) -> dict[str, Any]:
    """Call the LLM and parse its JSON response."""
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise AgentLoopError("GOOGLE_API_KEY not found in environment")

    genai.configure(api_key=api_key)

    MODEL = "gemini-2.5-flash"
    model = genai.GenerativeModel(MODEL)

    prompt = build_agent_prompt(
        user_query=user_query,
        tool_context=build_tool_context(),
        observations=observations,
    )

    response = model.generate_content(prompt)

    return parse_model_json(response.text)


def run_data_agent(
    user_query: str,
    df: pd.DataFrame,
    max_steps: int = 4,
) -> dict[str, Any]:
    """Run a small tool-using data agent.

    Flow:
    1. Ask model what to do.
    2. If model returns tool_call, execute safe backend tool.
    3. Add tool result to observations.
    4. Ask model again.
    5. Stop when model returns final_answer.

    Returns:
    {
        "answer": "...",
        "confidence": "medium",
        "observations": [...]
    }
    """
    observations: list[dict[str, Any]] = []

    for step in range(max_steps):
        model_output = call_agent_model(
            user_query=user_query,
            observations=observations,
        )

        output_type = model_output.get("type")

        if output_type == "tool_call":
            tool_name = model_output.get("tool")
            args = model_output.get("args", {})

            tool_result = execute_tool_call(
                df=df,
                tool_call={
                    "tool": tool_name,
                    "args": args,
                },
            )

            observations.append(
                {
                    "step": step + 1,
                    "model_output": model_output,
                    "tool_result": tool_result,
                }
            )

            continue

        if output_type == "final_answer":
            return {
                "answer": model_output.get("answer", ""),
                "confidence": model_output.get("confidence", "low"),
                "observations": observations,
            }

        raise AgentLoopError(f"Unsupported model output type: {output_type}")

    return {
        "answer": (
            "I could not complete the analysis within the tool-use step limit."
        ),
        "confidence": "low",
        "observations": observations,
    }