import pandas as pd

def df_to_records(df: pd.DataFrame, columns: list[str], top_n: int) -> list[dict]:
    available = [c for c in columns if c in df.columns]
    if not available:
        return []
    return df.loc[:, available].head(top_n).to_dict(orient="records")

def build_evidence_package(df_clean: pd.DataFrame, issue_count: int) -> dict:
    evidence = {
        "row_count": int(len(df_clean)),
        "issue_count": int(issue_count),
        "summary_stats": {
            "win_rate_mean": round(float(df_clean["win_rate"].mean()), 2) if not df_clean.empty else None,
            "ban_rate_mean": round(float(df_clean["ban_rate"].mean()), 2) if not df_clean.empty else None,
            "pick_rate_mean": round(float(df_clean["pick_rate"].mean()), 2) if not df_clean.empty else None,
            "win_rate_median": round(float(df_clean["win_rate"].median()), 2) if not df_clean.empty else None,
            "ban_rate_median": round(float(df_clean["ban_rate"].median()), 2) if not df_clean.empty else None,
            "pick_rate_median": round(float(df_clean["pick_rate"].median()), 2) if not df_clean.empty else None,
        },
        "lane_distribution": df_clean["lane"].value_counts().to_dict(),
        "top_win_rate": df_to_records(
            df_clean.sort_values("win_rate", ascending=False),
            ["hero", "tier", "win_rate", "pick_rate", "ban_rate"],
            12,
        ),
        "top_ban_rate": df_to_records(
            df_clean.sort_values("ban_rate", ascending=False),
            ["hero", "tier", "ban_rate", "win_rate", "pick_rate"],
            12,
        ),
        "top_pick_rate": df_to_records(
            df_clean.sort_values("pick_rate", ascending=False),
            ["hero", "tier", "pick_rate", "win_rate", "ban_rate"],
            12,
        ),
        "high_win_low_pick": df_to_records(
            df_clean.sort_values(["win_rate", "pick_rate"], ascending=[False, True]),
            ["hero", "tier", "win_rate", "pick_rate", "ban_rate"],
            12,
        ),
    }
    return evidence