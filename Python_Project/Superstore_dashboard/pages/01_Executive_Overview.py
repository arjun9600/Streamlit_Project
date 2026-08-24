import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="Executive Overview", layout="wide")
apply_custom_theme()
require_login()

st.title("Executive Overview")
st.caption("High-level performance summary.")

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
region_df = filtered.groupby('Region')[['Sales', 'Profit']].sum().reset_index().sort_values('Sales', ascending=False)
with col_a:
    fig1 = px.bar(region_df, x='Region', y=['Sales', 'Profit'], barmode='group',
                   title="Sales & Profit by Region", color_discrete_sequence=[PALETTE[2], PALETTE[0]])
    st.plotly_chart(style_fig(fig1), use_container_width=True)

with col_b:
    cat_share = filtered.groupby('Category')['Sales'].sum().reset_index()
    fig2 = px.pie(cat_share, names='Category', values='Sales', hole=0.55,
                   title="Revenue Share by Category", color_discrete_sequence=PALETTE)
    st.plotly_chart(style_fig(fig2), use_container_width=True)

if not filtered.empty and filtered['Sales'].sum() > 0:
    top_region = region_df.iloc[0]
    overall_margin = filtered['Profit'].sum() / filtered['Sales'].sum() * 100
    top_cat_row = cat_share.sort_values('Sales', ascending=False).iloc[0]
    cat_share_pct = top_cat_row['Sales'] / filtered['Sales'].sum() * 100
    points = [
        f"<b>{top_region['Region']}</b> leads all regions with ${top_region['Sales']:,.0f} in sales and ${top_region['Profit']:,.0f} in profit — the strongest territory to protect and replicate.",
        f"<b>{top_cat_row['Category']}</b> accounts for <b>{cat_share_pct:.1f}%</b> of revenue in the current filter, showing how concentrated the product mix is.",
        f"Blended profit margin is <b>{overall_margin:.1f}%</b> — use this as the baseline when comparing individual regions or categories on other pages.",
    ]
    insight_box("Where the business stands right now", points)

st.subheader("Detailed Records")
st.dataframe(filtered[['Order ID', 'Order Date', 'Region', 'Category', 'Sub-Category', 'Sales', 'Profit']].head(50), use_container_width=True)
