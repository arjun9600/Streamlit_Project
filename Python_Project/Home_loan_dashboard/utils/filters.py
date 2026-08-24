"""Shared sidebar filter controls used across every page."""
import streamlit as st
from utils.theme import sidebar_profile


def render_sidebar_filters(df, key_prefix=""):
    st.sidebar.markdown("### 🎛️ Portfolio Filters")

    gender = st.sidebar.multiselect(
        "Gender", options=sorted(df["GENDER_LABEL"].dropna().unique()),
        default=sorted(df["GENDER_LABEL"].dropna().unique()), key=f"{key_prefix}gender"
    )
    contract = st.sidebar.multiselect(
        "Loan type", options=df["NAME_CONTRACT_TYPE"].unique(),
        default=df["NAME_CONTRACT_TYPE"].unique(), key=f"{key_prefix}contract"
    )
    income_type = st.sidebar.multiselect(
        "Income type", options=df["NAME_INCOME_TYPE"].unique(),
        default=df["NAME_INCOME_TYPE"].unique(), key=f"{key_prefix}income_type"
    )
    education = st.sidebar.multiselect(
        "Education", options=df["NAME_EDUCATION_TYPE"].unique(),
        default=df["NAME_EDUCATION_TYPE"].unique(), key=f"{key_prefix}education"
    )
    age_min, age_max = float(df["AGE_YEARS"].min()), float(df["AGE_YEARS"].max())
    age_range = st.sidebar.slider(
        "Age range", min_value=float(round(age_min)), max_value=float(round(age_max)),
        value=(float(round(age_min)), float(round(age_max))), key=f"{key_prefix}age"
    )
    risk_filter = st.sidebar.radio(
        "Repayment status", options=["All applicants", "Repaid on time", "Payment difficulty"],
        index=0, key=f"{key_prefix}risk"
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(f"📊 {len(df):,} total applicants loaded")

    filtered = df.copy()
    if gender:
        filtered = filtered[filtered["GENDER_LABEL"].isin(gender)]
    if contract:
        filtered = filtered[filtered["NAME_CONTRACT_TYPE"].isin(contract)]
    if income_type:
        filtered = filtered[filtered["NAME_INCOME_TYPE"].isin(income_type)]
    if education:
        filtered = filtered[filtered["NAME_EDUCATION_TYPE"].isin(education)]
    filtered = filtered[(filtered["AGE_YEARS"] >= age_range[0]) & (filtered["AGE_YEARS"] <= age_range[1])]
    if risk_filter != "All applicants":
        filtered = filtered[filtered["RISK_LABEL"] == risk_filter]

    st.sidebar.caption(f"✅ {len(filtered):,} match current filters")
    sidebar_profile()
    return filtered
