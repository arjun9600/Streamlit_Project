import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import PALETTE, CONTINUOUS, style_fig, insight_box

st.set_page_config(page_title="Profit Analysis", layout="wide")
apply_custom_theme()
require_login()

st.title("Profit Analysis")
st.caption("Profit margins and loss mitigation.")

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

col_a, col_b = st.columns(2)
subcat_profit = filtered.groupby('Sub-Category').agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum')).reset_index()
subcat_profit['Margin %'] = (subcat_profit['Profit'] / subcat_profit['Sales'] * 100).round(1)
with col_a:
    fig1 = px.bar(subcat_profit.sort_values('Profit'), x='Profit', y='Sub-Category', orientation='h',
                   color='Margin %', color_continuous_scale=CONTINUOUS, title="Profit by Sub-Category")
    st.plotly_chart(style_fig(fig1, height=480), use_container_width=True)

with col_b:
    fig2 = px.histogram(filtered, x='Margin %', nbins=40, title="Profit Margin Distribution",
                         color_discrete_sequence=[PALETTE[1]])
    st.plotly_chart(style_fig(fig2), use_container_width=True)

if not filtered.empty and not subcat_profit.empty:
    best = subcat_profit.sort_values('Profit', ascending=False).iloc[0]
    worst = subcat_profit.sort_values('Profit', ascending=True).iloc[0]
    overall_margin = filtered['Profit'].sum() / filtered['Sales'].sum() * 100 if filtered['Sales'].sum() else 0
    points = [
        f"<b>{best['Sub-Category']}</b> generates the most profit (${best['Profit']:,.0f}, {best['Margin %']:.1f}% margin) — a strong candidate for extra marketing spend.",
        f"<b>{worst['Sub-Category']}</b> is the weakest at ${worst['Profit']:,.0f} profit ({worst['Margin %']:.1f}% margin) — {'it is actively losing money' if worst['Profit'] < 0 else 'margins here are thin'} and worth a pricing or cost review.",
        f"Overall blended margin is <b>{overall_margin:.1f}%</b> across the current filter.",
    ]
    insight_box("Where profit is made — and lost", points)

st.subheader("Detailed Records")
st.dataframe(filtered[['Order ID', 'Order Date', 'Region', 'Category', 'Sub-Category', 'Sales', 'Profit']].head(50), use_container_width=True)
