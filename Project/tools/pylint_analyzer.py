"""
PyLint tool (preloaded).

A single deterministic function that runs PyLint on one file and returns its score
and top issues. It is EVIDENCE ONLY — the QualityAgent's LLM reads these results
and produces the quality score. `python -m pylint` is used so it works regardless
of PATH. No state, no orchestration, no helpers.
"""

import json
import os
import subprocess
import sys
import tempfile
from typing import Any, Dict


def run_pylint(code: str, filename: str) -> Dict[str, Any]:
    """Run PyLint on one file and return its numeric score and top issues."""
    temp_path = ""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as handle:
            handle.write(code)
            temp_path = handle.name
        result = subprocess.run(
            [sys.executable, "-m", "pylint", temp_path, "--output-format=json2"],
            capture_output=True, text=True, timeout=30,
        )
        report = json.loads(result.stdout) if result.stdout.strip() else {}
        messages = report.get("messages", [])
        raw_score = report.get("statistics", {}).get("score")
        pylint_score = round(float(raw_score), 2) if raw_score is not None else 5.0
        issues = [
            {"type": m.get("type"), "symbol": m.get("symbol"),
             "message": m.get("message"), "line": m.get("line")}
            for m in messages[:10]
        ]
        return {"filename": filename, "pylint_score": pylint_score,
                "total_issues": len(messages), "issues": issues}
    except Exception as error:
        return {"filename": filename, "pylint_score": 5.0, "total_issues": 0,
                "issues": [], "error": str(error)}
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
