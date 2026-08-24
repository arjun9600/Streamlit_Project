# =====================================================================
#  Home Loan Risk Intelligence Dashboard — Windows PowerShell setup
#  Usage:
#    1. Unzip home_loan_dashboard.zip anywhere, e.g. C:\Projects\
#    2. Open PowerShell, cd into the extracted "home_loan_dashboard" folder
#    3. Run:  .\run_project.ps1
#  (If scripts are blocked, first run:
#     Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass )
# =====================================================================

Write-Host "== Home Loan Risk Intelligence Dashboard setup ==" -ForegroundColor Cyan

# 1. Create a virtual environment (skips if it already exists)
if (-not (Test-Path ".\venv")) {
    Write-Host "Creating virtual environment (venv)..." -ForegroundColor Yellow
    python -m venv venv
}

# 2. Activate it
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
. .\venv\Scripts\Activate.ps1

# 3. Install dependencies
Write-Host "Installing requirements..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Launch the dashboard
Write-Host "Launching Streamlit app on http://localhost:8501 ..." -ForegroundColor Green
streamlit run app.py
