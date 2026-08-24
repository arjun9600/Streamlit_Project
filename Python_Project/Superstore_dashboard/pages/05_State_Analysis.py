import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, apply_custom_theme
from utils.auth import require_login, render_logout
from utils.charts import CONTINUOUS, PALETTE, style_fig, insight_box

st.set_page_config(page_title="State Deep-Dive", layout="wide")
apply_custom_theme()
require_login()

st.title("State Deep-Dive")
st.caption("State-level sales maps and tables.")

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

state_df = filtered.groupby('State').agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum')).reset_index()

col_a, col_b = st.columns(2)
with col_a:
    fig1 = px.choropleth(state_df, locations='State', locationmode='USA-states', color='Sales',
                          scope='usa', color_continuous_scale=CONTINUOUS, title="Sales Heatmap by State")
    st.plotly_chart(style_fig(fig1, height=460), use_container_width=True)

with col_b:
    top10 = state_df.sort_values('Sales', ascending=False).head(10)
    fig2 = px.bar(top10.sort_values('Sales'), x='Sales', y='State', orientation='h', color='Sales',
                   color_continuous_scale=PALETTE, title="Top 10 States by Sales")
    st.plotly_chart(style_fig(fig2, height=460), use_container_width=True)

if not state_df.empty:
    top_state = state_df.sort_values('Sales', ascending=False).iloc[0]
    weakest_states = state_df[state_df['Profit'] < 0]
    points = [
        f"<b>{top_state['State']}</b> is the single biggest state by revenue (${top_state['Sales']:,.0f}).",
    ]
    if not weakest_states.empty:
        loss_total = weakest_states['Profit'].sum()
        points.append(f"<b>{len(weakest_states)}</b> state(s) are currently unprofitable, together losing ${abs(loss_total):,.0f} — see the Loss Analysis page for detail.")
    else:
        points.append("Every state in the current filter is profitable — a healthy geographic footprint.")
    points.append("Use the map to spot under-penetrated states relative to population/region — those are expansion candidates.")
    insight_box("Geographic concentration of revenue", points)

st.subheader("Detailed Records")
st.dataframe(filtered[['Order ID', 'Order Date', 'Region', 'State', 'Category', 'Sales', 'Profit']].head(50), use_container_width=True)
