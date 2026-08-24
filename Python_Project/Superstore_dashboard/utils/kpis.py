import streamlit as st

def display_top_kpis(df):
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    total_orders = df["Order ID"].nunique()
    total_quantity = df["Quantity"].sum()
    margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

    col1.metric("Total Sales", f"${total_sales:,.2f}")
    col2.metric("Total Profit", f"${total_profit:,.2f}")
    col3.metric("Total Orders", f"{total_orders:,}")
    col4.metric("Quantity Sold", f"{total_quantity:,}")
    col5.metric("Profit Margin", f"{margin:.2f}%")