import pandas as pd

REQUIRED_COLUMNS = [
    "rank", "lane", "hero", "tier",
    "win_rate", "ban_rate", "pick_rate", "roles"
]

ALLOWED_TIERS = {"SS", "S", "A", "B", "C", "D"}

def validate_df(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    issues = []

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            issues.append({
                "row_index": None,
                "hero": None,
                "field": col,
                "issue": "missing_column",
                "value": None,
            })
    
    if issues:
        return df.iloc[0:0].copy(), pd.DataFrame(issues)
    
    for i, row in df.iterrows():
        hero = row["hero"]

        if row["rank"] is None or pd.isna(row["rank"]) or row["rank"] < 1:
            issues.append({
                "row_index": i, "hero": hero, "field": "rank",
                "issue": "invalid_rank", "value": row["rank"]
            })
        
        for field in ["win_rate", "ban_rate", "pick_rate"]:
            value = row[field]
            if value is None or pd.isna(value):
                issues.append({
                    "row_index": i, "hero": hero, "field": field,
                    "issue": "missing_value", "value": value
                })
            elif not (0 <= value <= 100):
                issues.append({
                    "row_index": i, "hero": hero, "field": field,
                    "issue": "out_of_range", "value": value
                })
        
        if not str(hero).strip():
            issues.append({
                "row_index": i, "hero": hero, "field": "hero",
                "issue": "empty_hero", "value": hero
            })
        
        tier = str(row["tier"]).strip()
        if tier and tier not in ALLOWED_TIERS:
            issues.append({
                "row_index": i, "hero": hero, "field": "tier",
                "issue": "unexpected_tier", "value": tier
            })
    
    dupes = df[df.duplicated(subset=["hero"], keep=False)]
    for idx, row in dupes.iterrows():
        issues.append({
            "row_index": idx, "hero": row["hero"], "field": "hero",
            "issue": "duplicate_hero", "value": row["hero"]
        })

    issues_df = pd.DataFrame(issues)

    invalid_rows = set(issues_df["row_index"].dropna().astype(int).tolist()) if not issues_df.empty else set()
    cleaned_df = df.drop(index=list(invalid_rows)).copy()

    return cleaned_df, issues_df