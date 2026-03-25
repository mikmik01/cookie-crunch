from pathlib import Path

SRC_URL = "https://mlbb.gg/statistics"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"

TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36 "
    "Edg/120.0.0.0"
)

PLAYWRIGHT_WAIT_MS = 5000
PLAYWRIGHT_TIMEOUT_MS = 30000

SYSTEM_PROMPT = """
You are a planning module for an MLBB meta analysis workflow.

You must return valid JSON only.
Do not include markdown fences.
Do not include any extra commentary.

Allowed task_type values:
- summarize_meta
- find_underrated_heroes
- find_overbanned_heroes

Allowed steps:
- fetch_extract
- normalize
- validate
- generate_insights
- build_report

Return this JSON shape:
{
  "task_type": "summarize_meta",
  "filters": {
    "lane": null,
    "hero": null,
    "min_win_rate": null,
    "max_win_rate": null,
    "min_pick_rate": null,
    "max_pick_rate": null,
    "min_ban_rate": null,
    "max_ban_rate": null,
    "top_n": 10
  },
  "steps": [
    "fetch_extract",
    "normalize",
    "validate",
    "generate_insights",
    "build_report"
  ],
  "reasoning_summary": "short explanation"
}

Interpret user intent conservatively.
If the user asks for underrated heroes, prefer:
- task_type = find_underrated_heroes
- min_win_rate around 52
- max_pick_rate around 10

If the user asks for overbanned heroes, prefer:
- task_type = find_overbanned_heroes
- min_ban_rate around 30
- max_win_rate around 52

If the user asks for a general overview, use summarize_meta.
"""

ALLOWED_TASK_TYPES = {
    "summarize_meta",
    "find_underrated_heroes",
    "find_overbanned_heroes",
}

ALLOWED_STEPS = [
    "fetch_extract",
    "normalize",
    "validate",
    "generate_insights",
    "build_report",
]

DEFAULT_PLAN = {
    "task_type": "summarize_meta",
    "filters": {
        "lane": None,
        "hero": None,
        "min_win_rate": None,
        "max_win_rate": None,
        "min_pick_rate": None,
        "max_pick_rate": None,
        "min_ban_rate": None,
        "max_ban_rate": None,
        "top_n": 10,
    },
    "steps": [
        "fetch_extract",
        "normalize",
        "validate",
        "generate_insights",
        "build_report",
    ],
    "reasoning_summary": "Fallback summary plan.",
}

REQUIRED_COLUMNS = [
    "rank", "lane", "hero", "tier",
    "win_rate", "ban_rate", "pick_rate", "roles"
]

ALLOWED_TIERS = {"SS", "S", "A", "B", "C", "D"}