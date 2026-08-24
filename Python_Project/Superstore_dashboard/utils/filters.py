import streamlit as st


def render_search_bar(df, key="global_search"):
    """Renders a working search box that filters rows by matching the query
    against Product Name, Customer Name, Order ID, City, and State."""
    query = st.text_input(
        "🔍 Search products, customers, order ID, city or state",
        placeholder="e.g. 'chair', 'Claire Gute', 'CA-2024-100032', 'Seattle'...",
        key=key,
    )

    if not query:
        return df, query

    searchable_cols = [c for c in ["Product Name", "Customer Name", "Order ID", "City", "State"] if c in df.columns]
    if not searchable_cols:
        return df, query

    mask = False
    for col in searchable_cols:
        mask = mask | df[col].astype(str).str.contains(query, case=False, na=False)

    results = df[mask]
    st.caption(f"Found **{len(results):,}** matching record(s) for “{query}”.")
    return results, query


def render_sidebar_filters(df):
    st.sidebar.header("Global Filters")
    
    min_date = df["Order Date"].min().date()
    max_date = df["Order Date"].max().date()
    
    date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
    
    region = st.sidebar.multiselect("Region", options=df["Region"].unique(), default=df["Region"].unique())
    category = st.sidebar.multiselect("Category", options=df["Category"].unique(), default=df["Category"].unique())
    segment = st.sidebar.multiselect("Segment", options=df["Segment"].unique(), default=df["Segment"].unique())

    filtered_df = df.copy()
    if len(date_range) == 2:
        filtered_df = filtered_df[(filtered_df["Order Date"].dt.date >= date_range[0]) & 
                                  (filtered_df["Order Date"].dt.date <= date_range[1])]
    
    if region:
        filtered_df = filtered_df[filtered_df["Region"].isin(region)]
    if category:
        filtered_df = filtered_df[filtered_df["Category"].isin(category)]
    if segment:
        filtered_df = filtered_df[filtered_df["Segment"].isin(segment)]

    return filtered_df