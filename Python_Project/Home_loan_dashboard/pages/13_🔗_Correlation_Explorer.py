import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.theme import apply_theme, style_fig, page_header, PLOTLY_CONFIG, sidebar_brand, topbar, RISK_COLOR_MAP, DANGER, PRIMARY
from utils.components import section_start, section_end, insight_box
from utils.filters import render_sidebar_filters
from utils.auth import require_login

st.set_page_config(page_title="Correlation Explorer", page_icon="🔗", layout="wide")
apply_theme()
require_login()
df = load_data()

sidebar_brand()
filtered = render_sidebar_filters(df, key_prefix="corr_")

topbar(filtered)

page_header("Correlation Explorer", "Interactively inspect how numeric features relate to each other and to default risk.", "🔗")

numeric_options = [
    "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE",
    "AGE_YEARS", "EMPLOYED_YEARS", "CREDIT_INCOME_RATIO", "ANNUITY_INCOME_RATIO",
    "CREDIT_TERM_YEARS", "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3", "EXT_SOURCE_MEAN",
    "REGION_POPULATION_RELATIVE", "REGION_RATING_CLIENT", "CNT_FAM_MEMBERS", "CNT_CHILDREN",
    "RISK_SCORE", "TARGET",
]

section_start("🧮 Correlation Heatmap")
selected = st.multiselect("Select numeric features to correlate", numeric_options,
                           default=["AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AGE_YEARS",
                                    "CREDIT_INCOME_RATIO", "EXT_SOURCE_MEAN", "TARGET"])
if len(selected) >= 2:
    corr = filtered[selected].corr()
    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale=[DANGER, "#dcebe8", PRIMARY], zmin=-1, zmax=1)
    fig.update_layout(height=520)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)

    if "TARGET" in selected and len(selected) > 1:
        target_corr = corr["TARGET"].drop("TARGET").abs().sort_values(ascending=False)
        if len(target_corr):
            top_feat = target_corr.index[0]
            top_val = corr.loc[top_feat, "TARGET"]
            direction = "inversely" if top_val < 0 else "directly"
            insight_box(
                f"<b>{top_feat}</b> has the strongest relationship with default (<b>TARGET</b>) among the selected "
                f"features, moving {direction} with risk at r = <b>{top_val:.2f}</b>. Correlations near ±0.1–0.3 are "
                f"typical for individual features in credit data — no single variable should be used in isolation.",
                tone="info",
            )
else:
    st.warning("Select at least two features.")
section_end()

section_start("🔬 Custom Scatter Explorer")
c1, c2, c3 = st.columns(3)
x_axis = c1.selectbox("X axis", numeric_options, index=0)
y_axis = c2.selectbox("Y axis", numeric_options, index=1)
color_by = c3.selectbox("Color by", ["RISK_LABEL", "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE", "GENDER_LABEL"], index=0)

plot_df = filtered.dropna(subset=[x_axis, y_axis]).copy()
x_cap, y_cap = plot_df[x_axis].quantile(0.98), plot_df[y_axis].quantile(0.98)
plot_df = plot_df[(plot_df[x_axis] <= x_cap) & (plot_df[y_axis] <= y_cap)]
sample = plot_df.sample(min(2000, len(plot_df)), random_state=1) if len(plot_df) else plot_df

color_map = RISK_COLOR_MAP if color_by == "RISK_LABEL" else None
fig = px.scatter(sample, x=x_axis, y=y_axis, color=color_by, opacity=0.55,
                  color_discrete_map=color_map, color_discrete_sequence=None if color_map else px.colors.qualitative.Set2)
fig.update_layout(height=480)
st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
st.caption(f"Sampled {len(sample):,} of {len(plot_df):,} matching rows (99th-percentile outliers clipped) for smooth rendering.")
section_end()
