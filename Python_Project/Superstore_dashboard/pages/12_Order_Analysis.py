import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="Order Intelligence", layout="wide")
apply_custom_theme()
require_login()

st.title("Order Intelligence")
st.caption("Volume distributions and basket sizes.")

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

basket_df = filtered.groupby('Order ID')['Sales'].sum().reset_index()
ship_df = filtered.groupby('Ship Mode')['Order ID'].nunique().reset_index(name='Orders')

col_a, col_b = st.columns(2)
with col_a:
    fig1 = px.histogram(basket_df, x='Sales', nbins=40, title="Order Value Distribution",
                         color_discrete_sequence=[PALETTE[0]])
    st.plotly_chart(style_fig(fig1), use_container_width=True)

with col_b:
    fig2 = px.bar(ship_df.sort_values('Orders', ascending=False), x='Ship Mode', y='Orders', color='Ship Mode',
                   title="Orders by Ship Mode", color_discrete_sequence=PALETTE)
    st.plotly_chart(style_fig(fig2), use_container_width=True)

if not basket_df.empty:
    avg_order = basket_df['Sales'].mean()
    median_order = basket_df['Sales'].median()
    top_ship = ship_df.sort_values('Orders', ascending=False).iloc[0]
    points = [
        f"Average order value is <b>${avg_order:,.2f}</b>, median is ${median_order:,.2f} — a wide gap usually means a small number of very large orders are pulling the average up.",
        f"<b>{top_ship['Ship Mode']}</b> is the most-used shipping method ({top_ship['Orders']:,} orders) — worth checking it isn't the costliest one too (see Shipping Analysis).",
        "Low-value orders on the far left of the histogram are the most expensive to fulfill relative to revenue — consider a minimum order threshold for free shipping.",
    ]
    insight_box("How order size and fulfillment method break down", points)

st.subheader("Detailed Records")
st.dataframe(filtered[['Order ID', 'Order Date', 'Ship Mode', 'Region', 'Category', 'Sales', 'Profit']].head(50), use_container_width=True)
