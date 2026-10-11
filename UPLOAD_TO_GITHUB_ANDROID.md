# Upload this project to GitHub from Android

1. Download `credit-risk-loan-analytics.zip` and extract it with your phone's Files app (or use a ZIP extractor).
2. Open https://github.com/new in Chrome or GitHub Mobile.
3. Repository name: `credit-risk-loan-analytics`.
4. Description: `Credit risk portfolio analytics with SQL, Python, Power BI and Excel`.
5. Choose **Public** only if you want recruiters to see it. Keep real/raw borrower data out of the repository.
6. You may initialize the repository with a README, but if this project already has a `README.md`, avoid creating a duplicate. Easiest path: create an empty repository with no README/license/gitignore.
7. Open the new repository → **Add file → Upload files**. Select the files inside the extracted `credit-risk-loan-analytics` folder (not just the ZIP file). If the mobile browser cannot select multiple folders/files reliably, use GitHub's web desktop mode or upload a smaller set first.
8. Commit message: `Add credit risk analytics portfolio project`.
9. After upload, open `README.md` and confirm the file list and links render correctly.
10. For test verification, run the project locally or enable the included GitHub Actions workflow; do not say the live dashboard works until you have run it or deployed it successfully.

## Before publishing

- The bundled CSV is explicitly synthetic.
- Do not commit downloaded LendingClub raw files or any row-level confidential/private data; `data/raw/` is git-ignored by default.
- Do not claim the included synthetic numbers are findings from real LendingClub loans.
- If deploying to Streamlit Community Cloud, choose `app/streamlit_app.py` as the entry file and ensure `requirements.txt` is present at repository root.
