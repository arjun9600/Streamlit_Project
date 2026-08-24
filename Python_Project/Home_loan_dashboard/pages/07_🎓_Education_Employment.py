import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.theme import apply_theme, style_fig, page_header, PLOTLY_CONFIG, sidebar_brand, topbar, CATEGORICAL_PALETTE
from utils.components import kpi_row, section_start, section_end, insight_box
from utils.filters import render_sidebar_filters
from utils.auth import require_login

st.set_page_config(page_title="Education & Employment", page_icon="🎓", layout="wide")
apply_theme()
require_login()
df = load_data()

sidebar_brand()
filtered = render_sidebar_filters(df, key_prefix="edu_")

topbar(filtered)

page_header("Education & Employment", "Education attainment, tenure and how they shape income and risk.", "🎓")

kpi_row([
    {"label": "Most common education", "value": f"{filtered['NAME_EDUCATION_TYPE'].mode()[0]}", "icon": "🎓"},
    {"label": "Median years employed", "value": f"{filtered['EMPLOYED_YEARS'].median():.1f}", "icon": "💼"},
    {"label": "% Higher education", "value": f"{(filtered['NAME_EDUCATION_TYPE']=='Higher education').mean()*100:.1f}%", "icon": "📚"},
    {"label": "Top occupation", "value": f"{filtered['OCCUPATION_TYPE'].mode()[0] if filtered['OCCUPATION_TYPE'].notna().any() else 'N/A'}", "icon": "🧑‍💼"},
])

c1, c2 = st.columns(2)
with c1:
    section_start("🎓 Education Level Distribution")
    grp = filtered["NAME_EDUCATION_TYPE"].value_counts().reset_index()
    grp.columns = ["Education", "Applicants"]
    fig = px.bar(grp, x="Applicants", y="Education", orientation="h", color="Education",
                 color_discrete_sequence=CATEGORICAL_PALETTE)
    fig.update_layout(height=360, showlegend=False, yaxis_title="")
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

with c2:
    section_start("💵 Median Income by Education Level")
    grp = filtered.groupby("NAME_EDUCATION_TYPE")["AMT_INCOME_TOTAL"].median().sort_values().reset_index()
    fig = px.bar(grp, x="AMT_INCOME_TOTAL", y="NAME_EDUCATION_TYPE", orientation="h",
                 color="AMT_INCOME_TOTAL", color_continuous_scale=["#dcebe8", "#4c748c"])
    fig.update_layout(height=360, xaxis_title="Median income ($)", yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

c3, c4 = st.columns(2)
with c3:
    section_start("💼 Years Employed Distribution")
    plot_df = filtered.dropna(subset=["EMPLOYED_YEARS"])
    fig = px.histogram(plot_df, x="EMPLOYED_YEARS", nbins=40, color_discrete_sequence=["#4c748c"])
    fig.update_layout(height=360, xaxis_title="Years employed")
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

with c4:
    section_start("🧑‍💼 Occupation Type Volume (top 12)")
    grp = filtered["OCCUPATION_TYPE"].value_counts().head(12).reset_index()
    grp.columns = ["Occupation", "Applicants"]
    fig = px.bar(grp, x="Applicants", y="Occupation", orientation="h",
                 color="Applicants", color_continuous_scale=["#dcebe8", "#f59e0b"])
    fig.update_layout(height=360, yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

section_start("🎓 Education × Default Rate Summary")
tbl = filtered.groupby("NAME_EDUCATION_TYPE").agg(
    Applicants=("SK_ID_CURR", "count"),
    **{"Median income ($)": ("AMT_INCOME_TOTAL", "median")},
    **{"Default rate %": ("TARGET", lambda x: round(x.mean()*100, 2))},
).reset_index().sort_values("Default rate %", ascending=False)
st.dataframe(tbl, use_container_width=True, hide_index=True)
section_end()
