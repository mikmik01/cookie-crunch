import pandas as pd

def get_top_win_rate(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    return (
        df.sort_values(by="win_rate", ascending=False)
        .loc[:, ["hero", "lane", "tier", "win_rate", "pick_rate", "ban_rate"]]
        .head(top_n)
        .reset_index(drop=True)
    )

def get_underrated_heroes(
    df: pd.DataFrame,
    lane: str | None = None,
    min_win_rate: float = 52.0,
    max_pick_rate: float = 10.0,
    top_n: int = 10,
) -> pd.DataFrame:
    out = df.copy()

    if lane:
        out = out[out["lane"].str.lower() == lane.lower()]

    out = out[
        (out["win_rate"] >= min_win_rate) &
        (out["pick_rate"] <= max_pick_rate)
    ]

    return (
        out.sort_values(by=["win_rate", "pick_rate"], ascending=[False, True])
        .loc[:, ["hero", "lane", "tier", "win_rate", "pick_rate", "ban_rate"]]
        .head(top_n)
        .reset_index(drop=True)
    )

def get_overbanned_heroes(
    df: pd.DataFrame,
    lane: str | None = None,
    min_ban_rate: float = 30.0,
    max_win_rate: float = 52.0,
    top_n: int = 10,
) -> pd.DataFrame:
    out = df.copy()

    if lane:
        out = out[out["lane"].str.lower() == lane.lower()]

    out = out[
        (out["ban_rate"] >= min_ban_rate) &
        (out["win_rate"] <= max_win_rate)
    ]

    return (
        out.sort_values(by=["ban_rate", "win_rate"], ascending=[False, True])
        .loc[:, ["hero", "lane", "tier", "win_rate", "pick_rate", "ban_rate"]]
        .head(top_n)
        .reset_index(drop=True)
    )

def run_insight_task(df: pd.DataFrame, plan: dict) -> pd.DataFrame:
    task_type = plan["task_type"]
    f = plan["filters"]

    lane = f["lane"]
    top_n = f["top_n"] or 10

    if task_type == "find_underrated_heroes":
        return get_underrated_heroes(
            df,
            lane=lane,
            min_win_rate=f["min_win_rate"] if f["min_win_rate"] is not None else 52.0,
            max_pick_rate=f["max_pick_rate"] if f["max_pick_rate"] is not None else 10.0,
            top_n=top_n,
        )

    if task_type == "find_overbanned_heroes":
        return get_overbanned_heroes(
            df,
            lane=lane,
            min_ban_rate=f["min_ban_rate"] if f["min_ban_rate"] is not None else 30.0,
            max_win_rate=f["max_win_rate"] if f["max_win_rate"] is not None else 52.0,
            top_n=top_n,
        )

    return get_top_win_rate(df, top_n=top_n)