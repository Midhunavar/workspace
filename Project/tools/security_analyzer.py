"""
Security scan tool (preloaded).

A single deterministic function that returns regex-detected security findings for
one file. It is EVIDENCE ONLY — the SecurityAgent's LLM reads these findings and
produces the security score. No state, no orchestration, no helpers.
"""

import re
from typing import Any, Dict

SECURITY_PATTERNS = [
    (r"eval\s*\(", "HIGH", "Use of eval() - code injection risk"),
    (r"exec\s*\(", "HIGH", "Use of exec() - code execution risk"),
    (r"subprocess.*shell\s*=\s*True", "HIGH", "Shell injection vulnerability"),
    (r"pickle\.loads?\s*\(", "MEDIUM", "Unsafe deserialization with pickle"),
    (r"open\s*\([^)]*[\'\"]w[\'\"]", "MEDIUM", "File write operation"),
    (r"requests\..*verify\s*=\s*False", "MEDIUM", "SSL verification disabled"),
    (r"password\s*=\s*[\'\"][^\'\"]+[\'\"]", "HIGH", "Hardcoded password"),
    (r"api_key\s*=\s*[\'\"][^\'\"]+[\'\"]", "HIGH", "Hardcoded API key"),
    (r"token\s*=\s*[\'\"][^\'\"]+[\'\"]", "HIGH", "Hardcoded token"),
    (r"SECRET\s*=\s*[\'\"][^\'\"]+[\'\"]", "HIGH", "Hardcoded secret"),
    (r"os\.system\s*\(", "HIGH", "Potential command injection with os.system"),
    (r"yaml\.load\s*\([^)]*\)", "MEDIUM", "Unsafe YAML loading without safe_load"),
    (r"\.execute\s*\([\'\"][^\'\"]*%", "HIGH", "SQL injection vulnerability"),
    (r"md5\s*\(", "LOW", "Weak hash (MD5)"),
]


def scan_security(code: str, filename: str) -> Dict[str, Any]:
    """Return the regex-detected vulnerabilities and severity counts for one file."""
    vulnerabilities = []
    for pattern, severity, description in SECURITY_PATTERNS:
        for match in re.finditer(pattern, code, re.IGNORECASE):
            line_num = code[: match.start()].count("\n") + 1
            vulnerabilities.append({
                "line": line_num, "severity": severity,
                "description": description, "code_snippet": match.group(),
            })
    severity_counts = {
        level: sum(1 for v in vulnerabilities if v["severity"] == level)
        for level in ("HIGH", "MEDIUM", "LOW")
    }
    return {"filename": filename, "vulnerabilities": vulnerabilities, "severity_counts": severity_counts}
