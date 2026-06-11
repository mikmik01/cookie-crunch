import os
import re
import json

import google.generativeai as genai
from dotenv import load_dotenv

from app.core.config import SYSTEM_PROMPT, DEFAULT_PLAN

load_dotenv()

MODEL = "gemini-2.5-flash"


def get_plan(user_query: str) -> dict:
    try:
        return get_plan_from_llm(user_query)
    except Exception:
        return DEFAULT_PLAN.copy()


def get_plan_from_llm(user_query: str) -> dict:
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not found in environment")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(MODEL)

    response = model.generate_content(
        SYSTEM_PROMPT + "\nUser query: " + user_query
    )

    text = response.text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    return json.loads(text)