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
    # Coerce non-string response content to a string for robust parsing
    if not isinstance(text, str):
        try:
            text = json.dumps(text)
        except Exception:
            text = str(text)

    text = text.strip()

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


class SecurityAgent(BaseAgent):
    def __init__(self, config, name: str = "security"):
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

            assessment = parsed.get("assessment", "")
            # If parsing fails, put the raw response in the assessment for debugging.
            if not parsed:
                assessment = f"Failed to parse LLM response: {text}"

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
                    "assessment": assessment,
                }
            )

        return results
