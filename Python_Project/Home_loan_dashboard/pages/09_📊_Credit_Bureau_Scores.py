import streamlit as st
import plotly.express as px
import pandas as pd

from utils.data_loader import load_data
from utils.theme import apply_theme, style_fig, page_header, PLOTLY_CONFIG, sidebar_brand, topbar, RISK_COLOR_MAP
from utils.components import kpi_row, section_start, section_end, insight_box
from utils.filters import render_sidebar_filters
from utils.auth import require_login

st.set_page_config(page_title="Credit Bureau Scores", page_icon="📊", layout="wide")
apply_theme()
require_login()
df = load_data()

sidebar_brand()
filtered = render_sidebar_filters(df, key_prefix="ext_")

topbar(filtered)

page_header("External Credit Bureau Scores", "EXT_SOURCE_1/2/3 are normalized external scoring signals — the strongest known predictors of default in this data.", "📊")

kpi_row([
    {"label": "Avg. EXT_SOURCE_1", "value": f"{filtered['EXT_SOURCE_1'].mean():.3f}" if filtered['EXT_SOURCE_1'].notna().any() else "N/A", "icon": "①"},
    {"label": "Avg. EXT_SOURCE_2", "value": f"{filtered['EXT_SOURCE_2'].mean():.3f}" if filtered['EXT_SOURCE_2'].notna().any() else "N/A", "icon": "②"},
    {"label": "Avg. EXT_SOURCE_3", "value": f"{filtered['EXT_SOURCE_3'].mean():.3f}" if filtered['EXT_SOURCE_3'].notna().any() else "N/A", "icon": "③"},
    {"label": "Avg. composite score", "value": f"{filtered['EXT_SOURCE_MEAN'].mean():.3f}", "icon": "🧮"},
])

c1, c2 = st.columns(2)
with c1:
    section_start("📉 Score Distribution by Repayment Outcome")
    src = st.selectbox("Choose bureau score", ["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3", "EXT_SOURCE_MEAN"], index=3)
    plot_df = filtered.dropna(subset=[src])
    fig = px.histogram(plot_df, x=src, color="RISK_LABEL", nbins=40, barmode="overlay",
                        color_discrete_map=RISK_COLOR_MAP, opacity=0.75)
    fig.update_layout(height=380, legend_title="")
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

with c2:
    section_start("🔗 Score Correlation Matrix")
    corr = filtered[["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3", "TARGET"]].corr()
    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale=["#ef4444", "#dcebe8", "#4c748c"], zmin=-1, zmax=1)
    fig.update_layout(height=380)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

section_start("🎯 Default Rate by Composite Score Decile")
plot_df = filtered.dropna(subset=["EXT_SOURCE_MEAN"]).copy()
plot_df["decile"] = pd.qcut(plot_df["EXT_SOURCE_MEAN"], 10, labels=[f"D{i}" for i in range(1, 11)], duplicates="drop")
grp = plot_df.groupby("decile", observed=True)["TARGET"].mean().mul(100).reset_index()
fig = px.bar(grp, x="decile", y="TARGET", color="TARGET",
             color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"], text_auto=".1f")
fig.update_layout(height=380, xaxis_title="Composite score decile (D1 = lowest score)", yaxis_title="Default rate (%)", coloraxis_showscale=False)
st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
st.caption("A clear downward-sloping default rate across deciles confirms the external bureau scores are strongly predictive.")
section_end()

section_start("📈 Score Missingness")
miss = filtered[["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]].isna().mean().mul(100).reset_index()
miss.columns = ["Score", "% Missing"]
fig = px.bar(miss, x="Score", y="% Missing", color="Score", color_discrete_sequence=["#4c748c", "#f59e0b", "#3d5f73"])
fig.update_layout(height=300, showlegend=False)
st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
section_end()
