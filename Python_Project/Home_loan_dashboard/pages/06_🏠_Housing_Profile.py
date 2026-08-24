import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.theme import apply_theme, style_fig, page_header, PLOTLY_CONFIG, sidebar_brand, topbar, CATEGORICAL_PALETTE
from utils.components import kpi_row, section_start, section_end, insight_box
from utils.filters import render_sidebar_filters
from utils.auth import require_login

st.set_page_config(page_title="Housing Profile", page_icon="🏠", layout="wide")
apply_theme()
require_login()
df = load_data()

sidebar_brand()
filtered = render_sidebar_filters(df, key_prefix="house_")

topbar(filtered)

page_header("Housing Profile", "Where applicants live, property quality indicators, and the link to credit risk.", "🏠")

kpi_row([
    {"label": "Most common housing", "value": f"{filtered['NAME_HOUSING_TYPE'].mode()[0]}", "icon": "🏠"},
    {"label": "Own realty", "value": f"{(filtered['FLAG_OWN_REALTY']=='Y').mean()*100:.1f}%", "icon": "🏘️"},
    {"label": "Avg. living area (norm.)", "value": f"{filtered['LIVINGAREA_AVG'].mean():.3f}" if filtered['LIVINGAREA_AVG'].notna().any() else "N/A", "icon": "📐"},
    {"label": "Emergency state flag rate", "value": f"{(filtered['EMERGENCYSTATE_MODE']=='Yes').mean()*100:.1f}%", "icon": "🚨"},
])

c1, c2 = st.columns(2)
with c1:
    section_start("🏘️ Housing Type Distribution")
    grp = filtered["NAME_HOUSING_TYPE"].value_counts().reset_index()
    grp.columns = ["Housing type", "Applicants"]
    fig = px.bar(grp, x="Applicants", y="Housing type", orientation="h", color="Housing type",
                 color_discrete_sequence=CATEGORICAL_PALETTE)
    fig.update_layout(height=380, showlegend=False, yaxis_title="")
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

with c2:
    section_start("⚠️ Default Rate by Housing Type")
    grp = filtered.groupby("NAME_HOUSING_TYPE")["TARGET"].mean().mul(100).sort_values().reset_index()
    fig = px.bar(grp, x="TARGET", y="NAME_HOUSING_TYPE", orientation="h", color="TARGET",
                 color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"], text_auto=".2f")
    fig.update_layout(height=380, xaxis_title="Default rate (%)", yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

c3, c4 = st.columns(2)
with c3:
    section_start("🧱 Wall Material Mix")
    grp = filtered["WALLSMATERIAL_MODE"].value_counts().reset_index()
    grp.columns = ["Wall material", "Count"]
    fig = px.pie(grp, names="Wall material", values="Count", hole=0.5, color_discrete_sequence=CATEGORICAL_PALETTE)
    fig.update_layout(height=360)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

with c4:
    section_start("📐 Property Age (Years Since Construction) vs Default")
    plot_df = filtered.dropna(subset=["YEARS_BUILD_AVG"]).copy()
    if len(plot_df):
        fig = px.histogram(plot_df, x="YEARS_BUILD_AVG", color="RISK_LABEL", nbins=30, barmode="overlay",
                            opacity=0.75, color_discrete_map={"Repaid on time": "#10b981", "Payment difficulty": "#ef4444"})
        fig.update_layout(height=360, xaxis_title="Normalized building age score", legend_title="")
        st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    else:
        st.info("No building-age data available for the current filter selection.")
    section_end()

section_start("🏡 Housing × Realty Ownership Summary")
tbl = filtered.groupby(["NAME_HOUSING_TYPE", "OWN_REALTY_LABEL"]).agg(
    Applicants=("SK_ID_CURR", "count"),
    **{"Default rate %": ("TARGET", lambda x: round(x.mean()*100, 2))},
).reset_index().sort_values("Applicants", ascending=False)
st.dataframe(tbl, use_container_width=True, hide_index=True)
section_end()
