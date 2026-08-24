import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="Time Series Forecasting", layout="wide")
apply_custom_theme()
require_login()

st.title("Time Series Forecasting")
st.caption("Historical trends and seasonality.")

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

monthly = filtered.resample('ME', on='Order Date')['Sales'].sum().reset_index()
filtered = filtered.copy()
filtered['Month Name'] = filtered['Order Date'].dt.strftime('%b')
filtered['Year'] = filtered['Order Date'].dt.year
seasonality = filtered.groupby(['Year', 'Month Name'])['Sales'].sum().reset_index()
month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

col_a, col_b = st.columns(2)
with col_a:
    fig1 = px.line(monthly, x='Order Date', y='Sales', markers=True, title="Monthly Sales Trend",
                    color_discrete_sequence=[PALETTE[0]])
    fig1.update_traces(line=dict(width=3), marker=dict(size=6, color=PALETTE[1]))
    st.plotly_chart(style_fig(fig1), use_container_width=True)

with col_b:
    fig2 = px.line(seasonality, x='Month Name', y='Sales', color='Year', category_orders={'Month Name': month_order},
                    title="Seasonality: Sales by Month Across Years", color_discrete_sequence=PALETTE, markers=True)
    st.plotly_chart(style_fig(fig2), use_container_width=True)

if len(monthly) > 1:
    best_month = monthly.loc[monthly['Sales'].idxmax()]
    seasonal_peak = seasonality.groupby('Month Name')['Sales'].mean().reindex(month_order).idxmax()
    points = [
        f"All-time peak was <b>{best_month['Order Date'].strftime('%B %Y')}</b> at ${best_month['Sales']:,.0f}.",
        f"<b>{seasonal_peak}</b> is consistently the strongest month across years — plan inventory and staffing ahead of it.",
        "Overlapping year lines that trend upward each year indicate healthy YoY growth — see the Growth Analysis page for the exact percentages.",
    ]
    insight_box("Seasonal patterns worth planning around", points)

st.subheader("Detailed Records")
st.dataframe(filtered[['Order ID', 'Order Date', 'Region', 'Category', 'Sub-Category', 'Sales', 'Profit']].head(50), use_container_width=True)
