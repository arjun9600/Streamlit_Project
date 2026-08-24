import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.theme import apply_theme, style_fig, page_header, PLOTLY_CONFIG, sidebar_brand, topbar
from utils.components import kpi_row, section_start, section_end, insight_box
from utils.filters import render_sidebar_filters
from utils.auth import require_login

st.set_page_config(page_title="Regional Analysis", page_icon="🌍", layout="wide")
apply_theme()
require_login()
df = load_data()

sidebar_brand()
filtered = render_sidebar_filters(df, key_prefix="region_")

topbar(filtered)

page_header("Regional & Address Patterns", "Region ratings, population density and address-mismatch signals.", "🌍")

kpi_row([
    {"label": "Avg. region rating", "value": f"{filtered['REGION_RATING_CLIENT'].mean():.2f}", "icon": "⭐"},
    {"label": "Avg. population density (norm.)", "value": f"{filtered['REGION_POPULATION_RELATIVE'].mean():.4f}", "icon": "🏙️"},
    {"label": "Reg ≠ Live region", "value": f"{(filtered['REG_REGION_NOT_LIVE_REGION']==1).mean()*100:.1f}%", "icon": "📍"},
    {"label": "Reg ≠ Work region", "value": f"{(filtered['REG_REGION_NOT_WORK_REGION']==1).mean()*100:.1f}%", "icon": "🧭"},
])

c1, c2 = st.columns(2)
with c1:
    section_start("⭐ Default Rate by Region Rating")
    grp = filtered.groupby("REGION_RATING_CLIENT")["TARGET"].agg(["mean", "count"]).reset_index()
    grp["mean"] = (grp["mean"] * 100).round(2)
    fig = px.bar(grp, x="REGION_RATING_CLIENT", y="mean", color="mean",
                 color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"], text_auto=".2f")
    fig.update_layout(height=360, xaxis_title="Region rating (1 = best)", yaxis_title="Default rate (%)", coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

with c2:
    section_start("🏙️ Population Density vs Default")
    plot_df = filtered.copy()
    plot_df["density_bin"] = pd.qcut(plot_df["REGION_POPULATION_RELATIVE"], 5,
                                      labels=["Rural", "Low", "Mid", "High", "Urban core"], duplicates="drop")
    grp = plot_df.groupby("density_bin", observed=True)["TARGET"].mean().mul(100).reset_index()
    fig = px.bar(grp, x="density_bin", y="TARGET", color="TARGET",
                 color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"], text_auto=".2f")
    fig.update_layout(height=360, xaxis_title="Population density band", yaxis_title="Default rate (%)", coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

section_start("📍 Address Mismatch Flags vs Default Rate")
mismatch_cols = ["REG_REGION_NOT_LIVE_REGION", "REG_REGION_NOT_WORK_REGION", "LIVE_REGION_NOT_WORK_REGION",
                  "REG_CITY_NOT_LIVE_CITY", "REG_CITY_NOT_WORK_CITY", "LIVE_CITY_NOT_WORK_CITY"]
rows = []
for c in mismatch_cols:
    sub_match = filtered[filtered[c] == 0]["TARGET"].mean() * 100
    sub_mismatch = filtered[filtered[c] == 1]["TARGET"].mean() * 100
    rows.append({"Flag": c, "Match (default %)": round(sub_match, 2), "Mismatch (default %)": round(sub_mismatch, 2)})
mdf = pd.DataFrame(rows).melt(id_vars="Flag", var_name="Status", value_name="Default rate %")
fig = px.bar(mdf, x="Flag", y="Default rate %", color="Status", barmode="group",
             color_discrete_sequence=["#10b981", "#ef4444"])
fig.update_layout(height=380, xaxis_tickangle=-20)
st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
st.caption("A mismatch between registered / live / work addresses is a known soft-fraud & instability signal.")
section_end()
