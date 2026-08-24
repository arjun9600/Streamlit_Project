import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="City Performance", layout="wide")
apply_custom_theme()
require_login()

st.title("City Performance")
st.caption("Top and bottom performing cities.")

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

city_df = filtered.groupby('City').agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum')).reset_index()
top10 = city_df.sort_values('Profit', ascending=False).head(10)
bottom10 = city_df.sort_values('Profit', ascending=True).head(10)

col_a, col_b = st.columns(2)
with col_a:
    fig1 = px.bar(top10.sort_values('Profit'), x='Profit', y='City', orientation='h',
                   color='Profit', color_continuous_scale=PALETTE, title="Top 10 Cities by Profit")
    st.plotly_chart(style_fig(fig1), use_container_width=True)

with col_b:
    fig2 = px.bar(bottom10.sort_values('Profit', ascending=False), x='Profit', y='City', orientation='h',
                   color='Profit', color_continuous_scale=["#8d00c4", "#b53dff"], title="Bottom 10 Cities by Profit")
    st.plotly_chart(style_fig(fig2), use_container_width=True)

if not city_df.empty:
    best_city = top10.iloc[0]
    worst_city = bottom10.iloc[0]
    loss_cities = city_df[city_df['Profit'] < 0]
    points = [
        f"<b>{best_city['City']}</b> is the most profitable city (${best_city['Profit']:,.0f}) — a strong reference case for what's working.",
        f"<b>{worst_city['City']}</b> is the weakest, at ${worst_city['Profit']:,.0f} — {'currently a net loss' if worst_city['Profit'] < 0 else 'thin margin'} for the current filter.",
        f"<b>{len(loss_cities)}</b> cities are unprofitable overall — worth checking if it's a discounting issue or a shipping-cost issue for those metros.",
    ]
    insight_box("City-level performance spread", points)

st.subheader("Detailed Records")
st.dataframe(filtered[['Order ID', 'Order Date', 'City', 'Region', 'Category', 'Sales', 'Profit']].head(50), use_container_width=True)
