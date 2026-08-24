import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import PALETTE, style_fig, insight_box

st.set_page_config(page_title="Sub-Category Analysis", layout="wide")
apply_custom_theme()
require_login()
render_logout()
st.title("📑 Sub-Category Deep-Dive")
df = load_data()

sub_df = df.groupby('Sub-Category')[['Sales', 'Profit']].sum().reset_index()

c1, c2 = st.columns(2)
with c1:
    fig1 = px.bar(
        sub_df.sort_values('Sales'),
        x='Sales',
        y='Sub-Category',
        orientation='h',
        color='Sales',
        title="Sub-Category Sales Volume",
        color_continuous_scale=PALETTE,
    )
    st.plotly_chart(style_fig(fig1, height=520), use_container_width=True)

with c2:
    fig2 = px.line_polar(
        sub_df,
        r='Profit',
        theta='Sub-Category',
        line_close=True,
        title="Sub-Category Profit Radar",
    )
    fig2.update_traces(line_color=PALETTE[0], fillcolor="rgba(20,232,30,0.20)", fill='toself')
    st.plotly_chart(style_fig(fig2, height=520), use_container_width=True)

if not sub_df.empty:
    top_sub = sub_df.sort_values('Sales', ascending=False).iloc[0]
    top_profit_sub = sub_df.sort_values('Profit', ascending=False).iloc[0]
    loss_subs = sub_df[sub_df['Profit'] < 0]
    points = [
        f"<b>{top_sub['Sub-Category']}</b> is the highest-volume sub-category by sales (${top_sub['Sales']:,.0f}).",
        f"<b>{top_profit_sub['Sub-Category']}</b> generates the most profit (${top_profit_sub['Profit']:,.0f}) — notice on the radar whether high sales and high profit line up on the same sub-category or not.",
    ]
    if not loss_subs.empty:
        names = ", ".join(loss_subs.sort_values('Profit').head(3)['Sub-Category'])
        points.append(f"These sub-categories are currently losing money: <b>{names}</b> — prime targets for a pricing or discount-cap review.")
    insight_box("Sales volume vs profit contribution by sub-category", points)

st.subheader("Detailed Records")
st.dataframe(df[['Order ID', 'Order Date', 'Region', 'Category', 'Sub-Category', 'Sales', 'Profit']].head(50), use_container_width=True)
