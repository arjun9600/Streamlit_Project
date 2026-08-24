import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_data
from utils.theme import apply_theme, style_fig, page_header, PLOTLY_CONFIG, sidebar_brand, topbar, RISK_COLOR_MAP, DANGER, SAFE, GOLD, PRIMARY, RISK_GRADIENT
from utils.components import kpi_row, section_start, section_end, insight_box
from utils.filters import render_sidebar_filters
from utils.auth import require_login

st.set_page_config(page_title="Risk Overview", page_icon="🎯", layout="wide")
apply_theme()
require_login()
df = load_data()

sidebar_brand()
filtered = render_sidebar_filters(df, key_prefix="risk_")

topbar(filtered)

page_header("Risk Overview", "Portfolio-level default risk, benchmarked against the overall book.", "🎯")

overall_rate = df["TARGET"].mean() * 100
seg_rate = filtered["TARGET"].mean() * 100 if len(filtered) else 0
high_risk_ct = int((filtered["RISK_SCORE"] >= 60).sum())

kpi_row([
    {"label": "Segment default rate", "value": f"{seg_rate:.2f}%", "icon": "⚠️"},
    {"label": "Portfolio benchmark", "value": f"{overall_rate:.2f}%", "icon": "📊"},
    {"label": "High in-house risk score (≥60)", "value": f"{high_risk_ct:,}", "icon": "🔴"},
    {"label": "Avg. in-house risk score", "value": f"{filtered['RISK_SCORE'].mean():.1f}/100", "icon": "🧮"},
])

c1, c2 = st.columns([1, 1.4])
with c1:
    section_start("🌡️ Segment Risk Gauge", side="left")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=seg_rate,
        delta={"reference": overall_rate, "increasing": {"color": DANGER}, "decreasing": {"color": SAFE}},
        number={"suffix": "%", "font": {"color": "#0f172a"}},
        gauge={
            "axis": {"range": [0, max(20, seg_rate * 1.5)], "tickcolor": "#8a93a8"},
            "bar": {"color": PRIMARY},
            "steps": [
                {"range": [0, 6], "color": "rgba(52,211,153,0.25)"},
                {"range": [6, 12], "color": "rgba(240,180,41,0.25)"},
                {"range": [12, 25], "color": "rgba(251,91,108,0.25)"},
            ],
            "threshold": {"line": {"color": DANGER, "width": 3}, "value": overall_rate},
        },
    ))
    fig.update_layout(height=320)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    st.caption("Red line marks the full-portfolio benchmark default rate.")
    gap = seg_rate - overall_rate
    insight_box(
        f"This segment is running <b>{abs(gap):.1f} points {'above' if gap > 0 else 'below'}</b> the portfolio "
        f"benchmark ({seg_rate:.1f}% vs {overall_rate:.1f}%) — "
        f"{'flag for tighter underwriting criteria on this slice.' if gap > 0 else 'this slice is currently outperforming the book.'}",
        tone="warn" if gap > 0 else "good",
    )
    section_end()

with c2:
    section_start("📉 In-House Risk Score Distribution", side="right")
    fig = px.histogram(filtered, x="RISK_SCORE", color="RISK_LABEL", nbins=40, barmode="overlay",
                        color_discrete_map=RISK_COLOR_MAP, opacity=0.75)
    fig.add_vline(x=60, line_dash="dash", line_color=GOLD, annotation_text="Watch threshold")
    fig.update_layout(height=320, legend_title="")
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    watch_pct = (filtered["RISK_SCORE"] >= 60).mean() * 100
    insight_box(
        f"<b>{watch_pct:.1f}%</b> of applicants in view sit above the 60/100 watch threshold. "
        f"That group should be prioritized for manual review before disbursement.",
        tone="warn" if watch_pct > 15 else "info",
    )
    section_end()

c3, c4 = st.columns(2)
with c3:
    section_start("🏛️ Default Rate by Education", side="left")
    grp = filtered.groupby("NAME_EDUCATION_TYPE")["TARGET"].agg(["mean", "count"]).reset_index()
    grp["mean"] = (grp["mean"] * 100).round(2)
    grp = grp.sort_values("mean")
    fig = px.bar(grp, x="mean", y="NAME_EDUCATION_TYPE", orientation="h", color="mean",
                 color_continuous_scale=RISK_GRADIENT, text="mean")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=340, xaxis_title="Default rate (%)", yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    if len(grp) >= 2:
        insight_box(
            f"<b>{grp.iloc[-1]['NAME_EDUCATION_TYPE']}</b> applicants default {grp.iloc[-1]['mean'] - grp.iloc[0]['mean']:.1f} "
            f"points more often than <b>{grp.iloc[0]['NAME_EDUCATION_TYPE']}</b> holders — education level is a strong, "
            f"stable proxy for repayment ability across the book.",
            tone="info",
        )
    section_end()

with c4:
    section_start("👤 Default Rate by Family Status", side="right")
    grp = filtered.groupby("NAME_FAMILY_STATUS")["TARGET"].agg(["mean", "count"]).reset_index()
    grp["mean"] = (grp["mean"] * 100).round(2)
    grp = grp.sort_values("mean")
    fig = px.bar(grp, x="mean", y="NAME_FAMILY_STATUS", orientation="h", color="mean",
                 color_continuous_scale=RISK_GRADIENT, text="mean")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=340, xaxis_title="Default rate (%)", yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    if len(grp) >= 2:
        insight_box(
            f"<b>{grp.iloc[-1]['NAME_FAMILY_STATUS']}</b> applicants show the highest default rate "
            f"({grp.iloc[-1]['mean']:.1f}%); <b>{grp.iloc[0]['NAME_FAMILY_STATUS']}</b> the lowest ({grp.iloc[0]['mean']:.1f}%).",
            tone="warn",
        )
    section_end()

section_start("🧾 Risk Segments Reference Table")
seg_table = filtered.groupby("NAME_INCOME_TYPE").agg(
    Applicants=("SK_ID_CURR", "count"),
    **{"Default rate %": ("TARGET", lambda x: round(x.mean() * 100, 2))},
    **{"Avg risk score": ("RISK_SCORE", lambda x: round(x.mean(), 1))},
    **{"Avg loan ($)": ("AMT_CREDIT", lambda x: round(x.mean(), 0))},
).reset_index().sort_values("Default rate %", ascending=False)
st.dataframe(seg_table, use_container_width=True, hide_index=True)
section_end()
