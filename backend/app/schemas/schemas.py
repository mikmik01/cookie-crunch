from backend.app.services.data_tools import (
    ALLOWED_AGG_FUNCS,
    ALLOWED_COLUMNS,
    ALLOWED_DIRECTIONS,
    ALLOWED_OPERATORS,
    get_schema,
)

def _sorted(values: set[str]) -> list[str]:
    return sorted(values)

TOOL_SCHEMAS = [
    {
        "name": "get_schema",
        "description": (
            "Return the dataset columns, their meanings, and important data "
            "limitations. Use this when the query is ambiguous or when the "
            "agent needs to inspect what data is available."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "name": "filter_rows",
        "description": (
            "Filter and optionally sort hero statistic rows using generic "
            "column operations. Use this for hero lookups, lane-specific row "
            "inspection, top heroes, highest rates, most picked heroes, and "
            "similar row-level questions."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "filters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "column": {
                                "type": "string",
                                "enum": _sorted(ALLOWED_COLUMNS),
                            },
                            "operator": {
                                "type": "string",
                                "enum": _sorted(ALLOWED_OPERATORS),
                            },
                            "value": {
                                "type": ["string", "number", "integer"],
                            },
                        },
                        "required": ["column", "operator", "value"],
                        "additionalProperties": False,
                    },
                    "default": [],
                },
                "sort": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "column": {
                                "type": "string",
                                "enum": _sorted(ALLOWED_COLUMNS),
                            },
                            "direction": {
                                "type": "string",
                                "enum": _sorted(ALLOWED_DIRECTIONS),
                            },
                        },
                        "required": ["column", "direction"],
                        "additionalProperties": False,
                    },
                    "default": [],
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                },
            },
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "name": "aggregate_rows",
        "description": (
            "Group rows and compute summary statistics. Use this for lane-level "
            "or tier-level summaries, averages, medians, maximums, minimums, "
            "and counts."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "group_by": {
                    "type": "string",
                    "enum": _sorted(ALLOWED_COLUMNS),
                },
                "metrics": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "column": {
                                "type": "string",
                                "enum": _sorted(ALLOWED_COLUMNS),
                            },
                            "function": {
                                "type": "string",
                                "enum": _sorted(ALLOWED_AGG_FUNCS),
                            },
                        },
                        "required": ["column", "function"],
                        "additionalProperties": False,
                    },
                    "minItems": 1,
                },
                "sort": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "column": {"type": "string"},
                            "direction": {
                                "type": "string",
                                "enum": _sorted(ALLOWED_DIRECTIONS),
                            },
                        },
                        "required": ["column", "direction"],
                        "additionalProperties": False,
                    },
                    "default": [],
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                },
            },
            "required": ["group_by", "metrics"],
            "additionalProperties": False,
        },
    },
]


TOOL_NAMES = {schema["name"] for schema in TOOL_SCHEMAS}


def get_tool_schemas() -> list[dict]:
    return [dict(schema) for schema in TOOL_SCHEMAS]


def build_tool_context() -> dict:
    """Return the full tool context for the agent prompt."""
    return {
        "dataset_schema": get_schema(),
        "tool_schemas": get_tool_schemas(),
    }

STAT_FIELDS = [
    "rank",
    "lane",
    "hero",
    "tier",
    "win_rate",
    "ban_rate",
    "pick_rate",
    "roles",
]

STAT_OUTPUT_FIELDS = STAT_FIELDS + ["rank_filter"]