"""
Documentation agent.

Implement DocumentationAgent (extends BaseAgent, name "documentation"): for each file it calls the
pre-loaded measure_documentation tool for evidence and reports a documentation percentage. See the
problem description for the analyze() return contract and scale.
"""
import json
import re

from agents.base_agent import BaseAgent
from tools.documentation_analyzer import measure_documentation
from utils.gemini_client import get_review_llm


def _parse_json(text):
    if not isinstance(text, str):
        try:
            text = json.dumps(text)
        except Exception:
            text = str(text)

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)

        if match:
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                return {}
        else:
            return {}

    if isinstance(parsed, list):
        for item in parsed:
            if isinstance(item, dict):
                parsed = item
                break
        else:
            return {}

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


class DocumentationAgent(BaseAgent):

    def __init__(self, name="documentation"):
        super().__init__(name)
        self.model = get_review_llm()

    def analyze(self, files_data: list) -> list:
        results = []

        for file_data in files_data:
            filename = file_data.get("filename", "unknown.py")
            content = file_data.get("content", "")

            evidence = measure_documentation(content)

            prompt = f"""
You are a Python documentation reviewer.

Use the supplied AST documentation measurement as factual evidence.

File:
{filename}

Documentation evidence:
{json.dumps(evidence, indent=2, default=str)}

Code:
{content}

Return ONLY JSON:

{{
  "documentation_coverage": 0.0,
  "assessment": "..."
}}

documentation_coverage must be between 0 and 100.
Do not fabricate documented items.
"""

            response = self.model.invoke(prompt)
            text = getattr(response, "content", str(response))
            parsed = _parse_json(text)

            coverage = _clamp(
                parsed.get("documentation_coverage", 0),
                0,
                100,
            )

            results.append(
                {
                    "filename": filename,
                    "documentation_coverage": coverage,
                    "documented_items": evidence.get(
                        "documented_items",
                        0,
                    ),
                    "total_items": evidence.get(
                        "total_items",
                        0,
                    ),
                    "assessment": parsed.get(
                        "assessment",
                        text,
                    ),
                }
            )

        return results
