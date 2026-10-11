# Upload this project to GitHub from Android

1. Download `credit-risk-loan-analytics.zip` and extract it with your phone's Files app.
2. In a browser, open https://github.com/new and sign in.
3. Repository name: `credit-risk-loan-analytics`.
4. Description: `Credit risk and loan analytics using Python, SQL, Streamlit, and a leakage-aware baseline model`.
5. Choose **Public** for a portfolio project, and do not initialize with a README (the project already has one).
6. Create the repository. On the repository page, choose **Add file → Upload files**.
7. Upload the *contents* of the extracted project folder, preserving folders (`app`, `data`, `docs`, `sql`, `src`, `tests`). Do not upload the ZIP as the only file.
8. Commit with message `Add credit risk analytics project`.
9. Open the repository README and verify that folder links and the data notice appear.

## Optional: publish the dashboard

1. Push the repository first.
2. Open https://share.streamlit.io/ and sign in with GitHub.
3. Create app → select repository `credit-risk-loan-analytics`, branch `main`, main file `app/streamlit_app.py`.
4. Deploy. Streamlit Cloud installs packages from `requirements.txt`.
5. Open the deployed URL and test the filters, charts, model tab, and data-quality tab.

**Important:** Python validation and model tests pass in the prepared environment, but Streamlit could not be installed in that environment because package-network access was unavailable. Therefore the browser dashboard still needs a first live smoke test after deployment. Bundled data is synthetic demo data, not real LendingClub data.
