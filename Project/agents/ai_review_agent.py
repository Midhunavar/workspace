"""
AI review agent.

Implement AIReviewAgent (extends BaseAgent, name "ai_review"): the holistic LLM reviewer that reads
each file directly (no tool) and returns an overall score and confidence. See the problem
description for the analyze() return contract and scale.
"""
import json
import re

from agents.base_agent import BaseAgent
from utils.gemini_client import get_review_llm


def _parse_json(text):
    # Ensure we have a string to feed to json.loads (some SDK responses may be lists/dicts)
    if not isinstance(text, str):
        try:
            text = json.dumps(text)
        except Exception:
            text = str(text)

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        # fallback: try to extract an embedded JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                return {}
        else:
            return {}

    # If LLM returned a list, try to find the first dict element
    if isinstance(parsed, list):
        for item in parsed:
            if isinstance(item, dict):
                parsed = item
                break
        else:
            return {}
    # If the dict contains a nested JSON string in common fields, parse that
    if isinstance(parsed, dict):
        for key in ("text", "content", "message"):
            val = parsed.get(key)
            if isinstance(val, str):
                val_str = val.strip()
                if val_str.startswith("{") or val_str.startswith("["):
                    try:
                        inner = json.loads(val_str)
                    except Exception:
                        continue
                    if isinstance(inner, dict):
                        return inner
                    if isinstance(inner, list):
                        for item in inner:
                            if isinstance(item, dict):
                                return item
        return parsed

    return {}


def _clamp(value, low, high):
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = low

    return max(low, min(high, value))


class AIReviewAgent(BaseAgent):

    def __init__(self, config, name="ai_review"):
        super().__init__(name)
        self.model = get_review_llm()

    def analyze(self, files_data: list) -> list:
        results = []

        for file_data in files_data:
            filename = file_data.get("filename", "unknown.py")
            content = file_data.get("content", "")

            prompt = f"""
You are a senior Python code reviewer.

Perform a holistic review of the following code.

File:
{filename}

Code:
{content}

Evaluate:
- correctness
- maintainability
- security awareness
- readability
- architecture
- error handling
- Python best practices

Return ONLY JSON:

{{
  "overall_score": 0.0,
  "confidence": 0.0,
  "assessment": "..."
}}

overall_score and confidence must be between 0 and 1.
"""

            response = self.model.invoke(prompt)

            raw_content = getattr(response, "content", response)
            parsed = _parse_json(raw_content)
            # normalize raw_response as a string for tests/UI
            if isinstance(raw_content, str):
                raw_text = raw_content
            else:
                try:
                    raw_text = json.dumps(raw_content)
                except Exception:
                    raw_text = str(raw_content)

            results.append(
                {
                    "filename": filename,
                    "overall_score": _clamp(
                        parsed.get("overall_score", 0),
                        0,
                        1,
                    ),
                    "confidence": _clamp(
                        parsed.get("confidence", 0),
                        0,
                        1,
                    ),
                    "raw_response": raw_text,
                }
            )

        return results
