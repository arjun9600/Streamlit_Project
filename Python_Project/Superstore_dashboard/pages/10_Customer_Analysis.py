import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="Customer Lifetime Value", layout="wide")
apply_custom_theme()
require_login()

st.title("Customer Lifetime Value")
st.caption("Customer order frequency and value.")

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

cust_df = filtered.groupby('Customer Name').agg(
    Sales=('Sales', 'sum'), Orders=('Order ID', 'nunique')
).reset_index()
top10 = cust_df.sort_values('Sales', ascending=False).head(10)

col_a, col_b = st.columns(2)
with col_a:
    fig1 = px.bar(top10.sort_values('Sales'), x='Sales', y='Customer Name', orientation='h',
                   color='Sales', color_continuous_scale=PALETTE, title="Top 10 Customers by Lifetime Sales")
    st.plotly_chart(style_fig(fig1), use_container_width=True)

with col_b:
    fig2 = px.scatter(cust_df, x='Orders', y='Sales', size='Sales', color='Sales',
                       color_continuous_scale=PALETTE, title="Order Frequency vs Customer Value")
    st.plotly_chart(style_fig(fig2), use_container_width=True)

if not cust_df.empty:
    top_customer = top10.iloc[0]
    avg_orders = cust_df['Orders'].mean()
    one_time = (cust_df['Orders'] == 1).sum()
    points = [
        f"<b>{top_customer['Customer Name']}</b> is the highest-value customer at ${top_customer['Sales']:,.0f} lifetime sales.",
        f"Customers place an average of <b>{avg_orders:.1f}</b> orders — the scatter plot shows whether high value comes from big single orders or repeat purchases.",
        f"<b>{one_time}</b> customers have only ordered once — a re-engagement campaign here could unlock incremental revenue.",
    ]
    insight_box("Who your best customers are and how they buy", points)

st.subheader("Detailed Records")
st.dataframe(filtered[['Order ID', 'Order Date', 'Customer Name', 'Region', 'Category', 'Sales', 'Profit']].head(50), use_container_width=True)
