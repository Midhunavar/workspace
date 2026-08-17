"""
Coverage agent.

Implement CoverageAgent (extends BaseAgent, name "coverage"): for each file it calls the pre-loaded
estimate_coverage tool for evidence and reports a coverage percentage. See the problem description
for the analyze() return contract and scale.
"""
import json
import re

from agents.base_agent import BaseAgent
from tools.coverage_analyzer import estimate_coverage
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


class CoverageAgent(BaseAgent):

    def __init__(self, name="coverage"):
        super().__init__(name)
        self.model = get_review_llm()

    def analyze(self, files_data: list) -> list:
        results = []

        for file_data in files_data:
            filename = file_data.get("filename", "unknown.py")
            content = file_data.get("content", "")

            evidence = estimate_coverage(content)

            prompt = f"""
You are a Python test-coverage reviewer.

Use the supplied AST-based coverage estimate as factual evidence.

File:
{filename}

Coverage evidence:
{json.dumps(evidence, indent=2, default=str)}

Code:
{content}

Return ONLY JSON:

{{
  "coverage_percent": 0.0,
  "assessment": "..."
}}

coverage_percent must be between 0 and 100.
Do not invent testable items.
"""

            response = self.model.invoke(prompt)
            text = getattr(response, "content", str(response))
            parsed = _parse_json(text)

            coverage = _clamp(
                parsed.get("coverage_percent", 0),
                0,
                100,
            )

            total_items = evidence.get(
                "total_testable_items",
                evidence.get("total_items", 0),
            )

            results.append(
                {
                    "filename": filename,
                    "coverage_percent": coverage,
                    "total_testable_items": total_items,
                    "assessment": parsed.get(
                        "assessment",
                        text,
                    ),
                }
            )

        return results
