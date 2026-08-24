import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.theme import apply_theme, style_fig, page_header, PLOTLY_CONFIG, sidebar_brand, topbar, RISK_COLOR_MAP, CATEGORICAL_PALETTE, PALETTE_LEFT, PALETTE_RIGHT, CONTINUOUS_LEFT, CONTINUOUS_RIGHT
from utils.components import kpi_row, section_start, section_end, insight_box
from utils.filters import render_sidebar_filters
from utils.auth import require_login

st.set_page_config(page_title="Applicant Demographics", page_icon="🧑", layout="wide")
apply_theme()
require_login()
df = load_data()

sidebar_brand()
filtered = render_sidebar_filters(df, key_prefix="demo_")

topbar(filtered)

page_header("Applicant Demographics", "Who is applying: age, gender, children and dependants across the book.", "🧑")

kpi_row([
    {"label": "Median age", "value": f"{filtered['AGE_YEARS'].median():.0f} yrs", "icon": "🎂"},
    {"label": "% Female applicants", "value": f"{(filtered['GENDER_LABEL']=='Female').mean()*100:.1f}%", "icon": "🚺"},
    {"label": "Avg. children", "value": f"{filtered['CNT_CHILDREN'].mean():.2f}", "icon": "🧒"},
    {"label": "Avg. household size", "value": f"{filtered['CNT_FAM_MEMBERS'].mean():.2f}", "icon": "🏠"},
])

c1, c2 = st.columns(2)
with c1:
    section_start("🎂 Age Distribution by Repayment Outcome", side="left")
    fig = px.histogram(filtered, x="AGE_YEARS", color="RISK_LABEL", nbins=35, barmode="overlay",
                        color_discrete_map=RISK_COLOR_MAP, opacity=0.75)
    fig.update_layout(height=360, legend_title="", xaxis_title="Age (years)")
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    young = filtered[filtered["AGE_YEARS"] < 30]["TARGET"].mean() * 100
    old = filtered[filtered["AGE_YEARS"] >= 30]["TARGET"].mean() * 100
    if young == young and old == old:
        insight_box(
            f"Applicants under 30 default at <b>{young:.1f}%</b> vs <b>{old:.1f}%</b> for those 30+ — "
            f"younger borrowers are consistently the higher-risk age band in this book.",
            tone="warn" if young > old else "info",
        )
    section_end()

with c2:
    section_start("👥 Gender Split & Default Rate", side="right")
    grp = filtered.groupby("GENDER_LABEL").agg(Applicants=("SK_ID_CURR", "count"), Default_rate=("TARGET", "mean")).reset_index()
    grp["Default_rate"] = (grp["Default_rate"] * 100).round(2)
    fig = px.bar(grp, x="GENDER_LABEL", y="Applicants", color="GENDER_LABEL",
                 color_discrete_sequence=PALETTE_RIGHT, text="Default_rate")
    fig.update_traces(texttemplate="Default: %{text}%", textposition="outside")
    fig.update_layout(height=360, showlegend=False, xaxis_title="")
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    if len(grp) >= 2:
        gmax = grp.loc[grp["Default_rate"].idxmax()]
        gmin = grp.loc[grp["Default_rate"].idxmin()]
        insight_box(
            f"<b>{gmax['GENDER_LABEL']}</b> applicants default {gmax['Default_rate'] - gmin['Default_rate']:.1f} points "
            f"more often than <b>{gmin['GENDER_LABEL']}</b> applicants, despite {'similar' if abs(grp['Applicants'].pct_change().iloc[-1]) < 0.5 else 'different'} volumes.",
            tone="info",
        )
    section_end()

c3, c4 = st.columns(2)
with c3:
    section_start("📊 Applicants by Age Group", side="left")
    grp = filtered["AGE_GROUP"].value_counts().sort_index().reset_index()
    grp.columns = ["Age group", "Applicants"]
    fig = px.bar(grp, x="Age group", y="Applicants", color="Applicants",
                 color_continuous_scale=CONTINUOUS_LEFT)
    fig.update_layout(height=340, coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    if len(grp):
        peak = grp.loc[grp["Applicants"].idxmax()]
        insight_box(
            f"The <b>{peak['Age group']}</b> band is the largest applicant pool ({peak['Applicants']:,} applicants) — "
            f"marketing and underwriting capacity should be sized around this group.",
            tone="info",
        )
    section_end()

with c4:
    section_start("🧒 Default Rate vs Number of Children", side="right")
    grp = filtered.groupby("CNT_CHILDREN")["TARGET"].agg(["mean", "count"]).reset_index()
    grp = grp[grp["count"] >= 5]
    grp["mean"] = (grp["mean"] * 100).round(2)
    fig = px.line(grp, x="CNT_CHILDREN", y="mean", markers=True, color_discrete_sequence=[PALETTE_RIGHT[1]])
    fig.update_layout(height=340, xaxis_title="Number of children", yaxis_title="Default rate (%)")
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    if len(grp) >= 2:
        trend = "rises" if grp["mean"].iloc[-1] > grp["mean"].iloc[0] else "falls"
        insight_box(
            f"Default rate generally <b>{trend}</b> with household size, from {grp['mean'].iloc[0]:.1f}% "
            f"({int(grp['CNT_CHILDREN'].iloc[0])} children) to {grp['mean'].iloc[-1]:.1f}% "
            f"({int(grp['CNT_CHILDREN'].iloc[-1])} children) — larger families may carry tighter monthly budgets.",
            tone="warn" if trend == "rises" else "good",
        )
    section_end()

section_start("💍 Marital / Family Status Breakdown")
grp = filtered["NAME_FAMILY_STATUS"].value_counts().reset_index()
grp.columns = ["Family status", "Applicants"]
fig = px.treemap(grp, path=["Family status"], values="Applicants",
                  color="Applicants", color_continuous_scale=CONTINUOUS_LEFT)
fig.update_layout(height=380, coloraxis_showscale=False)
st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
section_end()
