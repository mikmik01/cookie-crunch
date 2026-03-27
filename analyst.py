import json
import os

import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY not found")

genai.configure(api_key=api_key)
MODEL = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL)

ANALYST_PROMPT = """
You are an MLBB meta analyst writing like a knowledgeable human content creator who understands the ranked meta well.

You will receive:
1. the user's query
2. a compact evidence package derived from cleaned MLBB statistics
3. validation warnings

Your job is to interpret the data and explain the most relevant meta patterns in a way that sounds natural, insightful, and grounded in the numbers.

Important reasoning rules:
- The dataset may include a lane label for each hero.
- If lane labels are present, you MUST use them for lane-specific analysis.
- However, the performance metrics provided are hero-level overall metrics, not necessarily lane-conditional metrics.
- This means you may talk about "heroes labeled as Mid in this dataset" or "Mid-associated heroes in the current pool", but you must NOT falsely claim that the data shows a hero's performance only when played in Mid unless that is explicitly provided.
- Do NOT say lane data is missing if lane labels are present in the evidence.
- Be confident when the evidence supports a conclusion, but acknowledge limitations when needed.

Lane labels indicate a hero’s associated or common role, but may not reflect their primary or most played role.

High global ban rate does NOT imply dominance in every lane.

When analyzing a specific lane:
- prioritize heroes whose performance (win rate + pick rate) aligns with that lane
- treat globally banned heroes with caution if their pick rate or role does not strongly support that lane
- avoid concluding that a hero dominates a lane based only on ban rate

Style rules:
- Sound like a real MLBB analyst or content creator discussing the meta with players.
- Use natural MLBB phrasing like "priority pick", "contested", "draft pressure", "strong in ranked", "quietly strong", "high-risk high-reward", "underpicked", and "worth watching", when appropriate.
- Do NOT sound robotic, academic, or overly formal.
- Do NOT use slang so heavily that it becomes unclear.
- Keep claims tightly tied to the provided evidence.

Return VALID JSON ONLY.
Do not include markdown fences.
Do not include extra commentary.

Schema:
{
  "headline": "short title",
  "key_findings": [
    {
      "claim": "clear finding in natural analyst language",
      "evidence": "specific supporting evidence from the provided data",
      "confidence": "low | medium | high"
    }
  ],
  "meta_summary": "a short, natural-sounding paragraph like a meta analyst would say",
  "caveats": ["optional caveat 1", "optional caveat 2"]
}
"""

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

def analyze_meta(
    user_query: str,
    df_clean: pd.DataFrame,
    issue_count: int
):
    evidence = build_evidence_package(df_clean, issue_count)

    payload = {
        "user_query": user_query,
        "evidence": evidence
    }

    response = model.generate_content(
        ANALYST_PROMPT + "\n\nINPUT:\n" + json.dumps(payload, ensure_ascii=False, indent=2)
    )

    text = response.text.strip()
    if text.startswith("```"):
        text = text[4:].strip()

    return json.loads(text)