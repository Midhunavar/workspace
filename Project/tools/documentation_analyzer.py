"""
Documentation tool (preloaded).

A single deterministic function that measures docstring coverage across the module,
its public functions and its classes (via AST). It is EVIDENCE ONLY — the
DocumentationAgent's LLM reads this measurement and produces the documentation
score. No state, no helpers.
"""

import ast
from typing import Any, Dict, List


def measure_documentation(code: str, filename: str) -> Dict[str, Any]:
    """Measure docstring coverage for one file (module + public functions + classes)."""
    try:
        tree = ast.parse(code)
        has_module_doc = bool(ast.get_docstring(tree))
        total_items = 1
        documented_items = 1 if has_module_doc else 0
        missing: List[Dict[str, Any]] = [] if has_module_doc else [{"type": "module", "name": filename, "line": 1}]
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                total_items += 1
                if ast.get_docstring(node):
                    documented_items += 1
                else:
                    missing.append({"type": "function", "name": node.name, "line": node.lineno})
            elif isinstance(node, ast.ClassDef):
                total_items += 1
                if ast.get_docstring(node):
                    documented_items += 1
                else:
                    missing.append({"type": "class", "name": node.name, "line": node.lineno})
        documentation_percent = round(documented_items / total_items * 100, 1) if total_items else 100.0
        return {"filename": filename, "documentation_percent": documentation_percent,
                "total_items": total_items, "documented_items": documented_items, "missing": missing[:10]}
    except Exception as error:
        return {"filename": filename, "documentation_percent": 0.0, "total_items": 0,
                "documented_items": 0, "missing": [], "error": str(error)}
