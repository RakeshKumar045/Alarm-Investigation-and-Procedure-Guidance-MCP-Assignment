import html
import os

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv(
    "COPILOT_BACKEND_URL",
    "http://127.0.0.1:8080",
).rstrip("/")

st.set_page_config(
    page_title="ABB Alarm Intelligence Copilot",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -------------------------------------------------
# Styling
# -------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background: #f4f7fb;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(135deg, #071f3a, #0e5d94);
        color: white;
        border-radius: 22px;
        padding: 2.2rem 2.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 12px 30px rgba(12, 54, 91, 0.22);
    }

    .hero-eyebrow {
        color: #9bdcff;
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 0.18rem;
        margin-bottom: 0.7rem;
    }

    .hero-title {
        font-size: 2.35rem;
        font-weight: 800;
        line-height: 1.15;
    }

    .hero-subtitle {
        color: #e6f5ff;
        font-size: 1.05rem;
        line-height: 1.6;
        margin-top: 0.8rem;
        max-width: 900px;
    }

    .status-pill {
        display: inline-block;
        margin-top: 1rem;
        padding: 0.45rem 0.85rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.14);
        border: 1px solid rgba(255, 255, 255, 0.28);
        color: white;
        font-size: 0.82rem;
        font-weight: 700;
    }

    .input-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem 1.4rem 1.4rem;
        border: 1px solid #e0e8f1;
        box-shadow: 0 5px 18px rgba(27, 55, 82, 0.07);
        margin-bottom: 1.5rem;
    }

    .section-title {
        color: #0b2942;
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }

    .asset-card {
        background: white;
        border-radius: 14px;
        border-left: 5px solid #168aad;
        padding: 1rem 1.2rem;
        margin: 0.8rem 0 1.2rem;
        box-shadow: 0 4px 14px rgba(25, 60, 90, 0.08);
    }

    .asset-label {
        color: #718096;
        font-size: 0.72rem;
        letter-spacing: 0.12rem;
        font-weight: 800;
    }

    .asset-name {
        color: #092b46;
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 0.25rem;
    }

    .asset-meta {
        color: #637589;
        font-size: 0.9rem;
        margin-top: 0.35rem;
    }

    .cause-item {
        background: #fff8e5;
        color: #604800;
        border-left: 4px solid #e4a500;
        border-radius: 9px;
        padding: 0.75rem 0.9rem;
        margin: 0.45rem 0;
    }

    .action-item {
        display: flex;
        gap: 0.7rem;
        align-items: flex-start;
        background: #eef8ff;
        color: #123951;
        border-left: 4px solid #168aad;
        border-radius: 9px;
        padding: 0.75rem 0.9rem;
        margin: 0.45rem 0;
    }

    .action-number {
        background: #168aad;
        color: white;
        border-radius: 50%;
        min-width: 1.45rem;
        height: 1.45rem;
        text-align: center;
        line-height: 1.45rem;
        font-size: 0.8rem;
        font-weight: 800;
    }

    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e0e8f1;
        border-radius: 12px;
        padding: 0.8rem;
        box-shadow: 0 4px 12px rgba(25, 60, 90, 0.06);
    }

    div.stButton > button {
        width: 100%;
        min-height: 2.8rem;
        border: none;
        border-radius: 10px;
        background: linear-gradient(135deg, #1261a0, #168aad);
        color: white;
        font-weight: 800;
        box-shadow: 0 5px 12px rgba(18, 97, 160, 0.22);
    }

    div.stButton > button:hover {
        color: white;
        background: linear-gradient(135deg, #0b4778, #1261a0);
    }

    .footer {
        text-align: center;
        color: #7b8794;
        font-size: 0.8rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #dfe7ef;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------
# Utility functions
# -------------------------------------------------

def safe(value) -> str:
    return html.escape(str(value if value is not None else "N/A"))


def render_header() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-eyebrow">
                ABB INDUSTRIAL INTELLIGENCE
            </div>
            <div class="hero-title">
                Alarm Intelligence Copilot
            </div>
            <div class="hero-subtitle">
                Investigate plant alarms using asset intelligence,
                MCP-powered analysis, and evidence-backed procedures.
            </div>
            <div class="status-pill">
                ● MCP Connected &nbsp;&nbsp;
                ● RAG Enabled &nbsp;&nbsp;
                ● Evidence-Based
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## ⚙️ Copilot Controls")
        st.caption("Alarm investigation workspace")

        st.markdown("---")

        st.markdown("### Connected services")
        st.success("Alarm API Simulator")
        st.success("Alarm MCP Server")
        st.success("Procedure RAG")

        st.markdown("---")

        st.markdown("### Supported analysis")
        st.markdown(
            """
            - Asset resolution
            - Active alarm retrieval
            - Priority scoring
            - Related asset correlation
            - Operator recommendations
            - Procedure and manual retrieval
            """
        )

        st.markdown("---")

        st.markdown("### 📊 System status")
        st.success("Backend API configured")
        st.success("MCP tools available")
        st.success("RAG index ready")

        st.markdown("---")

        st.markdown("### 🔗 API documentation")

        st.markdown(
            """
            - [Copilot Backend API](http://localhost:8080/docs)
            - [Alarm API Simulator](http://localhost:8000/docs)
            - [Backend Health](http://localhost:8080/health)
            - [Alarm API Health](http://localhost:8000/health)
            """
        )

        st.caption(f"Internal Docker backend: {BACKEND_URL}")
        st.caption("Version 1.0.0 · Synthetic demonstration environment")


def render_metrics(result: dict) -> None:
    asset = result.get("asset") or {}
    alarms = result.get("alarms") or []
    priority = result.get("priority") or {}

    severity = "N/A"
    status = "N/A"

    if alarms:
        severity = str(alarms[0].get("severity", "N/A")).upper()
        status = str(alarms[0].get("status", "N/A")).upper()

    st.markdown(
        '<div class="section-title">📊 Investigation Overview</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Asset", asset.get("asset_name", "Unknown"))

    with col2:
        st.metric("Alarms Found", len(alarms))

    with col3:
        st.metric("Severity", severity)

    with col4:
        st.metric("Priority Score", priority.get("priority_score", "N/A"))

    st.markdown(
        f"""
        <div class="asset-card">
            <div class="asset-label">INVESTIGATED ASSET</div>
            <div class="asset-name">{safe(asset.get("asset_name"))}</div>
            <div class="asset-meta">
                Site: {safe(asset.get("site"))}
                &nbsp; | &nbsp;
                Unit: {safe(asset.get("unit"))}
                &nbsp; | &nbsp;
                Type: {safe(asset.get("asset_type"))}
                &nbsp; | &nbsp;
                Status: {safe(status)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_alarm_table(result: dict) -> None:
    alarms = result.get("alarms") or []

    st.markdown(
        '<div class="section-title">🚨 Alarm Details</div>',
        unsafe_allow_html=True,
    )

    if not alarms:
        st.info("No alarms were returned for this asset.")
        return

    rows = [
        {
            "Alarm": alarm.get("alarm_name", "N/A"),
            "Severity": str(alarm.get("severity", "N/A")).upper(),
            "Status": str(alarm.get("status", "N/A")).upper(),
            "Start time": alarm.get("start_time", "N/A"),
            "Occurrences": alarm.get("occurrence_count", "N/A"),
        }
        for alarm in alarms
    ]

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )


def render_recommendations(result: dict) -> None:
    recommendations = result.get("recommendations") or {}
    causes = recommendations.get("likely_causes") or []
    actions = recommendations.get("recommended_actions") or []

    st.markdown(
        '<div class="section-title">🛠 Likely Causes and Actions</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    with left:
        st.markdown("#### Likely contributing factors")

        if causes:
            for cause in causes:
                st.markdown(
                    f'<div class="cause-item">◉ {safe(cause)}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No likely causes were returned.")

    with right:
        st.markdown("#### Immediate operator actions")

        if actions:
            for index, action in enumerate(actions, start=1):
                st.markdown(
                    f"""
                    <div class="action-item">
                        <span class="action-number">{index}</span>
                        <span>{safe(action)}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No operator recommendations were returned.")

    safety_note = recommendations.get("safety_note")

    if safety_note:
        st.warning(f"⚠️ Safety note: {safety_note}")


def render_citations(result: dict) -> None:
    citations = result.get("citations") or []

    st.markdown(
        '<div class="section-title">📚 Procedure and Maintenance Evidence</div>',
        unsafe_allow_html=True,
    )

    if not citations:
        st.warning("No sufficiently relevant documents were found.")
        return

    for citation in citations:
        document_id = citation.get("document_id", "Unknown")
        document_type = citation.get("document_type", "Document")
        title = citation.get("title", "Untitled document")
        score = citation.get("score", 0)
        source = citation.get("source", "")
        text = citation.get("text", "")

        with st.expander(
            f"{document_id} | {document_type} | relevance {score}"
        ):
            st.markdown(f"**{title}**")
            st.markdown(text)
            st.caption(f"Source: {source}")


def render_trace(result: dict) -> None:
    trace = result.get("trace") or []

    st.markdown(
        '<div class="section-title">🔍 MCP Execution Trace</div>',
        unsafe_allow_html=True,
    )

    if not trace:
        st.info("No MCP tool calls were recorded.")
        return

    successful = sum(
        1 for item in trace
        if item.get("status") == "success"
    )

    st.info(
        f"{successful}/{len(trace)} MCP tool calls completed successfully."
    )

    for index, item in enumerate(trace, start=1):
        tool = item.get("tool", "Unknown tool")
        status = item.get("status", "unknown")
        duration = item.get("duration_ms", "N/A")

        with st.expander(
            f"{index}. {tool} | {status} | {duration} ms"
        ):
            st.json(item)


def render_visualizations(result: dict) -> None:
    alarms = result.get("alarms") or []
    citations = result.get("citations") or []
    trace = result.get("trace") or []

    st.markdown(
        '<div class="section-title">📈 Operational Insights</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Alarm severity distribution")

        if alarms:
            severity_df = (
                pd.DataFrame(alarms)["severity"]
                .str.upper()
                .value_counts()
                .rename_axis("Severity")
                .reset_index(name="Count")
                .set_index("Severity")
            )

            st.bar_chart(
                severity_df,
                color="#168aad",
            )
        else:
            st.info("No severity data available.")

    with col2:
        st.markdown("#### Alarm recurrence")

        if alarms:
            recurrence_df = pd.DataFrame(
                [
                    {
                        "Alarm": alarm.get("alarm_name", "Unknown"),
                        "Occurrences": alarm.get("occurrence_count", 0),
                    }
                    for alarm in alarms
                ]
            ).set_index("Alarm")

            st.bar_chart(
                recurrence_df,
                color="#e4a500",
            )
        else:
            st.info("No recurrence data available.")

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Document relevance")

        if citations:
            citation_df = pd.DataFrame(
                [
                    {
                        "Document": citation.get(
                            "document_id",
                            "Unknown",
                        ),
                        "Score": citation.get("score", 0),
                    }
                    for citation in citations
                ]
            )

            citation_df["Document"] = (
                citation_df["Document"]
                + " "
                + citation_df.groupby("Document").cumcount().astype(str)
            )

            st.bar_chart(
                citation_df.set_index("Document"),
                color="#6c63ff",
            )
        else:
            st.info("No citation data available.")

    with col4:
        st.markdown("#### MCP tool latency")

        if trace:
            latency_df = pd.DataFrame(
                [
                    {
                        "Tool": item.get("tool", "Unknown"),
                        "Duration (ms)": item.get("duration_ms", 0),
                    }
                    for item in trace
                ]
            ).set_index("Tool")

            st.bar_chart(
                latency_df,
                color="#20a464",
            )
        else:
            st.info("No MCP trace data available.")


def render_raw_data(result: dict) -> None:
    with st.expander("🧾 Raw investigation response"):
        st.json(result)


# -------------------------------------------------
# Main interface
# -------------------------------------------------

render_sidebar()
render_header()

st.markdown(
    '<div class="section-title">💬 Ask the Copilot</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="input-card">', unsafe_allow_html=True)

question = st.text_area(
    "Investigation question",
    value=(
        "Investigate active alarms for Boiler Feed Pump 101 "
        "and recommend immediate actions."
    ),
    height=110,
    label_visibility="collapsed",
    placeholder=(
        "Example: Which active alarm has the highest priority "
        "and what procedure applies?"
    ),
)

investigate = st.button(
    "🚀 Investigate Alarm",
    type="primary",
)

st.markdown("</div>", unsafe_allow_html=True)


if investigate:
    if not question.strip():
        st.warning("Please enter an investigation question.")
        st.stop()

    with st.spinner(
        "Discovering MCP tools, analysing alarms, and retrieving evidence..."
    ):
        try:
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={"question": question.strip()},
                timeout=90,
            )

            if response.status_code != 200:
                st.error(
                    f"Copilot request failed "
                    f"({response.status_code}): {response.text}"
                )
                st.stop()

            result = response.json()

            if result.get("answer") == "No matching asset was found.":
                st.warning("No matching asset was found.")
                render_trace(result)
                st.stop()

            st.success("Investigation completed successfully.")

            render_metrics(result)

            tab_report, tab_visuals, tab_evidence, tab_trace, tab_raw = st.tabs(
                [
                    "📋 Investigation Report",
                    "📈 Visualizations",
                    "📚 Evidence",
                    "🔍 MCP Trace",
                    "🧾 Raw Data",
                ]
            )

            with tab_report:
                st.markdown(
                    '<div class="section-title">🧠 Copilot Assessment</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    result.get(
                        "answer",
                        "No answer was returned.",
                    )
                )

                render_alarm_table(result)
                render_recommendations(result)

            with tab_visuals:
                render_visualizations(result)

            with tab_evidence:
                render_citations(result)

            with tab_trace:
                render_trace(result)

            with tab_raw:
                render_raw_data(result)

        except requests.Timeout:
            st.error(
                "The copilot request timed out. "
                "Verify that the API, MCP server, and backend are running."
            )

        except requests.ConnectionError:
            st.error(
                "The copilot backend is unavailable. "
                f"Verify: {BACKEND_URL}"
            )

        except requests.RequestException as exc:
            st.error(f"Copilot backend request failed: {exc}")

        except ValueError:
            st.error("The backend returned invalid JSON.")


st.markdown(
    """
    <div class="footer">
        ABB Alarm Intelligence Copilot · MCP + RAG ·
        Synthetic Alarm Management Environment
    </div>
    """,
    unsafe_allow_html=True,
)


