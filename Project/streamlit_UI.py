"""
Preloaded Streamlit presentation layer — the Code Review Console.

Pure presentation. It never imports nodes/agents/graph; it receives three
callbacks from main.py:
    run_review(files, source, pr_details) -> {values, interrupted, interrupt_payload, thread_id}
    approve_review(thread_id) -> resumed state
    reject_review(thread_id)  -> resumed state
"""

from pathlib import Path

import streamlit as st

from config import config

STYLE = """
<style>
#MainMenu, header, footer {visibility: hidden;}
.block-container {padding-top: 2rem; max-width: 1100px;}
.cr-title {font-size: 1.5rem; font-weight: 600; color: #185FA5;}
.cr-sub {color: #5B6675; font-size: 0.9rem; margin-bottom: 0.5rem;}
.cr-badge {padding: 4px 12px; border-radius: 999px; font-size: 0.82rem; font-weight: 600;}
.cr-good {background: #EAF3DE; color: #27500A;}
.cr-warn {background: #FAEEDA; color: #633806;}
.cr-bad  {background: #FCEBEB; color: #791F1F;}
</style>
"""

DECISION_CLASS = {
    "auto_approve": "cr-good", "approved_by_reviewer": "cr-good",
    "documentation_review": "cr-warn", "human_review": "cr-warn",
    "critical_escalation": "cr-bad", "rejected_by_reviewer": "cr-bad",
}


def _collect_files(mode: str) -> list:
    """Build the files list from the chosen input widget."""
    if mode == "Sample":
        names = [p.name for p in sorted(Path(config.samples_dir).glob("*.py"))]
        chosen = st.selectbox("Sample file", names) if names else None
        if chosen:
            content = (Path(config.samples_dir) / chosen).read_text(encoding="utf-8")
            return [{"filename": chosen, "content": content}]
    elif mode == "Paste":
        pasted = st.text_area("Paste Python code", height=200, placeholder="def example():\n    ...")
        if pasted.strip():
            return [{"filename": "pasted.py", "content": pasted}]
    elif mode == "Upload":
        uploads = st.file_uploader("Upload .py files", type=["py"], accept_multiple_files=True)
        return [{"filename": f.name, "content": f.read().decode("utf-8", errors="replace")} for f in uploads or []]
    return []


def render_metrics(metrics: dict) -> None:
    """Show the five quality-gate metrics."""
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Security", f"{metrics.get('security_score', 0)}/10")
    m2.metric("Quality", f"{metrics.get('pylint_score', 0)}/10")
    m3.metric("Coverage", f"{metrics.get('coverage', 0)}%")
    m4.metric("AI score", f"{metrics.get('ai_score', 0)}")
    m5.metric("Docs", f"{metrics.get('documentation_coverage', 0)}%")


def render_findings(values: dict) -> None:
    """Show the per-file security findings and other analysis details."""
    for result in values.get("security_results", []):
        vulns = result.get("vulnerabilities", [])
        if vulns:
            with st.expander(f"Security · {result.get('filename')} — {len(vulns)} finding(s), score {result.get('security_score')}/10"):
                for vulnerability in vulns:
                    st.markdown(f"- **{vulnerability['severity']}** line {vulnerability['line']}: {vulnerability['description']}")
    with st.expander("AI review"):
        for review in values.get("ai_reviews", []):
            st.markdown(f"**{review.get('filename')}** — score {review.get('overall_score')}, confidence {review.get('confidence')}")
            st.caption(review.get("raw_response", "")[:400])


def render_app(run_review, approve_review, reject_review, recent_reviews) -> None:
    """Render the whole console. Receives the workflow callbacks + history reader from main.py."""
    st.set_page_config(page_title="AI Code Review Console", layout="wide")
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown('<div class="cr-title">AI code review console</div>', unsafe_allow_html=True)
    st.markdown('<div class="cr-sub">Submit code, run the 5 parallel analyses, and sign off on risky changes.</div>',
                unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="cr-title" style="font-size:1.1rem">Recent reviews</div>', unsafe_allow_html=True)
        history = recent_reviews(10)
        if not history:
            st.caption("No reviews yet — run one to build the history.")
        for row in history:
            st.markdown(
                f'<div class="cr-badge {DECISION_CLASS.get(row["decision"], "cr-warn")}">'
                f'{row["decision"].replace("_", " ").title()}</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                f"{row['review_id']} · {row['created_at']} · "
                f"sec {row['security_score']}/10 · cov {row['coverage']}% · docs {row['documentation_coverage']}%"
            )

    mode = st.radio("Input source", ["Sample", "Paste", "Upload", "GitHub PR"], horizontal=True)
    source, pr_details, files = "local", {}, []
    if mode == "GitHub PR":
        col1, col2, col3 = st.columns(3)
        owner = col1.text_input("Owner", placeholder="octocat")
        repo = col2.text_input("Repo", placeholder="Hello-World")
        pr_number = col3.number_input("PR #", min_value=1, step=1, value=1)
        source, pr_details = "github", {"repo_owner": owner, "repo_name": repo, "pr_number": int(pr_number)}
    else:
        files = _collect_files(mode)

    if st.button("Run review", type="primary"):
        if source == "github" or files:
            with st.spinner("Running the 5 parallel analyses ..."):
                st.session_state["result"] = run_review(files, source, pr_details)
        else:
            st.warning("Provide some code first.")

    result = st.session_state.get("result")
    if not result:
        return

    values = result["values"]
    # HITL gate — the graph paused for a human
    if result.get("interrupted"):
        payload = result["interrupt_payload"]
        st.markdown(
            f'<div class="cr-badge {DECISION_CLASS.get(payload.get("decision"), "cr-warn")}">'
            f'{payload.get("decision", "").replace("_", " ").title()}</div>',
            unsafe_allow_html=True,
        )
        render_metrics(payload.get("metrics", {}))
        st.warning(f"Human review required — {payload.get('high_severity_issues', 0)} high-severity issue(s). {payload.get('question')}")
        approve_col, reject_col = st.columns(2)
        if approve_col.button("Approve for merge", use_container_width=True):
            resumed = approve_review(result["thread_id"])
            st.session_state["result"] = {"values": resumed, "interrupted": False, "thread_id": result["thread_id"]}
            st.rerun()
        if reject_col.button("Reject", use_container_width=True):
            resumed = reject_review(result["thread_id"])
            st.session_state["result"] = {"values": resumed, "interrupted": False, "thread_id": result["thread_id"]}
            st.rerun()
        render_findings(values)
        return

    # Completed — show the report
    report = values.get("report", {})
    decision = report.get("decision", values.get("decision", ""))
    st.markdown(
        f'<div class="cr-badge {DECISION_CLASS.get(decision, "cr-warn")}">Decision: {decision.replace("_", " ").title()}</div>',
        unsafe_allow_html=True,
    )
    render_metrics(report.get("metrics", values.get("decision_metrics", {})))
    if report.get("key_findings"):
        st.markdown("**Key findings**")
        for finding in report["key_findings"]:
            st.markdown(f"- {finding}")
    if report.get("action_items"):
        st.markdown("**Action items**")
        for item in report["action_items"]:
            st.markdown(f"- {item}")
    render_findings(values)
