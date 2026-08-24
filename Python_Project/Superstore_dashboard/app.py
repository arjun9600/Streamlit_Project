import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.filters import render_search_bar
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="Superstore Command Center", layout="wide", initial_sidebar_state="expanded")
apply_custom_theme()

# Gate the whole app behind the login screen
require_login()

st.title("🏆 Superstore Executive Analytics Suite")
st.caption("Next-Generation Business Intelligence Dashboard")

df = load_data()

# Sidebar: global filters + logout
st.sidebar.header("🕹️ Global Controls")
selected_region = st.sidebar.multiselect("Region", df['Region'].unique(), default=df['Region'].unique())
selected_year = st.sidebar.multiselect("Year", df['Order Date'].dt.year.unique(), default=df['Order Date'].dt.year.unique())
render_logout()

filtered_df = df[(df['Region'].isin(selected_region)) & (df['Order Date'].dt.year.isin(selected_year))]

# Working global search bar
filtered_df, _search_query = render_search_bar(filtered_df)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Revenue", f"${filtered_df['Sales'].sum():,.2f}")
col2.metric("Net Profit", f"${filtered_df['Profit'].sum():,.2f}")
col3.metric("Profit Margin", f"{(filtered_df['Profit'].sum()/filtered_df['Sales'].sum()*100):.1f}%")
col4.metric("Total Orders", f"{filtered_df['Order ID'].nunique():,}")
col5.metric("Avg Order Value", f"${(filtered_df['Sales'].sum()/filtered_df['Order ID'].nunique()):,.2f}")

st.markdown("---")

c1, c2 = st.columns(2)
with c1:
    st.subheader("📈 Monthly Revenue Trend")
    # NOTE: pandas removed the 'M' offset alias — use 'ME' (month-end) instead,
    # otherwise this raises: ValueError: 'M' is no longer supported for offsets.
    monthly = filtered_df.resample('ME', on='Order Date')['Sales'].sum().reset_index()
    fig1 = px.area(monthly, x='Order Date', y='Sales', markers=True, color_discrete_sequence=[PALETTE[0]])
    fig1.update_traces(line=dict(color=PALETTE[0], width=3), fillcolor="rgba(20,232,30,0.15)",
                        marker=dict(color=PALETTE[1], size=6))
    st.plotly_chart(style_fig(fig1), use_container_width=True)

with c2:
    st.subheader("🎯 Profitability by Category")
    cat_df = filtered_df.groupby('Category')[['Sales', 'Profit']].sum().reset_index()
    fig2 = px.bar(cat_df, x='Category', y=['Sales', 'Profit'], barmode='group',
                   color_discrete_sequence=[PALETTE[2], PALETTE[0]])
    st.plotly_chart(style_fig(fig2), use_container_width=True)

# ---- Dynamic business insights ----
if not filtered_df.empty and filtered_df['Sales'].sum() > 0:
    best_month_row = monthly.loc[monthly['Sales'].idxmax()]
    cat_sorted = cat_df.sort_values('Profit', ascending=False)
    top_cat = cat_sorted.iloc[0]
    bottom_cat = cat_sorted.iloc[-1]
    overall_margin = filtered_df['Profit'].sum() / filtered_df['Sales'].sum() * 100

    points = [
        f"Peak revenue month is <b>{best_month_row['Order Date'].strftime('%B %Y')}</b> with ${best_month_row['Sales']:,.0f} in sales — worth investigating what drove the spike (promo, seasonality, big orders) so it can be repeated.",
        f"<b>{top_cat['Category']}</b> is the profit engine of the business (${top_cat['Profit']:,.0f} profit); <b>{bottom_cat['Category']}</b> trails at ${bottom_cat['Profit']:,.0f} — worth a pricing/discount review.",
        f"Blended profit margin across the current filter is <b>{overall_margin:.1f}%</b> — track this against your target margin as a single north-star health metric.",
    ]
    insight_box("Executive summary for the selected Region / Year filters", points)
