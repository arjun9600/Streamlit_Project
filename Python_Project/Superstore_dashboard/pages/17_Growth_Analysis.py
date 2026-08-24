import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="MoM & YoY Growth", layout="wide")
apply_custom_theme()
require_login()

st.title("MoM & YoY Growth")
st.caption("Percentage growth trajectories.")

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
monthly['MoM %'] = monthly['Sales'].pct_change() * 100

yearly = filtered.resample('YE', on='Order Date')['Sales'].sum().reset_index()
yearly['Year'] = yearly['Order Date'].dt.year
yearly['YoY %'] = yearly['Sales'].pct_change() * 100

col_a, col_b = st.columns(2)
with col_a:
    fig1 = px.bar(monthly.dropna(), x='Order Date', y='MoM %', color='MoM %',
                   color_continuous_scale=["#8d00c4", "#14e81e"], title="Month-over-Month Growth %")
    st.plotly_chart(style_fig(fig1), use_container_width=True)

with col_b:
    fig2 = px.line(yearly.dropna(), x='Year', y='YoY %', markers=True, title="Year-over-Year Growth %",
                    color_discrete_sequence=[PALETTE[2]])
    fig2.update_traces(line=dict(width=3), marker=dict(size=10, color=PALETTE[0]))
    st.plotly_chart(style_fig(fig2), use_container_width=True)

mom_clean = monthly.dropna()
yoy_clean = yearly.dropna()
if not mom_clean.empty:
    best_mom = mom_clean.loc[mom_clean['MoM %'].idxmax()]
    latest_mom = mom_clean.iloc[-1]
    points = [
        f"Best single-month growth was <b>{best_mom['Order Date'].strftime('%B %Y')}</b> at <b>{best_mom['MoM %']:.1f}%</b> MoM.",
        f"Most recent month grew <b>{latest_mom['MoM %']:.1f}%</b> MoM — {'accelerating' if latest_mom['MoM %'] > 0 else 'a dip worth investigating'}.",
    ]
    if not yoy_clean.empty:
        latest_yoy = yoy_clean.iloc[-1]
        points.append(f"Latest full year grew <b>{latest_yoy['YoY %']:.1f}%</b> YoY ({int(latest_yoy['Year'])}).")
    insight_box("Growth momentum, short- and long-term", points)

st.subheader("Detailed Records")
st.dataframe(filtered[['Order ID', 'Order Date', 'Region', 'Category', 'Sales', 'Profit']].head(50), use_container_width=True)
