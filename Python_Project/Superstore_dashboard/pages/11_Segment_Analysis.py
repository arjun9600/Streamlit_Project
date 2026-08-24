import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="Customer Segments", layout="wide")
apply_custom_theme()
require_login()

st.title("Customer Segments")
st.caption("Consumer vs Corporate vs Home Office.")

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

seg_df = filtered.groupby('Segment').agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum')).reset_index()
seg_df['Margin %'] = (seg_df['Profit'] / seg_df['Sales'] * 100).round(1)

col_a, col_b = st.columns(2)
with col_a:
    fig1 = px.bar(seg_df, x='Segment', y=['Sales', 'Profit'], barmode='group',
                   title="Sales & Profit by Segment", color_discrete_sequence=[PALETTE[2], PALETTE[0]])
    st.plotly_chart(style_fig(fig1), use_container_width=True)

with col_b:
    fig2 = px.pie(seg_df, names='Segment', values='Profit', hole=0.55, title="Profit Contribution by Segment",
                   color_discrete_sequence=PALETTE)
    st.plotly_chart(style_fig(fig2), use_container_width=True)

if not seg_df.empty:
    top_seg = seg_df.sort_values('Profit', ascending=False).iloc[0]
    best_margin_seg = seg_df.sort_values('Margin %', ascending=False).iloc[0]
    points = [
        f"<b>{top_seg['Segment']}</b> contributes the most profit (${top_seg['Profit']:,.0f}).",
        f"<b>{best_margin_seg['Segment']}</b> is the most efficient segment at <b>{best_margin_seg['Margin %']:.1f}%</b> margin — a good target for growth investment.",
        "If one segment shows high sales but low profit share on the pie chart, its discounting or cost-to-serve is likely too high.",
    ]
    insight_box("Which customer segment to double down on", points)

st.subheader("Detailed Records")
st.dataframe(filtered[['Order ID', 'Order Date', 'Segment', 'Region', 'Category', 'Sales', 'Profit']].head(50), use_container_width=True)
