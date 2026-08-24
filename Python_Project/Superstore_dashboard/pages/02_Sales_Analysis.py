import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="Sales Analysis", layout="wide")
apply_custom_theme()
require_login()

st.title("Sales Analysis")
st.caption("Sales trends and channel distributions.")

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
monthly = filtered.resample('ME', on='Order Date')['Sales'].sum().reset_index()
with col_a:
    fig1 = px.line(monthly, x='Order Date', y='Sales', markers=True, title="Monthly Sales Trend",
                    color_discrete_sequence=[PALETTE[0]])
    fig1.update_traces(line=dict(width=3), marker=dict(size=6, color=PALETTE[1]))
    st.plotly_chart(style_fig(fig1), use_container_width=True)

with col_b:
    seg_df = filtered.groupby('Segment')['Sales'].sum().reset_index().sort_values('Sales', ascending=False)
    fig2 = px.bar(seg_df, x='Segment', y='Sales', color='Segment', title="Sales by Customer Segment",
                   color_discrete_sequence=PALETTE)
    st.plotly_chart(style_fig(fig2), use_container_width=True)

if not filtered.empty and len(monthly) > 1:
    best_month = monthly.loc[monthly['Sales'].idxmax()]
    last_two = monthly.tail(2)
    mom_change = None
    if len(last_two) == 2 and last_two.iloc[0]['Sales'] != 0:
        mom_change = (last_two.iloc[1]['Sales'] - last_two.iloc[0]['Sales']) / last_two.iloc[0]['Sales'] * 100
    top_seg = seg_df.iloc[0]
    points = [
        f"Best-performing month is <b>{best_month['Order Date'].strftime('%B %Y')}</b> at ${best_month['Sales']:,.0f} — check what campaign or seasonal pattern drove it.",
        f"<b>{top_seg['Segment']}</b> is the largest sales channel (${top_seg['Sales']:,.0f}) — prioritize inventory and support here first.",
    ]
    if mom_change is not None:
        direction = "up" if mom_change >= 0 else "down"
        points.append(f"Sales are trending <b>{direction} {abs(mom_change):.1f}%</b> month-over-month in the latest period — {'keep the momentum going' if mom_change >= 0 else 'worth a quick root-cause check'}.")
    insight_box("Sales trend and channel mix", points)

st.subheader("Detailed Records")
st.dataframe(filtered[['Order ID', 'Order Date', 'Region', 'Category', 'Sub-Category', 'Sales', 'Profit']].head(50), use_container_width=True)
