import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="Regional Performance", layout="wide")
apply_custom_theme()
require_login()

st.title("Regional Performance")
st.caption("Cross-regional KPI benchmarks.")

df = load_data()

st.sidebar.header("Filter Options")
render_logout()
reg = st.sidebar.multiselect("Select Region", df['Region'].unique(), default=df['Region'].unique())
cat = st.sidebar.multiselect("Select Category", df['Category'].unique(), default=df['Category'].unique())

filtered = df[(df['Region'].isin(reg)) & (df['Category'].isin(cat))]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Selected Sales", f"${filtered['Sales'].sum():,.2f}")
k2.metric("Selected Profit", f"${filtered['Profit'].sum():,.2f}")
k3.metric("Volume Sold", f"{filtered['Quantity'].sum():,}")
k4.metric("Avg Discount", f"{filtered['Discount'].mean()*100:.1f}%")

st.markdown("---")

region_df = filtered.groupby('Region').agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum')).reset_index()
region_df['Margin %'] = (region_df['Profit'] / region_df['Sales'] * 100).round(1)

col_a, col_b = st.columns(2)
with col_a:
    fig1 = px.bar(region_df.sort_values('Sales', ascending=False), x='Region', y=['Sales', 'Profit'],
                   barmode='group', title="Sales & Profit by Region", color_discrete_sequence=[PALETTE[2], PALETTE[0]])
    st.plotly_chart(style_fig(fig1), use_container_width=True)

with col_b:
    fig2 = px.bar(region_df.sort_values('Margin %', ascending=False), x='Region', y='Margin %', color='Margin %',
                   title="Profit Margin % by Region", color_continuous_scale=PALETTE)
    st.plotly_chart(style_fig(fig2), use_container_width=True)

if not region_df.empty:
    best_margin = region_df.sort_values('Margin %', ascending=False).iloc[0]
    worst_margin = region_df.sort_values('Margin %', ascending=True).iloc[0]
    top_sales = region_df.sort_values('Sales', ascending=False).iloc[0]
    points = [
        f"<b>{top_sales['Region']}</b> is the top region by revenue (${top_sales['Sales']:,.0f}).",
        f"<b>{best_margin['Region']}</b> converts sales to profit most efficiently at <b>{best_margin['Margin %']:.1f}%</b> margin — study what it's doing differently (pricing, mix, discounting).",
        f"<b>{worst_margin['Region']}</b> lags at <b>{worst_margin['Margin %']:.1f}%</b> margin — a good candidate for a discount policy or cost audit.",
    ]
    insight_box("Benchmarking regions against each other", points)

st.subheader("Detailed Records")
st.dataframe(filtered[['Order ID', 'Order Date', 'Region', 'Category', 'Sub-Category', 'Sales', 'Profit']].head(50), use_container_width=True)
