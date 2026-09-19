from __future__ import annotations

import pandas as pd
import streamlit as st

from flowforge import analyze_intake, insert_result, list_results

st.set_page_config(page_title="FlowForge", page_icon="⚡", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.6rem; max-width: 1250px;}
.hero {padding: 1.15rem 1.3rem; border: 1px solid #d9e2ec; border-radius: 18px; margin-bottom: 1rem;}
.hero h1 {margin: 0; font-size: 2.1rem;}
.hero p {margin: .35rem 0 0 0; color: #64748b;}
.small {color: #64748b; font-size: .9rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>⚡ FlowForge Operations Command Center</h1>
  <p>Turn messy inbound requests into prioritized, routed, structured work in seconds.</p>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Workspace", ["Dashboard", "New Intake", "Priority Queue", "Architecture"])

rows = list_results()
df = pd.DataFrame(rows)

if page == "Dashboard":
    c1, c2, c3, c4 = st.columns(4)
    total = len(df)
    critical = int((df["priority_score"] >= 80).sum()) if total else 0
    high = int(((df["priority_score"] >= 60) & (df["priority_score"] < 80)).sum()) if total else 0
    avg = round(float(df["priority_score"].mean()), 1) if total else 0
    c1.metric("Requests", total)
    c2.metric("Critical", critical)
    c3.metric("High Priority", high)
    c4.metric("Avg. Priority", avg)

    st.subheader("Operational workload")
    if total:
        left, right = st.columns([1, 1])
        with left:
            st.caption("Requests by category")
            st.bar_chart(df["category"].value_counts())
        with right:
            st.caption("Requests by owner")
            st.bar_chart(df["suggested_owner"].value_counts())
        st.subheader("Latest routed work")
        st.dataframe(
            df[["priority_label", "category", "subject", "suggested_owner", "sentiment", "created_at"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Run `python seed_demo.py` or add a request from New Intake.")

elif page == "New Intake":
    st.subheader("Process a new request")
    source = st.selectbox("Source", ["Email", "Web form", "Chat", "API", "Manual"])
    subject = st.text_input("Subject", "Enterprise customer reports checkout outage")
    text = st.text_area(
        "Request text",
        "URGENT: Our checkout is down and all orders are blocked. Please help immediately. Contact ops@northstar.example. Case #SUP-8842.",
        height=180,
    )
    if st.button("Analyze and route", type="primary"):
        result = analyze_intake(source, subject, text).to_dict()
        row_id = insert_result(result)
        st.success(f"Request #{row_id} processed")
        a, b, c = st.columns(3)
        a.metric("Priority", result["priority_label"])
        b.metric("Category", result["category"].title())
        c.metric("Owner", result["suggested_owner"])
        st.write("**Recommended action:**", result["suggested_action"])
        st.json({k: result[k] for k in ("emails", "phones", "monetary_values", "reference_ids")})

elif page == "Priority Queue":
    st.subheader("Priority queue")
    if df.empty:
        st.info("No requests yet.")
    else:
        category = st.multiselect("Filter category", sorted(df["category"].unique()))
        view = df.copy()
        if category:
            view = view[view["category"].isin(category)]
        st.dataframe(
            view[["priority_score", "priority_label", "subject", "category", "suggested_owner", "sentiment"]],
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            "Download queue as CSV",
            view.to_csv(index=False).encode("utf-8"),
            "flowforge_queue.csv",
            "text/csv",
        )

else:
    st.subheader("Architecture")
    st.code("""
Inbound request
   ↓
Normalization + field extraction
   ↓
Category classification
   ↓
Priority scoring
   ↓
Routing recommendation
   ↓
SQLite audit trail
   ↙             ↘
Streamlit UI    FastAPI REST API
""", language="text")
    st.markdown("**Engineering features:** deterministic rules, auditable routing, persistent storage, REST API, dashboard, CSV export, Docker support, tests, and CI.")
