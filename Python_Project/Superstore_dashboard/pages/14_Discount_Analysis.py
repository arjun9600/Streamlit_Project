import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="Discount Sensitivity", layout="wide")
apply_custom_theme()
require_login()

st.title("Discount Sensitivity")
st.caption("Discount impact on profit margins.")

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

disc_cat = filtered.groupby('Category')['Discount'].mean().reset_index()

col_a, col_b = st.columns(2)
with col_a:
    fig1 = px.scatter(filtered, x='Discount', y='Profit', color='Category', trendline=None,
                       title="Discount vs Profit", color_discrete_sequence=PALETTE)
    st.plotly_chart(style_fig(fig1), use_container_width=True)

with col_b:
    fig2 = px.bar(disc_cat.sort_values('Discount', ascending=False), x='Category', y='Discount', color='Category',
                   title="Average Discount Rate by Category", color_discrete_sequence=PALETTE)
    fig2.update_yaxes(tickformat=".0%")
    st.plotly_chart(style_fig(fig2), use_container_width=True)

if not filtered.empty:
    corr = filtered['Discount'].corr(filtered['Profit'])
    heavy_discount = disc_cat.sort_values('Discount', ascending=False).iloc[0]
    loss_at_high_discount = filtered[filtered['Discount'] >= 0.3]['Profit'].sum()
    points = [
        f"Discount and profit move together with a correlation of <b>{corr:.2f}</b> — {'the more you discount, the less you keep' if corr < -0.1 else 'discounting does not appear to be strongly eroding profit here'}.",
        f"<b>{heavy_discount['Category']}</b> carries the highest average discount rate ({heavy_discount['Discount']*100:.0f}%) — a natural place to tighten discount caps first.",
        f"Orders with 30%+ discount contribute ${loss_at_high_discount:,.0f} in combined profit — check whether that's still net-positive or a hidden loss driver.",
    ]
    insight_box("Is discounting helping or hurting margin", points)

st.subheader("Detailed Records")
st.dataframe(filtered[['Order ID', 'Order Date', 'Category', 'Discount', 'Sales', 'Profit']].head(50), use_container_width=True)
