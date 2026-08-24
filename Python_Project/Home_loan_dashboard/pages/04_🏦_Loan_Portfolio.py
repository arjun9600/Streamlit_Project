import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.theme import apply_theme, style_fig, page_header, PLOTLY_CONFIG, sidebar_brand, topbar, RISK_COLOR_MAP, CATEGORICAL_PALETTE, PALETTE_LEFT, PALETTE_RIGHT
from utils.components import kpi_row, section_start, section_end, insight_box
from utils.filters import render_sidebar_filters
from utils.auth import require_login

st.set_page_config(page_title="Loan Portfolio", page_icon="🏦", layout="wide")
apply_theme()
require_login()
df = load_data()

sidebar_brand()
filtered = render_sidebar_filters(df, key_prefix="loan_")

topbar(filtered)

page_header("Loan Portfolio Structure", "Loan types, sizing, tenor and how much of the book is revolving vs. cash loans.", "🏦")

kpi_row([
    {"label": "Total credit issued", "value": f"${filtered['AMT_CREDIT'].sum():,.0f}", "icon": "💰"},
    {"label": "Avg. loan term", "value": f"{filtered['CREDIT_TERM_YEARS'].median():.1f} yrs", "icon": "🗓️"},
    {"label": "Avg. annuity", "value": f"${filtered['AMT_ANNUITY'].mean():,.0f}", "icon": "🧾"},
    {"label": "Cash loan share", "value": f"{(filtered['NAME_CONTRACT_TYPE']=='Cash loans').mean()*100:.1f}%", "icon": "💵"},
])

c1, c2 = st.columns(2)
with c1:
    section_start("📦 Loan Type Mix", side="left")
    grp = filtered["NAME_CONTRACT_TYPE"].value_counts().reset_index()
    grp.columns = ["Loan type", "Count"]
    fig = px.pie(grp, names="Loan type", values="Count", hole=0.55, color_discrete_sequence=PALETTE_LEFT)
    fig.update_layout(height=360)
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    if len(grp) >= 2:
        share = grp.iloc[0]["Count"] / grp["Count"].sum() * 100
        insight_box(
            f"<b>{grp.iloc[0]['Loan type']}</b> makes up <b>{share:.0f}%</b> of all originations — "
            f"the book is heavily concentrated in one product line, which is worth diversifying against.",
            tone="warn" if share > 80 else "info",
        )
    section_end()

with c2:
    section_start("💳 Credit Amount by Loan Type", side="right")
    fig = px.box(filtered, x="NAME_CONTRACT_TYPE", y="AMT_CREDIT", color="NAME_CONTRACT_TYPE",
                 color_discrete_sequence=PALETTE_RIGHT, points=False)
    fig.update_layout(height=360, showlegend=False, xaxis_title="", yaxis_title="Credit amount ($)")
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    med_by_type = filtered.groupby("NAME_CONTRACT_TYPE")["AMT_CREDIT"].median()
    if len(med_by_type) >= 2:
        insight_box(
            f"Median loan size ranges from ${med_by_type.min():,.0f} to ${med_by_type.max():,.0f} across loan types — "
            f"pricing and risk models should be tuned per product rather than applied uniformly.",
            tone="info",
        )
    section_end()

c3, c4 = st.columns(2)
with c3:
    section_start("🏷️ Goods Price vs Credit Amount", side="left")
    cap = filtered["AMT_CREDIT"].quantile(0.98)
    plot_df = filtered[filtered["AMT_CREDIT"] <= cap].sample(min(1500, len(filtered)), random_state=1)
    fig = px.scatter(plot_df, x="AMT_GOODS_PRICE", y="AMT_CREDIT", color="RISK_LABEL",
                      color_discrete_map=RISK_COLOR_MAP, opacity=0.55)
    fig.add_shape(type="line", x0=0, y0=0, x1=plot_df["AMT_GOODS_PRICE"].max(), y1=plot_df["AMT_GOODS_PRICE"].max(),
                  line=dict(color="#8a93a8", dash="dot"))
    fig.update_layout(height=360, xaxis_title="Goods price ($)", yaxis_title="Credit amount ($)")
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    over_financed = (filtered["AMT_CREDIT"] > filtered["AMT_GOODS_PRICE"]).mean() * 100
    insight_box(
        f"<b>{over_financed:.0f}%</b> of applicants are financed for more than the goods price itself (above the "
        f"dotted parity line) — typically added fees/insurance, but worth monitoring as a leverage signal.",
        tone="info",
    )
    section_end()

with c4:
    section_start("📐 Credit-to-Income Ratio Distribution", side="right")
    cap = filtered["CREDIT_INCOME_RATIO"].quantile(0.97)
    plot_df = filtered[filtered["CREDIT_INCOME_RATIO"] <= cap]
    fig = px.histogram(plot_df, x="CREDIT_INCOME_RATIO", color="RISK_LABEL", nbins=40, barmode="overlay",
                        color_discrete_map=RISK_COLOR_MAP, opacity=0.75)
    fig.update_layout(height=360, legend_title="", xaxis_title="Credit ÷ Income")
    st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
    high_leverage = (filtered["CREDIT_INCOME_RATIO"] > 5).mean() * 100
    insight_box(
        f"<b>{high_leverage:.0f}%</b> of applicants are borrowing more than 5× their annual income — "
        f"this cohort's default rate is {filtered.loc[filtered['CREDIT_INCOME_RATIO'] > 5, 'TARGET'].mean()*100:.1f}% "
        f"vs {filtered.loc[filtered['CREDIT_INCOME_RATIO'] <= 5, 'TARGET'].mean()*100:.1f}% for the rest of the book.",
        tone="warn",
    )
    section_end()

section_start("🧮 Loan Sizing Summary by Contract Type")
tbl = filtered.groupby("NAME_CONTRACT_TYPE").agg(
    Loans=("SK_ID_CURR", "count"),
    **{"Avg credit ($)": ("AMT_CREDIT", "mean")},
    **{"Avg annuity ($)": ("AMT_ANNUITY", "mean")},
    **{"Avg term (yrs)": ("CREDIT_TERM_YEARS", "median")},
    **{"Default rate %": ("TARGET", lambda x: round(x.mean()*100, 2))},
).reset_index()
st.dataframe(tbl, use_container_width=True, hide_index=True)
section_end()
