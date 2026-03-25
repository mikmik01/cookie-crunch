import os
import json
from typing import Any
import google.generativeai as genai
from config import SYSTEM_PROMPT
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY not found in environment")
genai.configure(api_key=api_key)
MODEL = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL)

def get_plan_from_llm(user_query: str) -> dict:
    response = model.generate_content(
        SYSTEM_PROMPT + "\nUser query: " + user_query
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.strip("```").strip("json").strip()

    return json.loads(text)