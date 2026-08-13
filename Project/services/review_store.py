"""
Review store (preloaded) — durable SQLite history of completed reviews.

Separate from the graph checkpointer: the checkpointer persists in-flight run state
(so a paused HITL review survives a restart), while this store keeps a queryable
record of every FINISHED review and its human sign-off, for audit and history.

The connection is opened per call (not at import), so importing the package never
depends on the database being reachable.
"""

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List

from config import config

_SCHEMA = (
    "CREATE TABLE IF NOT EXISTS reviews ("
    "review_id TEXT PRIMARY KEY, created_at TEXT, source TEXT, files_reviewed INTEGER, "
    "decision TEXT, human_decision TEXT, security_score REAL, pylint_score REAL, "
    "coverage REAL, ai_score REAL, documentation_coverage REAL, "
    "high_severity_issues INTEGER, report_json TEXT)"
)


class ReviewStore:
    """Persists finished reviews to SQLite and lists recent history."""

    def __init__(self):
        self.db_path = config.review_db_path

    def save_review(self, state: Dict[str, Any]) -> None:
        """Persist one finished review from the final graph state (idempotent by review_id)."""
        metrics = state.get("decision_metrics", {})
        report = state.get("report", {})
        connection = sqlite3.connect(self.db_path)
        connection.execute(_SCHEMA)
        connection.execute(
            "INSERT OR REPLACE INTO reviews VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                state.get("review_id", ""),
                datetime.now().isoformat(timespec="seconds"),
                state.get("source", ""),
                len(state.get("files", [])),
                report.get("decision", state.get("decision", "")),
                state.get("human_decision", ""),
                metrics.get("security_score", 0.0),
                metrics.get("pylint_score", 0.0),
                metrics.get("coverage", 0.0),
                metrics.get("ai_score", 0.0),
                metrics.get("documentation_coverage", 0.0),
                metrics.get("high_severity_issues", 0),
                json.dumps(report),
            ),
        )
        connection.commit()
        connection.close()

    def list_reviews(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Return the most recent reviews, newest first."""
        connection = sqlite3.connect(self.db_path)
        connection.execute(_SCHEMA)
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT review_id, created_at, source, files_reviewed, decision, human_decision, "
            "security_score, pylint_score, coverage, ai_score, documentation_coverage, "
            "high_severity_issues FROM reviews ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        connection.close()
        return [dict(row) for row in rows]


review_store = ReviewStore()
