import json
import os
import re

import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv

from evidence import build_evidence_package

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY not found")

genai.configure(api_key=api_key)
MODEL = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL)

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
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    return json.loads(text)



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