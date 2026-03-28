# Loan Portfolio Dashboard

This repository contains a Streamlit dashboard for loan portfolio visualization and risk mapping.

## Files

- `app.py`: Streamlit dashboard application.
- `requirements.txt`: Python dependencies.
- `.gitignore`: Local ignore rules.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. To load data from SQL, set environment variables:

```bash
export DATA_SOURCE=sql
export DATABASE_URL='mysql+pymysql://Sumit_Kumar_Garg:SuMKgT%2302@192.168.93.20/dwh'
export SQL_QUERY='select * from `loan-portfolio-mapping-data-2 (1)`;'
```

3. Otherwise, place your `Loan_portfolio.csv` file in the repository root or upload a CSV when prompted.

4. Run the app locally:

```bash
streamlit run app.py
```

> If you use SQL, the deployment environment must be able to reach `192.168.93.20:3306`. If the host is not reachable, the app will show a connection error.

## Deployment

To share the dashboard with your office:

- Deploy on Streamlit Community Cloud by connecting this GitHub repository.
- Or use any Python web host that supports Streamlit.

The app auto-refreshes every 10 minutes by reloading the browser page.

## Notes

- If `Loan_portfolio.csv` is not present in the repo, the app will prompt you to upload a CSV file.
- Once deployed, share the generated URL with your team.
