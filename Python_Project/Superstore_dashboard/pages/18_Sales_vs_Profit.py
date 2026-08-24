import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="Scatter Matrix Analysis", layout="wide")
apply_custom_theme()
require_login()

st.title("Scatter Matrix Analysis")
st.caption("Sales vs Profit correlation graphs.")

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
with col_a:
    fig1 = px.scatter(filtered, x='Sales', y='Profit', color='Category', size='Quantity',
                       hover_data=['Product Name'], title="Sales vs Profit (bubble = quantity)",
                       color_discrete_sequence=PALETTE)
    st.plotly_chart(style_fig(fig1), use_container_width=True)

with col_b:
    corr_by_cat = filtered.groupby('Category').apply(lambda g: g['Sales'].corr(g['Profit'])).reset_index(name='Correlation')
    fig2 = px.bar(corr_by_cat.sort_values('Correlation'), x='Correlation', y='Category', orientation='h',
                   color='Correlation', color_continuous_scale=["#8d00c4", "#14e81e"],
                   title="Sales-Profit Correlation by Category")
    st.plotly_chart(style_fig(fig2), use_container_width=True)

if not filtered.empty:
    overall_corr = filtered['Sales'].corr(filtered['Profit'])
    strongest = corr_by_cat.sort_values('Correlation', ascending=False).iloc[0]
    weakest = corr_by_cat.sort_values('Correlation', ascending=True).iloc[0]
    points = [
        f"Overall, Sales and Profit correlate at <b>{overall_corr:.2f}</b> — {'higher sales reliably mean higher profit' if overall_corr > 0.5 else 'sales volume alone is not a strong predictor of profit'}.",
        f"<b>{strongest['Category']}</b> shows the tightest sales-to-profit relationship ({strongest['Correlation']:.2f}) — pricing here is well calibrated.",
        f"<b>{weakest['Category']}</b> shows the weakest link ({weakest['Correlation']:.2f}) — big sales don't reliably translate to profit, likely due to discounting or cost variance.",
    ]
    insight_box("Does more revenue actually mean more profit?", points)

st.subheader("Detailed Records")
st.dataframe(filtered[['Order ID', 'Order Date', 'Category', 'Quantity', 'Sales', 'Profit']].head(50), use_container_width=True)
