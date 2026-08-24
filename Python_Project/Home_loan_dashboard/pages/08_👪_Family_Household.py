import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.theme import apply_theme, style_fig, page_header, PLOTLY_CONFIG, sidebar_brand, topbar, CATEGORICAL_PALETTE
from utils.components import kpi_row, section_start, section_end, insight_box
from utils.filters import render_sidebar_filters
from utils.auth import require_login

st.set_page_config(page_title="Family & Household", page_icon="👪", layout="wide")
apply_theme()
require_login()
df = load_data()

sidebar_brand()
filtered = render_sidebar_filters(df, key_prefix="fam_")

topbar(filtered)

page_header("Family & Household Structure", "Household size, dependants and accompanying-person patterns.", "👪")

kpi_row([
    {"label": "Avg. household size", "value": f"{filtered['CNT_FAM_MEMBERS'].mean():.2f}", "icon": "👪"},
    {"label": "Applicants with children", "value": f"{(filtered['CNT_CHILDREN']>0).mean()*100:.1f}%", "icon": "🧒"},
    {"label": "Most common suite", "value": f"{filtered['NAME_TYPE_SUITE'].mode()[0] if filtered['NAME_TYPE_SUITE'].notna().any() else 'N/A'}", "icon": "🧍"},
    {"label": "Married applicants", "value": f"{(filtered['NAME_FAMILY_STATUS']=='Married').mean()*100:.1f}%", "icon": "💍"},
])

c1, c2 = st.columns(2)
with c1:
    section_start("👪 Household Size Distribution")
    grp = filtered["CNT_FAM_MEMBERS"].value_counts().sort_index().reset_index()
    grp.columns = ["Household size", "Applicants"]
    grp = grp[grp["Household size"] <= 8]
    fig = px.bar(grp, x="Household size", y="Applicants", color="Applicants",
                 color_continuous_scale=["#dcebe8", "#3d5f73"])
    fig.update_layout(height=360, coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

with c2:
    section_start("🧍 Accompanying Person (Suite Type)")
    grp = filtered["NAME_TYPE_SUITE"].value_counts().reset_index()
    grp.columns = ["Suite type", "Applicants"]
    fig = px.pie(grp, names="Suite type", values="Applicants", hole=0.55, color_discrete_sequence=CATEGORICAL_PALETTE)
    fig.update_layout(height=360)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

c3, c4 = st.columns(2)
with c3:
    section_start("⚠️ Default Rate by Household Size")
    grp = filtered[filtered["CNT_FAM_MEMBERS"] <= 7].groupby("CNT_FAM_MEMBERS")["TARGET"].agg(["mean", "count"]).reset_index()
    grp = grp[grp["count"] >= 5]
    grp["mean"] = (grp["mean"] * 100).round(2)
    fig = px.line(grp, x="CNT_FAM_MEMBERS", y="mean", markers=True, color_discrete_sequence=["#ef4444"])
    fig.update_layout(height=340, xaxis_title="Household size", yaxis_title="Default rate (%)")
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

with c4:
    section_start("💍 Default Rate by Family Status")
    grp = filtered.groupby("NAME_FAMILY_STATUS")["TARGET"].mean().mul(100).sort_values().reset_index()
    fig = px.bar(grp, x="TARGET", y="NAME_FAMILY_STATUS", orientation="h", color="TARGET",
                 color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"], text_auto=".2f")
    fig.update_layout(height=340, xaxis_title="Default rate (%)", yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()
