import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from utils.data_loader import load_data
from utils.theme import (apply_theme, style_fig, page_header, PLOTLY_CONFIG, sidebar_brand, topbar,
                          welcome_banner, current_user, CATEGORICAL_PALETTE, RISK_COLOR_MAP,
                          PRIMARY, GOLD, DANGER, SAFE, PALETTE_LEFT, PALETTE_RIGHT, RISK_GRADIENT)
from utils.components import kpi_row, section_start, section_end, insight_box
from utils.filters import render_sidebar_filters
from utils.auth import require_login

st.set_page_config(page_title="Home Loan Risk Intelligence", page_icon="🏦", layout="wide", initial_sidebar_state="expanded")
apply_theme()
require_login()

df = load_data()

sidebar_brand()
st.sidebar.caption("Loan portfolio & default-risk analytics")
st.sidebar.markdown("---")
filtered = render_sidebar_filters(df, key_prefix="home_")

topbar(filtered)

# ---------------------------------------------------------------- KPIs ----
default_rate = filtered["TARGET"].mean() * 100 if len(filtered) else 0
avg_credit = filtered["AMT_CREDIT"].mean() if len(filtered) else 0
avg_income = filtered["AMT_INCOME_TOTAL"].mean() if len(filtered) else 0
avg_ratio = filtered["CREDIT_INCOME_RATIO"].replace([float("inf")], None).mean() if len(filtered) else 0
avg_ext = filtered["EXT_SOURCE_MEAN"].mean() if len(filtered) else 0

u = current_user()
first_name = u["name"].split(" ")[0]
hour = datetime.now().hour
greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 18 else "Good evening")
welcome_banner(
    f"{greeting}, {first_name}",
    f"{len(filtered):,} applicants in view — portfolio default rate is holding at {default_rate:.2f}% this period.",
    pill_text=f"📅 {datetime.now().strftime('%A, %b %d')}",
)

kpi_row([
    {"label": "Applicants in view", "value": f"{len(filtered):,}", "icon": "👥"},
    {"label": "Default rate", "value": f"{default_rate:.2f}%", "icon": "⚠️",
     "delta": "of applicants had repayment difficulty", "delta_dir": "up" if default_rate > df['TARGET'].mean()*100 else "down"},
    {"label": "Avg. loan amount", "value": f"${avg_credit:,.0f}", "icon": "💰"},
    {"label": "Avg. annual income", "value": f"${avg_income:,.0f}", "icon": "💵"},
    {"label": "Avg. credit / income", "value": f"{avg_ratio:.1f}×", "icon": "📐"},
    {"label": "Avg. bureau score", "value": f"{avg_ext:.2f}" if avg_ext == avg_ext else "N/A", "icon": "🧮"},
])

st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns([1.3, 1])

# ---- LEFT column: cool palette -------------------------------------------
with c1:
    section_start("📈 Loan Volume & Default Rate by Loan Type", side="left")
    grp = filtered.groupby("NAME_CONTRACT_TYPE").agg(
        applicants=("SK_ID_CURR", "count"),
        default_rate=("TARGET", "mean"),
        avg_credit=("AMT_CREDIT", "mean"),
    ).reset_index()
    grp["default_rate"] = (grp["default_rate"] * 100).round(2)
    fig = go.Figure()
    fig.add_bar(x=grp["NAME_CONTRACT_TYPE"], y=grp["applicants"], name="Applicants",
                marker_color=PALETTE_LEFT[0], yaxis="y1")
    fig.add_trace(go.Scatter(x=grp["NAME_CONTRACT_TYPE"], y=grp["default_rate"], name="Default rate %",
                              mode="lines+markers", marker_color=PALETTE_LEFT[2], yaxis="y2", line=dict(width=3)))
    fig.update_layout(
        yaxis=dict(title="Applicants"),
        yaxis2=dict(title="Default rate %", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=360,
    )
    st.plotly_chart(style_fig(fig, side="left"), use_container_width=True, config=PLOTLY_CONFIG)

    if len(grp) >= 2:
        top_vol = grp.sort_values("applicants", ascending=False).iloc[0]
        top_risk = grp.sort_values("default_rate", ascending=False).iloc[0]
        insight_box(
            f"<b>{top_vol['NAME_CONTRACT_TYPE']}</b> drives most of the book ({top_vol['applicants']:,} applicants), "
            f"but <b>{top_risk['NAME_CONTRACT_TYPE']}</b> carries the higher default rate at "
            f"<b>{top_risk['default_rate']:.1f}%</b> — volume and risk aren't concentrated in the same product.",
            tone="warn" if top_risk["default_rate"] > default_rate else "info",
        )
    section_end()

with c1:
    section_start("💳 Credit Amount Distribution", side="left")
    fig = px.histogram(filtered, x="AMT_CREDIT", color="RISK_LABEL", barmode="overlay", nbins=40,
                        color_discrete_map=RISK_COLOR_MAP, opacity=0.75)
    fig.update_layout(height=340, legend_title="")
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    med_ok = filtered.loc[filtered["RISK_LABEL"] == "Repaid on time", "AMT_CREDIT"].median()
    med_bad = filtered.loc[filtered["RISK_LABEL"] == "Payment difficulty", "AMT_CREDIT"].median()
    if med_ok == med_ok and med_bad == med_bad:
        diff_pct = (med_bad - med_ok) / med_ok * 100 if med_ok else 0
        direction = "higher" if diff_pct > 0 else "lower"
        insight_box(
            f"Applicants who ran into repayment difficulty had a <b>{abs(diff_pct):.0f}% {direction}</b> "
            f"median loan amount (${med_bad:,.0f}) than those who repaid on time (${med_ok:,.0f}) — "
            f"loan size alone is a useful early screening signal.",
            tone="warn" if diff_pct > 0 else "good",
        )
    section_end()

# ---- RIGHT column: warm palette -------------------------------------------
with c2:
    section_start("🎯 Repayment Outcome Split", side="right")
    outcome = filtered["RISK_LABEL"].value_counts().reset_index()
    outcome.columns = ["Outcome", "Count"]
    fig = px.pie(outcome, names="Outcome", values="Count", hole=0.62,
                 color="Outcome", color_discrete_map=RISK_COLOR_MAP)
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(height=360, showlegend=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    insight_box(
        f"<b>{default_rate:.1f}%</b> of the current view has hit repayment difficulty. "
        f"{'That is above the full-portfolio average of ' + format(df['TARGET'].mean()*100, '.1f') + '% — this segment merits closer underwriting review.' if default_rate > df['TARGET'].mean()*100 else 'That tracks close to the full-portfolio average, indicating this segment is not an outlier risk pocket.'}",
        tone="warn" if default_rate > df["TARGET"].mean() * 100 else "good",
    )
    section_end()

    section_start("🧬 Default Rate by Income Type", side="right")
    grp2 = filtered.groupby("NAME_INCOME_TYPE")["TARGET"].mean().mul(100).sort_values(ascending=True).reset_index()
    fig = px.bar(grp2, x="TARGET", y="NAME_INCOME_TYPE", orientation="h",
                 color="TARGET", color_continuous_scale=RISK_GRADIENT)
    fig.update_layout(height=340, xaxis_title="Default rate (%)", yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    if len(grp2) >= 2:
        riskiest = grp2.iloc[-1]
        safest = grp2.iloc[0]
        spread = riskiest["TARGET"] - safest["TARGET"]
        insight_box(
            f"<b>{riskiest['NAME_INCOME_TYPE']}</b> applicants default at <b>{riskiest['TARGET']:.1f}%</b> vs. just "
            f"<b>{safest['TARGET']:.1f}%</b> for <b>{safest['NAME_INCOME_TYPE']}</b> — a {spread:.1f} point spread. "
            f"Income type is one of the sharpest risk-segmentation levers in this book.",
            tone="warn",
        )
    section_end()

st.info("👈 Use the pages in the sidebar to explore Demographics, Income, Loan Portfolio, Risk Drivers, Housing, Credit Bureau Scores, Regional patterns, Document verification, Correlations and the Applicant Explorer.", icon="🧭")
