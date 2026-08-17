"""
Security agent.

Implement SecurityAgent (extends BaseAgent, name "security"): for each file it calls the pre-loaded
scan_security tool for evidence and asks the LLM to score the file's security. See the problem
description for the analyze() return contract and score scale.
"""
import json
import re

from agents.base_agent import BaseAgent
from tools.security_analyzer import scan_security
from utils.gemini_client import get_review_llm


def _extract_json(text: str) -> dict:
    """Extract JSON from an LLM response."""
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

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


class SecurityAgent(BaseAgent):
    def __init__(self, name: str = "security"):
        super().__init__(name)
        self.model = get_review_llm()

    def analyze(self, files_data: list) -> list:
        results = []

        for file_data in files_data:
            filename = file_data.get("filename", "unknown.py")
            content = file_data.get("content", "")

            evidence = scan_security(content)

            prompt = f"""
You are a Python security reviewer.

Review the following Python file using ONLY the supplied deterministic
security scan as factual evidence.

File: {filename}

Security scan:
{json.dumps(evidence, indent=2, default=str)}

Code:
{content}

Return ONLY valid JSON:

{{
  "security_score": 0.0,
  "vulnerabilities": [],
  "assessment": "..."
}}

security_score must be between 0 and 10.
Do not invent vulnerabilities that are not supported by the evidence.
"""

            response = self.model.invoke(prompt)

            text = getattr(response, "content", str(response))
            parsed = _extract_json(text)

            score = _clamp(
                parsed.get("security_score", 0.0),
                0.0,
                10.0,
            )

            results.append(
                {
                    "filename": filename,
                    "security_score": score,
                    "vulnerabilities": parsed.get(
                        "vulnerabilities",
                        [],
                    ),
                    "severity_counts": evidence.get(
                        "severity_counts",
                        {},
                    ),
                    "assessment": parsed.get(
                        "assessment",
                        text,
                    ),
                }
            )

        return results
