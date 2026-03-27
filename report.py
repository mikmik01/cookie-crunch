import pandas as pd

def dataframe_to_text(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "No results found."
    return df.to_string(index=False)

def build_report(
    analyst_output: dict
) -> str:
    lines = [
        f"# {analyst_output.get('headline', 'MLBB Meta Report')}",
        ""
    ]

    key_findings = analyst_output.get("key_findings", [])
    if key_findings:
        lines.append("## Key Findings")
        for i, item in enumerate(key_findings, start=1):
            lines.append(f"### Finding {i}")
            lines.append(f"- {item.get('claim', '')}")
            lines.append(f"- {item.get('evidence', '')}")
            lines.append(f"- Confidence: {item.get('confidence', '')}")
            lines.append("")
    
    meta_summary = analyst_output.get("meta_summary")
    if meta_summary:
        lines.append("## Summary")
        lines.append(meta_summary)
        lines.append("")

    # caveats = analyst_output.get("caveats", [])
    # if caveats:
    #     lines.append("## Caveats")
    #     for c in caveats:
    #         lines.append(f"- {c}")

    return "\n".join(lines)