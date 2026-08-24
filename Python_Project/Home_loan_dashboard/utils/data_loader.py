"""
Data loading & feature engineering for the Home Loan Risk Intelligence dashboard.
Source: Home Credit Default Risk application data (anonymized loan applicants).
"""
import os
import numpy as np
import pandas as pd
import streamlit as st

DATA_FILENAME = "home_loan.csv"


@st.cache_data(show_spinner="Loading applicant portfolio...")
def load_data() -> pd.DataFrame:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    file_path = os.path.join(project_root, "data", DATA_FILENAME)

    df = pd.read_csv(file_path, encoding="utf-8")

    # ---- Anomaly cleanup -------------------------------------------------
    # DAYS_EMPLOYED has a known sentinel value (365243) used for pensioners /
    # unemployed applicants -> treat as "not currently employed".
    df["DAYS_EMPLOYED"] = df["DAYS_EMPLOYED"].replace(365243, np.nan)

    # ---- Derived / human-readable features --------------------------------
    df["AGE_YEARS"] = (-df["DAYS_BIRTH"] / 365.25).round(1)
    df["EMPLOYED_YEARS"] = (-df["DAYS_EMPLOYED"] / 365.25).round(1)
    df["EMPLOYED_YEARS"] = df["EMPLOYED_YEARS"].clip(lower=0)

    df["AGE_GROUP"] = pd.cut(
        df["AGE_YEARS"],
        bins=[18, 25, 35, 45, 55, 65, 100],
        labels=["18-25", "26-35", "36-45", "46-55", "56-65", "65+"],
    )

    df["CREDIT_INCOME_RATIO"] = (df["AMT_CREDIT"] / df["AMT_INCOME_TOTAL"]).round(2)
    df["ANNUITY_INCOME_RATIO"] = (df["AMT_ANNUITY"] / df["AMT_INCOME_TOTAL"]).round(3)
    df["CREDIT_TERM_YEARS"] = (df["AMT_CREDIT"] / df["AMT_ANNUITY"]).round(1)
    df["GOODS_CREDIT_RATIO"] = (df["AMT_GOODS_PRICE"] / df["AMT_CREDIT"]).round(2)

    df["RISK_LABEL"] = df["TARGET"].map({0: "Repaid on time", 1: "Payment difficulty"})
    df["GENDER_LABEL"] = df["CODE_GENDER"].map({"M": "Male", "F": "Female", "XNA": "Other"})
    df["OWN_CAR_LABEL"] = df["FLAG_OWN_CAR"].map({"Y": "Owns car", "N": "No car"})
    df["OWN_REALTY_LABEL"] = df["FLAG_OWN_REALTY"].map({"Y": "Owns property", "N": "No property"})

    # Composite external credit-bureau score (average of the 3 normalized sources)
    df["EXT_SOURCE_MEAN"] = df[["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]].mean(axis=1)

    # Simple 0-100 in-house risk score for illustration (lower external score /
    # higher leverage -> higher risk). Purely descriptive, not a real model.
    norm_credit_ratio = (df["CREDIT_INCOME_RATIO"].clip(0, 15) / 15)
    ext_component = 1 - df["EXT_SOURCE_MEAN"].fillna(df["EXT_SOURCE_MEAN"].mean())
    df["RISK_SCORE"] = ((0.65 * ext_component + 0.35 * norm_credit_ratio) * 100).round(1)

    df["INCOME_BAND"] = pd.qcut(
        df["AMT_INCOME_TOTAL"], q=5,
        labels=["Q1 (Lowest)", "Q2", "Q3", "Q4", "Q5 (Highest)"], duplicates="drop"
    )

    doc_cols = [c for c in df.columns if c.startswith("FLAG_DOCUMENT_")]
    df["DOCS_SUBMITTED"] = df[doc_cols].sum(axis=1)

    df["APP_HOUR"] = df["HOUR_APPR_PROCESS_START"]

    return df.copy()  # defragment after many column insertions


def kpi_number(value, prefix="", suffix="", decimals=0):
    if pd.isna(value):
        return "N/A"
    fmt = f"{{:,.{decimals}f}}"
    return f"{prefix}{fmt.format(value)}{suffix}"
