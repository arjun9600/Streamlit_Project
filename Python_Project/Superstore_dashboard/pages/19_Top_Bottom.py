import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="Rankings Engine", layout="wide")
apply_custom_theme()
require_login()

st.title("Rankings Engine")
st.caption("Top and bottom 10 performers filter.")

df = load_data()

st.sidebar.header("Filter Options")
render_logout()
reg = st.sidebar.multiselect("Select Region", df['Region'].unique(), default=df['Region'].unique())
cat = st.sidebar.multiselect("Select Category", df['Category'].unique(), default=df['Category'].unique())
rank_by = st.sidebar.radio("Rank products by", ["Sales", "Profit"], horizontal=True)

filtered = df[(df['Region'].isin(reg)) & (df['Category'].isin(cat))]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Selected Sales", f"${filtered['Sales'].sum():,.2f}")
k2.metric("Selected Profit", f"${filtered['Profit'].sum():,.2f}")
k3.metric("Volume Sold", f"{filtered['Quantity'].sum():,}")
k4.metric("Avg Discount", f"{filtered['Discount'].mean()*100:.1f}%")

st.markdown("---")

prod_df = filtered.groupby('Product Name')[rank_by].sum().reset_index()
top10 = prod_df.sort_values(rank_by, ascending=False).head(10)
bottom10 = prod_df.sort_values(rank_by, ascending=True).head(10)

col_a, col_b = st.columns(2)
with col_a:
    fig1 = px.bar(top10.sort_values(rank_by), x=rank_by, y='Product Name', orientation='h',
                   color=rank_by, color_continuous_scale=PALETTE, title=f"Top 10 Products by {rank_by}")
    st.plotly_chart(style_fig(fig1), use_container_width=True)

with col_b:
    fig2 = px.bar(bottom10.sort_values(rank_by, ascending=False), x=rank_by, y='Product Name', orientation='h',
                   color=rank_by, color_continuous_scale=["#8d00c4", "#b53dff"], title=f"Bottom 10 Products by {rank_by}")
    st.plotly_chart(style_fig(fig2), use_container_width=True)

if not prod_df.empty:
    gap = top10.iloc[0][rank_by] - bottom10.iloc[0][rank_by]
    points = [
        f"<b>{top10.iloc[0]['Product Name']}</b> leads all products on {rank_by.lower()}.",
        f"The gap between the #1 and #10 product spans <b>{gap:,.0f}</b> in {rank_by.lower()} — a highly concentrated, long-tail product mix.",
        f"Bottom performers on {rank_by.lower()} are good candidates to discontinue or bundle, freeing up catalog and marketing focus for the top 10.",
    ]
    insight_box(f"Extremes of the product portfolio, ranked by {rank_by}", points)

st.subheader("Detailed Records")
st.dataframe(filtered[['Order ID', 'Order Date', 'Product Name', 'Category', 'Sales', 'Profit']].head(50), use_container_width=True)
