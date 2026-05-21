import os
import re
import json
from typing import Any
import google.generativeai as genai
from backend.app.core.config import SYSTEM_PROMPT, DEFAULT_PLAN
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY not found in environment")
genai.configure(api_key=api_key)
MODEL = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL)

def get_plan(user_query: str) -> dict:
    try:
        return get_plan_from_llm(user_query)
    except Exception:
        return DEFAULT_PLAN.copy()

def get_plan_from_llm(user_query: str) -> dict:
    response = model.generate_content(
        SYSTEM_PROMPT + "\nUser query: " + user_query
    )

    text = response.text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    return json.loads(text)