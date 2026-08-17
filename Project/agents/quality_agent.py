"""
Quality agent.

Implement QualityAgent (extends BaseAgent, name "quality"): for each file it calls the pre-loaded
run_pylint tool for evidence and asks the LLM to score the file's quality. See the problem
description for the analyze() return contract and score scale.
"""
import json
import re

from agents.base_agent import BaseAgent
from tools.pylint_analyzer import run_pylint
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


class QualityAgent(BaseAgent):

    def __init__(self, name="quality"):
        super().__init__(name)
        self.model = get_review_llm()

    def analyze(self, files_data: list) -> list:
        results = []

        for file_data in files_data:
            filename = file_data.get("filename", "unknown.py")
            content = file_data.get("content", "")

            evidence = run_pylint(content)

            prompt = f"""
You are a Python code-quality reviewer.

Use the supplied PyLint result as factual evidence.

File:
{filename}

PyLint evidence:
{json.dumps(evidence, indent=2, default=str)}

Code:
{content}

Return ONLY JSON:

{{
  "score": 0.0,
  "assessment": "..."
}}

Score must be from 0 to 10.
Do not fabricate PyLint findings.
"""

            response = self.model.invoke(prompt)
            text = getattr(response, "content", str(response))
            parsed = _parse_json(text)

            score = _clamp(parsed.get("score", 0), 0, 10)

            total_issues = evidence.get("total_issues")

            if total_issues is None:
                issues = evidence.get("issues", [])
                total_issues = len(issues)

            results.append(
                {
                    "filename": filename,
                    "score": score,
                    "total_issues": total_issues,
                    "assessment": parsed.get(
                        "assessment",
                        text,
                    ),
                }
            )

        return results
