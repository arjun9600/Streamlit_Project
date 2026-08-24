import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.theme import apply_theme, style_fig, page_header, PLOTLY_CONFIG, sidebar_brand, topbar, RISK_GRADIENT
from utils.components import kpi_row, section_start, section_end, insight_box
from utils.filters import render_sidebar_filters
from utils.auth import require_login

st.set_page_config(page_title="Default Risk Drivers", page_icon="⚠️", layout="wide")
apply_theme()
require_login()
df = load_data()

sidebar_brand()
filtered = render_sidebar_filters(df, key_prefix="drivers_")

topbar(filtered)

page_header("Default Risk Drivers", "Which applicant attributes correlate most strongly with repayment difficulty.", "⚠️")

kpi_row([
    {"label": "Highest-risk occupation", "value": f"{filtered.groupby('OCCUPATION_TYPE')['TARGET'].mean().idxmax() if filtered['OCCUPATION_TYPE'].notna().any() else 'N/A'}", "icon": "🧑‍💼"},
    {"label": "Highest-risk housing type", "value": f"{filtered.groupby('NAME_HOUSING_TYPE')['TARGET'].mean().idxmax()}", "icon": "🏠"},
    {"label": "Applicants w/o car", "value": f"{(filtered['FLAG_OWN_CAR']=='N').mean()*100:.1f}%", "icon": "🚗"},
    {"label": "Applicants w/o property", "value": f"{(filtered['FLAG_OWN_REALTY']=='N').mean()*100:.1f}%", "icon": "🏘️"},
])

c1, c2 = st.columns(2)
with c1:
    section_start("🧑‍💼 Default Rate by Occupation (min. 20 applicants)", side="left")
    grp = filtered.groupby("OCCUPATION_TYPE")["TARGET"].agg(["mean", "count"]).reset_index()
    grp = grp[grp["count"] >= 20]
    grp["mean"] = (grp["mean"] * 100).round(2)
    grp = grp.sort_values("mean", ascending=True)
    fig = px.bar(grp, x="mean", y="OCCUPATION_TYPE", orientation="h", color="mean",
                 color_continuous_scale=RISK_GRADIENT)
    fig.update_layout(height=460, xaxis_title="Default rate (%)", yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    if len(grp) >= 2:
        insight_box(
            f"<b>{grp.iloc[-1]['OCCUPATION_TYPE']}</b> has the highest default rate at "
            f"<b>{grp.iloc[-1]['mean']:.1f}%</b> among occupations with meaningful volume — "
            f"a strong candidate for occupation-based risk pricing tiers.",
            tone="warn",
        )
    section_end()

with c2:
    section_start("🚗🏘️ Asset Ownership vs Default Rate", side="right")
    own = filtered.groupby(["OWN_CAR_LABEL", "OWN_REALTY_LABEL"])["TARGET"].mean().mul(100).reset_index()
    own["combo"] = own["OWN_CAR_LABEL"] + " / " + own["OWN_REALTY_LABEL"]
    own = own.sort_values("TARGET")
    fig = px.bar(own, x="TARGET", y="combo", orientation="h", color="TARGET",
                 color_continuous_scale=RISK_GRADIENT, text_auto=".2f")
    fig.update_layout(height=460, xaxis_title="Default rate (%)", yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    if len(own) >= 2:
        insight_box(
            f"Applicants with <b>{own.iloc[0]['combo']}</b> default least ({own.iloc[0]['TARGET']:.1f}%), while "
            f"<b>{own.iloc[-1]['combo']}</b> default most ({own.iloc[-1]['TARGET']:.1f}%) — asset ownership is a "
            f"cheap, verifiable proxy for financial stability.",
            tone="info",
        )
    section_end()

c3, c4 = st.columns(2)
with c3:
    section_start("🏢 Default Rate by Organization Type (top 15 by volume)", side="left")
    top_orgs = filtered["ORGANIZATION_TYPE"].value_counts().head(15).index
    grp = filtered[filtered["ORGANIZATION_TYPE"].isin(top_orgs)].groupby("ORGANIZATION_TYPE")["TARGET"].mean().mul(100).sort_values().reset_index()
    fig = px.bar(grp, x="TARGET", y="ORGANIZATION_TYPE", orientation="h", color="TARGET",
                 color_continuous_scale=RISK_GRADIENT)
    fig.update_layout(height=440, xaxis_title="Default rate (%)", yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    if len(grp) >= 2:
        insight_box(
            f"Default rates across major employer types range from {grp['TARGET'].min():.1f}% to "
            f"{grp['TARGET'].max():.1f}% — <b>{grp.iloc[-1]['ORGANIZATION_TYPE']}</b> is the riskiest large segment.",
            tone="warn",
        )
    section_end()

with c4:
    section_start("💼 Years Employed vs Default Rate", side="right")
    plot_df = filtered.dropna(subset=["EMPLOYED_YEARS"]).copy()
    plot_df["EMP_BUCKET"] = pd.cut(
        plot_df["EMPLOYED_YEARS"], bins=[0, 1, 3, 5, 10, 20, 50],
        labels=["<1", "1-3", "3-5", "5-10", "10-20", "20+"]
    )
    grp = plot_df.groupby("EMP_BUCKET", observed=True)["TARGET"].mean().mul(100).reset_index()
    fig = px.bar(grp, x="EMP_BUCKET", y="TARGET", color="TARGET",
                 color_continuous_scale=RISK_GRADIENT, text_auto=".2f")
    fig.update_layout(height=440, xaxis_title="Years employed", yaxis_title="Default rate (%)", coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    if len(grp) >= 2:
        insight_box(
            f"Tenure matters: applicants employed <b>&lt;1 year</b> default at {grp.iloc[0]['TARGET']:.1f}% vs "
            f"{grp.iloc[-1]['TARGET']:.1f}% for those with 20+ years — job stability is one of the cleanest risk signals available.",
            tone="warn" if grp.iloc[0]["TARGET"] > grp.iloc[-1]["TARGET"] else "info",
        )
    section_end()

section_start("🧾 Top Risk-Correlated Flags")
flag_cols = ["FLAG_OWN_CAR", "FLAG_OWN_REALTY", "FLAG_WORK_PHONE", "FLAG_PHONE", "FLAG_EMAIL"]
rows = []
for f in flag_cols:
    for val in filtered[f].dropna().unique():
        sub = filtered[filtered[f] == val]
        rows.append({"Flag": f, "Value": str(val), "Applicants": len(sub), "Default rate %": round(sub["TARGET"].mean()*100, 2)})
st.dataframe(pd.DataFrame(rows).sort_values("Default rate %", ascending=False), use_container_width=True, hide_index=True)
section_end()
