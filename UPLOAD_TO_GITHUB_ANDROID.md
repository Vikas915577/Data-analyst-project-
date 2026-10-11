# Upload this complete project from an Android phone

## Prepare the files

1. Download `credit-risk-loan-analytics-complete.zip` and extract it in the Files app.
2. Open the extracted `credit-risk-loan-analytics` folder. Upload the **contents of this folder**, not the ZIP itself.
3. Keep the folder structure intact (`src`, `sql`, `docs`, `data`, `.github`, and other folders must remain in their original locations).

## Upload to GitHub

1. Open your repository in Chrome. On mobile, use **Desktop site** from the browser menu if folder/file selection is difficult.
2. Select **Add file → Upload files**.
3. Select all files and folders inside the extracted project folder, including the updated root `README.md`, `index.html`, `streamlit_app.py`, and `.github/workflows` files. Do not upload only `data/raw/README.md`.
4. Commit with the message `Fix and complete credit risk analytics project`.
5. Open the repository root and confirm that `README.md`, `index.html`, `streamlit_app.py`, `requirements.txt`, `src/`, `sql/`, `docs/`, `data/sample/`, `reports/`, `excel/`, and `powerbi/` are present.

If the repository already contains obsolete duplicate dashboards, keep `streamlit_app.py` at the repository root as the one canonical app entry point. The old `app/streamlit_app.py` file is not needed; remove it after confirming the root app is present if you are comfortable deleting a file.

## Fix GitHub Pages homepage

1. Open repository **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. In **Actions**, open the `Deploy portfolio site to GitHub Pages` workflow and check its result after the commit.
4. Open the repository Pages URL. The homepage should show **Credit Risk & Loan Analytics**, not the `Raw source data (not tracked)` note. The note belongs only at `data/raw/README.md`.

The workflow publishes the static homepage and HTML report. It does not host the Python app.

## Launch the interactive dashboard

To run locally:

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

For a public interactive link, deploy the repository on Streamlit Community Cloud with `streamlit_app.py` as the app entry point. This deployment is separate from GitHub Pages.

## Before sharing with recruiters

- The included demo CSV is entirely synthetic.
- Run the automated tests (`pytest -q`) or confirm the GitHub Actions quality workflow passes.
- Do not claim the synthetic dashboard's results as empirical findings from LendingClub or any actual lender.
- Do not commit real/private/raw borrower-level files.
