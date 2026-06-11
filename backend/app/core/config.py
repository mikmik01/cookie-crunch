from pathlib import Path
from urllib.parse import urlencode

SRC_URL = "https://mlbb.gg/statistics"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"
PROCESSED_DIR = DATA_DIR / "processed"
REPORT_DIR = DATA_DIR / "reports"

RANK_FILTERS = [
    "Epic",
    "Legend",
    "Mythic",
    "Mythical Honor",
    "Mythical Glory Plus",
]

def build_stats_url(rank_filter: str | None = None) -> str:
    params = {"mode": "rank"}

    if rank_filter:
        params["rank_filter"] = rank_filter

    return f"{SRC_URL}?{urlencode(params)}"

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
You are a planning module for an MLBB hero statistics and recommendation workflow.

You must return valid JSON only.
Do not include markdown fences.
Do not include extra commentary.

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
    "top_n": 5
  },
  "steps": [
    "fetch_extract",
    "normalize",
    "validate",
    "generate_insights",
    "build_report"
  ],
  "reasoning_summary": "short reason"
}

Planning rules:
- If the user asks for recommended heroes, strongest heroes, best heroes, or meta heroes, use summarize_meta.
- If the user asks for underrated heroes, use find_underrated_heroes, min_win_rate around 52, max_pick_rate around 10.
- If the user asks for overbanned heroes, use find_overbanned_heroes, min_ban_rate around 30, max_win_rate around 52.
- If the user asks for a specific lane, set lane to that lane.
- If the user asks for a specific hero, set hero to that hero.
- If the user asks for strongest heroes by role, best heroes per lane, or a role overview, leave lane as null and set top_n to 50.
- Do not add unnecessary filters.
- Keep reasoning_summary under 8 words.

Valid lane values:
- Exp
- Gold
- Jungle
- Mid
- Roam
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
        "top_n": 5,
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
    "rank_filter",
    "rank",
    "lane",
    "hero",
    "tier",
    "win_rate",
    "ban_rate",
    "pick_rate",
    "roles",
]

ALLOWED_TIERS = {"SS", "S", "A", "B", "C", "D"}