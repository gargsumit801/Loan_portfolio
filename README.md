# Loan Portfolio Dashboard

This repository contains a Streamlit dashboard for loan portfolio visualization and risk mapping.

## Files

- `app.py`: Streamlit dashboard application.
- `requirements.txt`: Python dependencies.
- `.gitignore`: Local ignore rules.

## Setup

1. Place your `Loan_portfolio.csv` file in the repository root.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app locally:

```bash
streamlit run app.py
```

## Deployment

To share the dashboard with your office:

- Deploy on Streamlit Community Cloud by connecting this GitHub repository.
- Or use any Python web host that supports Streamlit.

The app auto-refreshes every 10 minutes by reloading the browser page.

## Notes

- If `Loan_portfolio.csv` is not present in the repo, the app will prompt you to upload a CSV file.
- Once deployed, share the generated URL with your team.
