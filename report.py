import pandas as pd

def dataframe_to_text(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "No results found."
    return df.to_string(index=False)

def build_report(
    task_type: str,
    raw_rows: int,
    cleaned_rows: int,
    issue_count: int,
    insight_df: pd.DataFrame,
) -> str:
    title_map = {
        "summarize_meta": "MLBB Meta Summary",
        "find_underrated_heroes": "MLBB Underrated Heroes",
        "find_overbanned_heroes": "MLBB Overbanned Heroes",
    }

    title = title_map.get(task_type, "MLBB Report")

    lines = [
        f"# {title}",
        "",
        "## Data Summary",
        f"- Raw rows: {raw_rows}",
        f"- Cleaned rows: {cleaned_rows}",
        f"- Validation issues: {issue_count}",
        "",
    ]

    lines.append("## Results")
    lines.append(dataframe_to_text(insight_df))

    return "\n".join(lines)