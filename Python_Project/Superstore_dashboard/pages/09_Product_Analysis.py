import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="Product Matrix", layout="wide")
apply_custom_theme()
require_login()

st.title("Product Matrix")
st.caption("Individual SKU performance.")

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

prod_df = filtered.groupby('Product Name').agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum')).reset_index()
top10 = prod_df.sort_values('Sales', ascending=False).head(10)
tree_df = filtered.groupby(['Category', 'Sub-Category'])['Sales'].sum().reset_index()

col_a, col_b = st.columns(2)
with col_a:
    fig1 = px.bar(top10.sort_values('Sales'), x='Sales', y='Product Name', orientation='h',
                   color='Sales', color_continuous_scale=PALETTE, title="Top 10 Products by Sales")
    st.plotly_chart(style_fig(fig1, height=460), use_container_width=True)

with col_b:
    fig2 = px.treemap(tree_df, path=['Category', 'Sub-Category'], values='Sales',
                       color='Sales', color_continuous_scale=PALETTE, title="Product Mix Treemap")
    st.plotly_chart(style_fig(fig2, height=460), use_container_width=True)

if not prod_df.empty:
    best_product = top10.iloc[0]
    unprofitable = prod_df[prod_df['Profit'] < 0]
    points = [
        f"<b>{best_product['Product Name']}</b> is the top-selling SKU (${best_product['Sales']:,.0f}) in the current filter.",
        f"<b>{len(unprofitable)}</b> of {len(prod_df)} products are selling at a loss — the treemap shows which Category/Sub-Category they cluster in.",
        "Use the treemap to spot categories that look big in sales but are made up of many small, thin-margin SKUs — those are candidates for a catalog cleanup.",
    ]
    insight_box("SKU-level concentration and risk", points)

st.subheader("Detailed Records")
st.dataframe(filtered[['Order ID', 'Order Date', 'Region', 'Category', 'Sub-Category', 'Sales', 'Profit']].head(50), use_container_width=True)
