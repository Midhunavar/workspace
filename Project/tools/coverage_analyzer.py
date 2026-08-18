"""
Coverage estimate tool (preloaded).

A single deterministic function that gives an HONEST static coverage estimate:
the share of testable items (public functions + classes) that have a matching
`test_<name>` function in the same code. It is EVIDENCE ONLY — the CoverageAgent's
LLM reads this estimate and produces the coverage score. No fabricated baseline,
no state, no helpers.
"""

import ast
from typing import Any, Dict, List


def estimate_coverage(code: str) -> Dict[str, Any]:
    """Estimate coverage as the share of testable items that have a matching test."""
    try:
        tree = ast.parse(code)
        testable: List[Dict[str, Any]] = []
        all_function_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                all_function_names.add(node.name)
                if (not node.name.startswith("_") and node.name not in ("main",)
                        and not node.name.startswith("test")):
                    testable.append({"name": node.name, "line": node.lineno, "type": "function"})
            elif isinstance(node, ast.ClassDef):
                testable.append({"name": node.name, "line": node.lineno, "type": "class"})

        covered = {
            item["name"] for item in testable
            if any(fn.lower().startswith("test") and item["name"].lower() in fn.lower()
                   for fn in all_function_names)
        }
        total = len(testable)
        coverage_estimate = round(len(covered) / total * 100, 1) if total else 100.0
        missing_tests = [
            f"{item['type'].capitalize()} '{item['name']}' at line {item['line']}"
            for item in testable if item["name"] not in covered
        ][:5]
        return {"coverage_estimate": coverage_estimate,
                "total_testable_items": total, "missing_tests": missing_tests}
    except Exception as error:
        return {"coverage_estimate": 0.0,
                "total_testable_items": 0, "missing_tests": [], "error": str(error)}

