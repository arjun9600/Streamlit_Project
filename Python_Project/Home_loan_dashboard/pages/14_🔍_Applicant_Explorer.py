import streamlit as st
import plotly.graph_objects as go

from utils.data_loader import load_data
from utils.theme import apply_theme, style_fig, page_header, PLOTLY_CONFIG, sidebar_brand, topbar, PRIMARY, DANGER, SAFE, GOLD
from utils.components import kpi_row, section_start, section_end, insight_box, risk_badge
from utils.filters import render_sidebar_filters
from utils.auth import require_login

st.set_page_config(page_title="Applicant Explorer", page_icon="🔍", layout="wide")
apply_theme()
require_login()
df = load_data()

sidebar_brand()
filtered = render_sidebar_filters(df, key_prefix="explore_")

topbar(filtered)

page_header("Applicant Explorer", "Search the portfolio, inspect an individual application, or export the filtered book.", "🔍")

tab1, tab2 = st.tabs(["👤 Single Applicant Lookup", "📋 Full Data Table"])

with tab1:
    ids = filtered["SK_ID_CURR"].tolist()
    if ids:
        chosen_id = st.selectbox("Applicant ID (SK_ID_CURR)", ids, index=0)
        rec = filtered[filtered["SK_ID_CURR"] == chosen_id].iloc[0]

        is_high_risk = rec["RISK_SCORE"] >= 60
        badge_html = risk_badge(is_high_risk, mid=(45 <= rec["RISK_SCORE"] < 60))

        st.markdown(f"### Applicant #{int(rec['SK_ID_CURR'])} &nbsp; {badge_html}", unsafe_allow_html=True)

        kpi_row([
            {"label": "Age", "value": f"{rec['AGE_YEARS']:.0f} yrs", "icon": "🎂"},
            {"label": "Gender", "value": f"{rec['GENDER_LABEL']}", "icon": "🧑"},
            {"label": "Income type", "value": f"{rec['NAME_INCOME_TYPE']}", "icon": "💼"},
            {"label": "Annual income", "value": f"${rec['AMT_INCOME_TOTAL']:,.0f}", "icon": "💵"},
            {"label": "Loan amount", "value": f"${rec['AMT_CREDIT']:,.0f}", "icon": "🏦"},
            {"label": "Actual outcome", "value": f"{rec['RISK_LABEL']}", "icon": "🎯"},
        ])

        c1, c2 = st.columns([1, 1.3])
        with c1:
            section_start("🌡️ In-House Risk Score")
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=float(rec["RISK_SCORE"]),
                number={"suffix": "/100", "font": {"color": "#0f172a"}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": PRIMARY},
                    "steps": [
                        {"range": [0, 45], "color": "rgba(52,211,153,0.25)"},
                        {"range": [45, 60], "color": "rgba(240,180,41,0.25)"},
                        {"range": [60, 100], "color": "rgba(251,91,108,0.25)"},
                    ],
                },
            ))
            fig.update_layout(height=280)
            st.plotly_chart(style_fig(fig), use_container_width=True, config=PLOTLY_CONFIG)
            section_end()

        with c2:
            section_start("🧾 Application Details")
            details = {
                "Loan type": rec["NAME_CONTRACT_TYPE"],
                "Education": rec["NAME_EDUCATION_TYPE"],
                "Family status": rec["NAME_FAMILY_STATUS"],
                "Housing": rec["NAME_HOUSING_TYPE"],
                "Occupation": rec["OCCUPATION_TYPE"],
                "Owns car": rec["OWN_CAR_LABEL"],
                "Owns property": rec["OWN_REALTY_LABEL"],
                "Children": int(rec["CNT_CHILDREN"]),
                "Household size": rec["CNT_FAM_MEMBERS"],
                "Credit / income ratio": f"{rec['CREDIT_INCOME_RATIO']:.2f}×",
                "Annuity": f"${rec['AMT_ANNUITY']:,.0f}",
                "Ext. bureau score (avg)": f"{rec['EXT_SOURCE_MEAN']:.3f}" if rec['EXT_SOURCE_MEAN'] == rec['EXT_SOURCE_MEAN'] else "N/A",
                "Documents submitted": f"{int(rec['DOCS_SUBMITTED'])}",
            }
            for k, v in details.items():
                st.markdown(f"**{k}:** {v}")
            section_end()
    else:
        st.warning("No applicants match the current filters.")

with tab2:
    section_start("📋 Filtered Applicant Table")
    display_cols = ["SK_ID_CURR", "RISK_LABEL", "RISK_SCORE", "GENDER_LABEL", "AGE_YEARS",
                     "NAME_CONTRACT_TYPE", "NAME_INCOME_TYPE", "AMT_INCOME_TOTAL", "AMT_CREDIT",
                     "AMT_ANNUITY", "NAME_EDUCATION_TYPE", "NAME_FAMILY_STATUS", "NAME_HOUSING_TYPE"]
    st.dataframe(filtered[display_cols].sort_values("RISK_SCORE", ascending=False),
                 use_container_width=True, hide_index=True, height=480)
    csv = filtered[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download filtered data as CSV", data=csv, file_name="filtered_applicants.csv", mime="text/csv")
    section_end()
