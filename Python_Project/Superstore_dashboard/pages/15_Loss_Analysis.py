import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="Loss Prevention", layout="wide")
apply_custom_theme()
require_login()

st.title("Loss Prevention")
st.caption("Identifying negative margin transactions.")

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

loss_df = filtered[filtered['Profit'] < 0]
loss_by_subcat = loss_df.groupby('Sub-Category')['Profit'].sum().reset_index().sort_values('Profit')

col_a, col_b = st.columns(2)
with col_a:
    fig1 = px.bar(loss_by_subcat, x='Profit', y='Sub-Category', orientation='h', color='Profit',
                   color_continuous_scale=["#14e81e", "#8d00c4"], title="Total Loss by Sub-Category")
    st.plotly_chart(style_fig(fig1, height=460), use_container_width=True)

with col_b:
    fig2 = px.histogram(loss_df, x='Discount', nbins=20, title="Discount Level on Loss-Making Orders",
                         color_discrete_sequence=[PALETTE[3]])
    fig2.update_xaxes(tickformat=".0%")
    st.plotly_chart(style_fig(fig2), use_container_width=True)

total_loss = loss_df['Profit'].sum()
loss_order_count = loss_df['Order ID'].nunique()
if not loss_df.empty:
    worst_subcat = loss_by_subcat.iloc[0]
    avg_loss_discount = loss_df['Discount'].mean()
    points = [
        f"<b>{loss_order_count:,}</b> orders are currently unprofitable, totaling <b>${abs(total_loss):,.0f}</b> in lost profit.",
        f"<b>{worst_subcat['Sub-Category']}</b> accounts for the single biggest chunk of losses (${abs(worst_subcat['Profit']):,.0f}).",
        f"Loss-making orders carry an average discount of <b>{avg_loss_discount*100:.0f}%</b> — capping discounts on this sub-category is the fastest lever to stop the bleeding.",
    ]
else:
    points = ["No loss-making orders in the current filter — every transaction is profitable. 🎉"]
insight_box("Where money is actively being lost", points)

st.subheader("Detailed Records")
st.dataframe(loss_df[['Order ID', 'Order Date', 'Category', 'Sub-Category', 'Discount', 'Sales', 'Profit']].head(50), use_container_width=True)
