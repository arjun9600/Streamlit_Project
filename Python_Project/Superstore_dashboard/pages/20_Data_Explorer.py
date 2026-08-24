import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.filters import render_search_bar
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="Interactive Data Grid", layout="wide")
apply_custom_theme()
require_login()

st.title("Interactive Data Grid")
st.caption("Raw dataset filter and CSV exporter.")

df = load_data()

st.sidebar.header("Filter Options")
render_logout()
reg = st.sidebar.multiselect("Select Region", df['Region'].unique(), default=df['Region'].unique())
cat = st.sidebar.multiselect("Select Category", df['Category'].unique(), default=df['Category'].unique())

filtered = df[(df['Region'].isin(reg)) & (df['Category'].isin(cat))]

# Working global search
filtered, _search_query = render_search_bar(filtered, key="explorer_search")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Selected Sales", f"${filtered['Sales'].sum():,.2f}")
k2.metric("Selected Profit", f"${filtered['Profit'].sum():,.2f}")
k3.metric("Volume Sold", f"{filtered['Quantity'].sum():,}")
k4.metric("Avg Discount", f"{filtered['Discount'].mean()*100:.1f}%")

st.markdown("---")

col_a, col_b = st.columns(2)
with col_a:
    completeness = filtered.notna().mean().reset_index()
    completeness.columns = ['Column', 'Completeness']
    fig1 = px.bar(completeness, x='Completeness', y='Column', orientation='h', color='Completeness',
                   color_continuous_scale=PALETTE, title="Data Completeness by Column")
    fig1.update_xaxes(tickformat=".0%")
    st.plotly_chart(style_fig(fig1, height=460), use_container_width=True)

with col_b:
    order_counts = filtered.groupby('Order Priority')['Order ID'].nunique().reset_index(name='Orders') if 'Order Priority' in filtered.columns else None
    if order_counts is not None and not order_counts.empty:
        fig2 = px.pie(order_counts, names='Order Priority', values='Orders', hole=0.55,
                       title="Orders by Priority", color_discrete_sequence=PALETTE)
    else:
        cat_counts = filtered['Category'].value_counts().reset_index()
        cat_counts.columns = ['Category', 'Rows']
        fig2 = px.pie(cat_counts, names='Category', values='Rows', hole=0.55,
                       title="Rows by Category", color_discrete_sequence=PALETTE)
    st.plotly_chart(style_fig(fig2, height=460), use_container_width=True)

points = [
    f"The current filter/search returns <b>{len(filtered):,}</b> rows out of {len(df):,} total records.",
    f"Data quality looks {'clean — no missing values' if filtered.notna().all().all() else 'incomplete in at least one column — check the completeness chart before trusting downstream KPIs'}.",
    "Use the search bar above to spot-check a specific customer, order ID, or product before exporting.",
]
insight_box("Dataset health at a glance", points)

st.subheader("Full Filtered Table")
st.dataframe(filtered, use_container_width=True)
st.download_button("⬇️ Download filtered data as CSV", filtered.to_csv(index=False), file_name="superstore_filtered.csv", mime="text/csv")
