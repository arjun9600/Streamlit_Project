import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.theme import apply_theme, style_fig, page_header, PLOTLY_CONFIG, sidebar_brand, topbar, RISK_COLOR_MAP, CATEGORICAL_PALETTE
from utils.components import kpi_row, section_start, section_end, insight_box
from utils.filters import render_sidebar_filters
from utils.auth import require_login

st.set_page_config(page_title="Income Analysis", page_icon="💵", layout="wide")
apply_theme()
require_login()
df = load_data()

sidebar_brand()
filtered = render_sidebar_filters(df, key_prefix="income_")

topbar(filtered)

page_header("Income Analysis", "Income levels, sources of income, and how they relate to repayment risk.", "💵")

kpi_row([
    {"label": "Median annual income", "value": f"${filtered['AMT_INCOME_TOTAL'].median():,.0f}", "icon": "💵"},
    {"label": "Top income type", "value": f"{filtered['NAME_INCOME_TYPE'].mode()[0]}", "icon": "🏆"},
    {"label": "Avg. annuity / income", "value": f"{filtered['ANNUITY_INCOME_RATIO'].mean()*100:.1f}%", "icon": "📐"},
    {"label": "Applicants below $100K", "value": f"{(filtered['AMT_INCOME_TOTAL']<100000).mean()*100:.1f}%", "icon": "📉"},
])

c1, c2 = st.columns([1.3, 1])
with c1:
    section_start("💰 Income Distribution (clipped at 99th pct for readability)")
    cap = filtered["AMT_INCOME_TOTAL"].quantile(0.99)
    plot_df = filtered[filtered["AMT_INCOME_TOTAL"] <= cap]
    fig = px.histogram(plot_df, x="AMT_INCOME_TOTAL", color="RISK_LABEL", nbins=45, barmode="overlay",
                        color_discrete_map=RISK_COLOR_MAP, opacity=0.75)
    fig.update_layout(height=380, legend_title="", xaxis_title="Annual income ($)")
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

with c2:
    section_start("🏢 Income Source Mix")
    grp = filtered["NAME_INCOME_TYPE"].value_counts().reset_index()
    grp.columns = ["Income type", "Applicants"]
    fig = px.pie(grp, names="Income type", values="Applicants", hole=0.55,
                 color_discrete_sequence=CATEGORICAL_PALETTE)
    fig.update_layout(height=380)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

c3, c4 = st.columns(2)
with c3:
    section_start("📶 Default Rate by Income Quintile")
    grp = filtered.groupby("INCOME_BAND", observed=True)["TARGET"].mean().mul(100).reset_index()
    fig = px.bar(grp, x="INCOME_BAND", y="TARGET", color="TARGET",
                 color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"], text_auto=".2f")
    fig.update_layout(height=350, xaxis_title="Income quintile", yaxis_title="Default rate (%)", coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

with c4:
    section_start("💳 Income vs Credit Amount")
    cap_i = filtered["AMT_INCOME_TOTAL"].quantile(0.98)
    cap_c = filtered["AMT_CREDIT"].quantile(0.98)
    plot_df = filtered[(filtered["AMT_INCOME_TOTAL"] <= cap_i) & (filtered["AMT_CREDIT"] <= cap_c)]
    fig = px.scatter(plot_df.sample(min(1500, len(plot_df)), random_state=1),
                      x="AMT_INCOME_TOTAL", y="AMT_CREDIT", color="RISK_LABEL",
                      color_discrete_map=RISK_COLOR_MAP, opacity=0.55,
                      hover_data=["NAME_INCOME_TYPE"])
    fig.update_layout(height=350, xaxis_title="Annual income ($)", yaxis_title="Credit amount ($)")
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

section_start("📋 Income Type Summary")
tbl = filtered.groupby("NAME_INCOME_TYPE").agg(
    Applicants=("SK_ID_CURR", "count"),
    **{"Median income ($)": ("AMT_INCOME_TOTAL", "median")},
    **{"Avg loan ($)": ("AMT_CREDIT", "mean")},
    **{"Default rate %": ("TARGET", lambda x: round(x.mean()*100, 2))},
).reset_index().sort_values("Applicants", ascending=False)
st.dataframe(tbl, use_container_width=True, hide_index=True)
section_end()
