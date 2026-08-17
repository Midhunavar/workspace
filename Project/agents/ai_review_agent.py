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
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)

        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

    return {}


def _clamp(value, low, high):
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = low

    return max(low, min(high, value))


class AIReviewAgent(BaseAgent):

    def __init__(self, name="ai_review"):
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

            text = getattr(response, "content", str(response))
            parsed = _parse_json(text)

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
                    "raw_response": text,
                }
            )

        return results
