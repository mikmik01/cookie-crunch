import pandas as pd


def rank_candidates(
    df: pd.DataFrame,
    task_type: str,
    top_n: int | None = None,
) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    ranked = df.copy()

    if task_type == "find_underrated_heroes":
        ranked = ranked.sort_values(
            ["win_rate", "pick_rate", "ban_rate"],
            ascending=[False, True, True],
        )

    elif task_type == "find_overbanned_heroes":
        ranked = ranked.sort_values(
            ["ban_rate", "win_rate", "pick_rate"],
            ascending=[False, True, True],
        )

    else:
        if "rank" in ranked.columns:
            ranked = ranked.sort_values("rank", ascending=True)
        else:
            ranked = ranked.sort_values("pick_rate", ascending=False)

    if top_n:
        ranked = ranked.head(top_n)

    return ranked.reset_index(drop=True)