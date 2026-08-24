import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.theme import apply_theme, style_fig, page_header, PLOTLY_CONFIG, sidebar_brand, topbar
from utils.components import kpi_row, section_start, section_end, insight_box
from utils.filters import render_sidebar_filters
from utils.auth import require_login

st.set_page_config(page_title="Application Patterns", page_icon="📅", layout="wide")
apply_theme()
require_login()
df = load_data()

sidebar_brand()
filtered = render_sidebar_filters(df, key_prefix="app_")

topbar(filtered)

page_header("Application Timing Patterns", "When applications are submitted, and whether timing relates to risk.", "📅")

kpi_row([
    {"label": "Busiest weekday", "value": f"{filtered['WEEKDAY_APPR_PROCESS_START'].mode()[0]}", "icon": "📆"},
    {"label": "Peak hour", "value": f"{filtered['APP_HOUR'].mode()[0]}:00", "icon": "⏰"},
    {"label": "Weekend applications", "value": f"{filtered['WEEKDAY_APPR_PROCESS_START'].isin(['SATURDAY','SUNDAY']).mean()*100:.1f}%", "icon": "🎉"},
    {"label": "Off-hours (before 8am/after 8pm)", "value": f"{((filtered['APP_HOUR']<8)|(filtered['APP_HOUR']>20)).mean()*100:.1f}%", "icon": "🌙"},
])

weekday_order = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

c1, c2 = st.columns(2)
with c1:
    section_start("📆 Applications by Weekday")
    grp = filtered["WEEKDAY_APPR_PROCESS_START"].value_counts().reindex(weekday_order).reset_index()
    grp.columns = ["Weekday", "Applications"]
    fig = px.bar(grp, x="Weekday", y="Applications", color="Applications",
                 color_continuous_scale=["#dcebe8", "#4c748c"])
    fig.update_layout(height=360, coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

with c2:
    section_start("⏰ Applications by Hour of Day")
    grp = filtered["APP_HOUR"].value_counts().sort_index().reset_index()
    grp.columns = ["Hour", "Applications"]
    fig = px.area(grp, x="Hour", y="Applications", color_discrete_sequence=["#f59e0b"])
    fig.update_layout(height=360)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    section_end()

section_start("🔥 Default Rate Heatmap — Weekday × Hour")
heat = filtered.groupby(["WEEKDAY_APPR_PROCESS_START", "APP_HOUR"])["TARGET"].mean().mul(100).reset_index()
pivot = heat.pivot(index="WEEKDAY_APPR_PROCESS_START", columns="APP_HOUR", values="TARGET").reindex(weekday_order)
fig = px.imshow(pivot, color_continuous_scale=["#dcebe8", "#f59e0b", "#ef4444"], aspect="auto",
                 labels=dict(x="Hour of day", y="Weekday", color="Default rate %"))
fig.update_layout(height=380)
st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
section_end()
