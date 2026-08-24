# 🏦 Home Loan Risk Intelligence Dashboard

A custom-built Streamlit analytics suite for the **Home Credit Default Risk** loan
application dataset (10,000 applicants × 122 raw fields). Built with a distinct
"Vault" fintech visual identity — deep-navy gradients, glass KPI cards, gauge
charts and risk badges — rather than a default/boilerplate Streamlit layout.

## Project structure

```
home_loan_dashboard/
├── app.py                              # Home page — Portfolio Command Center
├── requirements.txt
├── .streamlit/
│   └── config.toml                     # Dark fintech theme colors
├── data/
│   └── home_loan.csv                   # Source dataset
├── utils/
│   ├── data_loader.py                  # Cached load + feature engineering
│   ├── theme.py                        # Custom CSS, Plotly styling, colors
│   ├── components.py                   # KPI cards / section cards / badges
│   └── filters.py                      # Shared sidebar filters
└── pages/
    ├── 01_🎯_Risk_Overview.py
    ├── 02_🧑_Demographics.py
    ├── 03_💵_Income_Analysis.py
    ├── 04_🏦_Loan_Portfolio.py
    ├── 05_⚠️_Default_Risk_Drivers.py
    ├── 06_🏠_Housing_Profile.py
    ├── 07_🎓_Education_Employment.py
    ├── 08_👪_Family_Household.py
    ├── 09_📊_Credit_Bureau_Scores.py
    ├── 10_🌍_Regional_Analysis.py
    ├── 11_📅_Application_Patterns.py
    ├── 12_📄_Document_Verification.py
    ├── 13_🔗_Correlation_Explorer.py
    └── 14_🔍_Applicant_Explorer.py
```

## What each page covers

| Page | Focus |
|---|---|
| Home | Portfolio KPIs, loan volume vs default rate, outcome split |
| Risk Overview | Risk gauge vs benchmark, risk-score distribution, education/family risk |
| Demographics | Age, gender, children, household size |
| Income Analysis | Income distribution, income type mix, income vs credit scatter |
| Loan Portfolio | Loan type mix, credit sizing, goods price vs credit, tenor |
| Default Risk Drivers | Occupation, asset ownership, organization type, employment tenure |
| Housing Profile | Housing type, wall material, property-age vs default |
| Education & Employment | Education level, income by education, tenure |
| Family & Household | Household size, accompanying persons, marital status |
| Credit Bureau Scores | EXT_SOURCE_1/2/3 distributions, correlation, decile risk |
| Regional Analysis | Region rating, population density, address-mismatch flags |
| Application Patterns | Weekday/hour heatmap of applications vs default |
| Document Verification | Docs submitted, social-circle delinquency, bureau inquiries |
| Correlation Explorer | Interactive heatmap + custom scatter tool |
| Applicant Explorer | Single-applicant risk gauge/profile lookup + full data export |

## Running it (Windows PowerShell)

See the companion `run_project.ps1` script, or run these commands manually:

```powershell
cd home_loan_dashboard
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Notes on the data

- `DAYS_EMPLOYED` contains a known sentinel value (365243) for pensioners /
  unemployed applicants — cleaned to `NaN` in `data_loader.py`.
- `RISK_SCORE` is a simple illustrative 0–100 in-house score (blend of external
  bureau scores + credit/income leverage) for demo purposes — **not** a real
  underwriting model.
- All filters in the sidebar are shared across every page via `utils/filters.py`.
