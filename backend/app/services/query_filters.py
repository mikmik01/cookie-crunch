import pandas as pd
import re

LANE_ALIASES = {
    "roam": "Roam",
    "roamer": "Roam",
    "roamers": "Roam",
    "support": "Roam",
    "supports": "Roam",

    "gold": "Gold",
    "gold lane": "Gold",
    "gold laner": "Gold",
    "gold laners": "Gold",
    "marksman": "Gold",
    "marksmen": "Gold",
    "mm": "Gold",

    "exp": "Exp",
    "exp lane": "Exp",
    "exp laner": "Exp",
    "exp laners": "Exp",
    "xp": "Exp",
    "offlane": "Exp",
    "offlaner": "Exp",
    "offlaners": "Exp",

    "jungle": "Jungle",
    "jungler": "Jungle",
    "junglers": "Jungle",
    "jg": "Jungle",

    "mid": "Mid",
    "mid lane": "Mid",
    "mid laner": "Mid",
    "mid laners": "Mid",
    "midlaner": "Mid",
    "midlaners": "Mid",
    "mage": "Mid",
    "mages": "Mid",
}


def normalize_lane(value: str | None) -> str | None:
    if not value:
        return None

    text = str(value).strip().lower()
    return LANE_ALIASES.get(text, value)


def infer_lane_from_query(query: str) -> str | None:
    text = re.sub(r"[^a-zA-Z0-9]+", " ", query.lower()).strip()

    for alias, lane in sorted(LANE_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        pattern = rf"\b{re.escape(alias)}\b"
        if re.search(pattern, text):
            return lane

    return None


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    f = filters

    if f.get("lane"):
        target_lane = normalize_lane(f["lane"])

        df = df[
            df["lane"]
            .astype(str)
            .apply(normalize_lane)
            == target_lane
        ]

    if f.get("hero"):
        df = df[df["hero"].str.lower() == f["hero"].lower()]

    if f.get("min_win_rate") is not None:
        df = df[df["win_rate"] >= f["min_win_rate"]]

    if f.get("max_win_rate") is not None:
        df = df[df["win_rate"] <= f["max_win_rate"]]

    if f.get("min_pick_rate") is not None:
        df = df[df["pick_rate"] >= f["min_pick_rate"]]

    if f.get("max_pick_rate") is not None:
        df = df[df["pick_rate"] <= f["max_pick_rate"]]

    if f.get("min_ban_rate") is not None:
        df = df[df["ban_rate"] >= f["min_ban_rate"]]

    if f.get("max_ban_rate") is not None:
        df = df[df["ban_rate"] <= f["max_ban_rate"]]

    if f.get("rank_filter") and "rank_filter" in df.columns:
        df = df[
            df["rank_filter"].astype(str).str.lower()
            == f["rank_filter"].lower()
        ]
        
    return df.head(f.get("top_n", 5)) if f.get("top_n") else df