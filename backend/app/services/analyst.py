import json
import os
import re

import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv

from backend.app.services.evidence import build_evidence_package

from pydantic import BaseModel, ValidationError

class AnalystFinding(BaseModel):
    claim: str
    evidence: str
    confidence: str

class AnalystResult(BaseModel):
    headline: str
    key_findings: list[AnalystFinding]
    meta_summary: str
    caveats: list[str] = []

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

    try:
        parsed = json.loads(text)
        validated = AnalystResult.model_validate(parsed)
        return validated.model_dump()
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValueError(f"Invalid analyst output schema: {exc}") from exc



ANALYST_PROMPT = """
You are an MLBB hero recommendation formatter.

You will receive:
1. the user's query
2. a compact evidence package derived from cleaned MLBB statistics
3. validation warnings

Your job is to return concise structured data for a frontend.

Use only the provided evidence.
Do not invent heroes, lanes, tiers, or statistics.
Do not explain your choices.
Do not include summaries.
Do not include caveats.
Do not include markdown.

Each recommended hero must include only:
- hero
- lane
- tier
- win_rate
- pick_rate
- ban_rate

For role_summary:
- Group heroes by lane.
- Include up to 3 heroes per lane.
- Use only lanes present in the evidence.
- Each hero object must include only hero, tier, win_rate, pick_rate, and ban_rate.

Recommendation rules:
- For general meta queries, return the strongest practical heroes from the evidence.
- For underrated hero queries, prioritize high win_rate and low pick_rate.
- For overbanned hero queries, prioritize high ban_rate with weaker win_rate.
- For lane-specific queries, only return heroes matching that lane.
- For strongest heroes by role, populate role_summary clearly.
- Round numeric values to 2 decimal places.

Return VALID JSON ONLY.
Do not include markdown fences.
Do not include extra commentary.

Schema:
{
  "recommendations": [
    {
      "hero": "hero name",
      "lane": "lane label",
      "tier": "tier label or null",
      "win_rate": 0.0,
      "pick_rate": 0.0,
      "ban_rate": 0.0
    }
  ],
  "role_summary": [
    {
      "lane": "lane label",
      "heroes": [
        {
          "hero": "hero name",
          "tier": "tier label or null",
          "win_rate": 0.0,
          "pick_rate": 0.0,
          "ban_rate": 0.0
        }
      ]
    }
  ]
}

Output size rules:
- recommendations should usually contain 5 to 10 heroes.
- role_summary should include up to 3 heroes per lane.
- If role_summary is not relevant, return an empty list.
"""