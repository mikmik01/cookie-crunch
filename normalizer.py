import pandas as pd

def normalize_text(val) -> str:
    if pd.isna(val):
        return ""
    return " ".join(str(val).strip().split())

def normalize_rate(val) -> float | None:
    if pd.isna(val):
        return None
    
    text = normalize_text(val).replace("%", "")
    if text == "":
        return None
    
    try:
        return float(text)
    except ValueError:
        return None

def normalize_rank(val) -> int | None:
    if pd.isna(val):
        return None
    
    text = normalize_text(val).replace("%", "")
    if text == "":
        return None
    
    try:
        return float(text)
    except ValueError:
        return None
    
def normalize_roles(value) -> str:
    text = normalize_text(value)
    if not text:
        return ""

    parts = [p.strip() for p in text.replace("/", ",").split(",")]
    parts = [p for p in parts if p]
    return ", ".join(parts)


def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    out["rank"] = out["rank"].apply(normalize_rank)
    out["lane"] = out["lane"].apply(normalize_text)
    out["hero"] = out["hero"].apply(normalize_text)
    out["tier"] = out["tier"].apply(normalize_text)
    out["win_rate"] = out["win_rate"].apply(normalize_rate)
    out["ban_rate"] = out["ban_rate"].apply(normalize_rate)
    out["pick_rate"] = out["pick_rate"].apply(normalize_rate)
    out["roles"] = out["roles"].apply(normalize_roles)

    return out