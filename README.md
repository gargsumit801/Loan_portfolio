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

2. To load data from CSV, set the path of your CSV file if it is not in the app folder:

```bash
export CSV_PATH='C:\\Users\\UHF5350\\Downloads\\Loan_portfolio.csv'
```

3. Run the app locally:

```bash
streamlit run app.py
```

> The app loads data from CSV. If the file is not present at the configured path, it will prompt for a local CSV upload.

## Deployment

To share the dashboard with your office:

- Deploy on Streamlit Community Cloud by connecting this GitHub repository.
- Or use any Python web host that supports Streamlit.

The app auto-refreshes every 10 minutes by reloading the browser page.

## Notes

- The app loads data from CSV. By default it looks for `C:\\Users\\UHF5350\\Downloads\\Loan_portfolio.csv` or `Loan_portfolio.csv` in the app folder.
- Set `CSV_PATH` if your file is in a different location.
- Once deployed, share the generated URL with your team.
