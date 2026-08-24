import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="Logistics & Shipping", layout="wide")
apply_custom_theme()
require_login()

st.title("Logistics & Shipping")
st.caption("Ship mode speed and transit delays.")

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

ship_speed = filtered.groupby('Ship Mode')['Shipping Days'].mean().reset_index()

col_a, col_b = st.columns(2)
with col_a:
    fig1 = px.bar(ship_speed.sort_values('Shipping Days'), x='Ship Mode', y='Shipping Days', color='Ship Mode',
                   title="Average Shipping Days by Mode", color_discrete_sequence=PALETTE)
    st.plotly_chart(style_fig(fig1), use_container_width=True)

with col_b:
    fig2 = px.histogram(filtered, x='Shipping Days', color='Ship Mode', barmode='overlay', nbins=15,
                         title="Shipping Days Distribution", color_discrete_sequence=PALETTE, opacity=0.75)
    st.plotly_chart(style_fig(fig2), use_container_width=True)

if not ship_speed.empty:
    fastest = ship_speed.sort_values('Shipping Days').iloc[0]
    slowest = ship_speed.sort_values('Shipping Days', ascending=False).iloc[0]
    points = [
        f"<b>{fastest['Ship Mode']}</b> is the fastest option, averaging <b>{fastest['Shipping Days']:.1f} days</b>.",
        f"<b>{slowest['Ship Mode']}</b> is the slowest at <b>{slowest['Shipping Days']:.1f} days</b> — if this is also a high-volume mode (see Order Intelligence), it's a customer-experience risk.",
        "A wide, overlapping spread in the histogram signals inconsistent delivery promises — worth tightening carrier SLAs for the slower modes.",
    ]
    insight_box("Delivery speed by shipping method", points)

st.subheader("Detailed Records")
st.dataframe(filtered[['Order ID', 'Order Date', 'Ship Mode', 'Shipping Days', 'Region', 'Sales']].head(50), use_container_width=True)
