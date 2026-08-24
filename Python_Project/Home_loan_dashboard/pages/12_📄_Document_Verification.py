import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.theme import apply_theme, style_fig, page_header, PLOTLY_CONFIG, sidebar_brand, topbar
from utils.components import kpi_row, section_start, section_end, insight_box
from utils.filters import render_sidebar_filters
from utils.auth import require_login

st.set_page_config(page_title="Document Verification", page_icon="📄", layout="wide")
apply_theme()
require_login()
df = load_data()

sidebar_brand()
filtered = render_sidebar_filters(df, key_prefix="doc_")

topbar(filtered)

page_header("Document Verification & Social Circle", "Submitted-document completeness and applicant social-circle delinquency signals.", "📄")

doc_cols = [c for c in df.columns if c.startswith("FLAG_DOCUMENT_")]

kpi_row([
    {"label": "Avg. documents submitted", "value": f"{filtered['DOCS_SUBMITTED'].mean():.1f} / {len(doc_cols)}", "icon": "📄"},
    {"label": "Applicants w/ social-circle default (30d)", "value": f"{(filtered['DEF_30_CNT_SOCIAL_CIRCLE']>0).mean()*100:.1f}%", "icon": "🧑‍🤝‍🧑"},
    {"label": "Avg. bureau inquiries (last year)", "value": f"{filtered['AMT_REQ_CREDIT_BUREAU_YEAR'].mean():.1f}" if filtered['AMT_REQ_CREDIT_BUREAU_YEAR'].notna().any() else "N/A", "icon": "🔍"},
    {"label": "Days since last phone change (median)", "value": f"{-filtered['DAYS_LAST_PHONE_CHANGE'].median():.0f}", "icon": "📱"},
])

c1, c2 = st.columns(2)
with c1:
    section_start("📄 Documents Submitted vs Default Rate")
    grp = filtered.groupby("DOCS_SUBMITTED")["TARGET"].agg(["mean", "count"]).reset_index()
    grp = grp[grp["count"] >= 5]
    grp["mean"] = (grp["mean"] * 100).round(2)
    fig = px.bar(grp, x="DOCS_SUBMITTED", y="mean", color="mean",
                 color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"])
    fig.update_layout(height=360, xaxis_title="Documents submitted", yaxis_title="Default rate (%)", coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

with c2:
    section_start("🧑‍🤝‍🧑 Social Circle Delinquency vs Default Rate")
    plot_df = filtered.copy()
    plot_df["has_social_default"] = plot_df["DEF_30_CNT_SOCIAL_CIRCLE"].fillna(0).gt(0).map({True: "Circle has defaults", False: "No known defaults in circle"})
    grp = plot_df.groupby("has_social_default")["TARGET"].mean().mul(100).reset_index()
    fig = px.bar(grp, x="has_social_default", y="TARGET", color="TARGET",
                 color_continuous_scale=["#10b981", "#ef4444"], text_auto=".2f")
    fig.update_layout(height=360, xaxis_title="", yaxis_title="Default rate (%)", coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

section_start("🔍 Credit Bureau Inquiry Frequency")
inq_cols = ["AMT_REQ_CREDIT_BUREAU_DAY", "AMT_REQ_CREDIT_BUREAU_WEEK", "AMT_REQ_CREDIT_BUREAU_MON",
            "AMT_REQ_CREDIT_BUREAU_QRT", "AMT_REQ_CREDIT_BUREAU_YEAR"]
means = filtered[inq_cols].mean().reset_index()
means.columns = ["Window", "Avg inquiries"]
fig = px.bar(means, x="Window", y="Avg inquiries", color="Avg inquiries",
             color_continuous_scale=["#dcebe8", "#3d5f73"])
fig.update_layout(height=340, coloraxis_showscale=False)
st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
st.caption("Frequent bureau inquiries in a short window can signal credit-seeking stress.")
section_end()
