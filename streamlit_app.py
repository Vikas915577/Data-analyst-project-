from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import streamlit as st
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.analyze import run_analysis

st.set_page_config(page_title="Credit Risk & Loan Analytics", page_icon="📊", layout="wide")
st.title("Credit Risk & Loan Analytics")
st.caption("Portfolio analytics • SQL + Python • Baseline model evaluation")
st.warning("Demo mode: bundled records are synthetic—not actual LendingClub data. Results are for learning and portfolio demonstration only.")
with st.sidebar:
    st.header("Data")
    upload = st.file_uploader("Upload a permitted, schema-mapped CSV", type=["csv"])
    st.caption("Required columns are documented in docs/DATA_DICTIONARY.md. Do not upload or publish personal borrower information.")
path = ROOT / "data/sample/synthetic_loans.csv"
try:
    df = pd.read_csv(upload) if upload is not None else pd.read_csv(path)
    result = run_analysis(df)
except Exception as e:
    st.error(f"Could not analyze this file: {e}")
    st.stop()
metrics = result["metrics"]
with st.sidebar:
    st.divider(); st.subheader("Filters")
    grades = st.multiselect("Grade", sorted(df["grade"].dropna().unique()), default=sorted(df["grade"].dropna().unique()))
    purposes = st.multiselect("Purpose", sorted(df["purpose"].dropna().unique()), default=sorted(df["purpose"].dropna().unique()))
    terms = st.multiselect("Term (months)", sorted(df["term_months"].dropna().unique()), default=sorted(df["term_months"].dropna().unique()))
filtered = df[df["grade"].isin(grades) & df["purpose"].isin(purposes) & df["term_months"].isin(terms)].copy()
if filtered.empty:
    st.info("No loans match these filters. Adjust the sidebar selections."); st.stop()
def_rate = filtered["default_flag"].mean()*100
a,b,c,d = st.columns(4)
a.metric("Loans in view", f"{len(filtered):,}")
b.metric("Default rate", f"{def_rate:.1f}%")
c.metric("Average loan", f"${filtered['loan_amnt'].mean():,.0f}")
d.metric("Average DTI", f"{filtered['dti'].mean():.1f}%")
st.divider()
tab1, tab2, tab3, tab4 = st.tabs(["Portfolio overview", "Risk segments", "Model evaluation", "Data quality & notes"])
with tab1:
    left,right=st.columns(2)
    with left:
        g=filtered.groupby("grade", observed=False).agg(loans=("loan_id","count"), default_rate=("default_flag","mean")).reset_index(); g["default_rate_pct"]=g.default_rate*100
        st.subheader("Default rate by grade"); st.plotly_chart(px.bar(g, x="grade", y="default_rate_pct", hover_data=["loans"], labels={"grade":"Grade","default_rate_pct":"Default rate (%)"}), use_container_width=True)
    with right:
        t=filtered.groupby("term_months").agg(loans=("loan_id","count"), default_rate=("default_flag","mean")).reset_index(); t["default_rate_pct"]=t.default_rate*100
        st.subheader("Default rate by term"); st.plotly_chart(px.bar(t, x="term_months", y="default_rate_pct", hover_data=["loans"], labels={"term_months":"Term (months)","default_rate_pct":"Default rate (%)"}), use_container_width=True)
    st.subheader("Monthly originations")
    dates=filtered.assign(issue_month=pd.to_datetime(filtered.issue_date, errors="coerce").dt.to_period("M").astype(str)).groupby("issue_month").size().reset_index(name="loans")
    st.plotly_chart(px.line(dates, x="issue_month", y="loans", labels={"issue_month":"Issue month","loans":"Loans"}), use_container_width=True)
with tab2:
    left,right=st.columns(2)
    with left:
        s=filtered.groupby("purpose").agg(loans=("loan_id","count"), defaults=("default_flag","sum"), rate=("default_flag","mean")).reset_index(); s["default_rate_pct"]=s.rate*100
        st.subheader("Purpose risk table"); st.dataframe(s[["purpose","loans","defaults","default_rate_pct"]].sort_values("default_rate_pct", ascending=False), use_container_width=True, hide_index=True)
    with right:
        dti_band=pd.cut(filtered.dti, [-0.001,10,20,30,100.001], labels=["<10","10–<20","20–<30","30+"])
        s2=filtered.assign(dti_band=dti_band).groupby("dti_band", observed=False).agg(loans=("loan_id","count"), rate=("default_flag","mean")).reset_index(); s2["default_rate_pct"]=s2.rate*100
        st.subheader("Default rate by DTI band"); st.plotly_chart(px.bar(s2, x="dti_band", y="default_rate_pct", hover_data=["loans"], labels={"dti_band":"DTI band (%)","default_rate_pct":"Default rate (%)"}), use_container_width=True)
    st.caption("Always inspect segment counts alongside rates; small groups can be volatile. Filtered rates are descriptive associations, not causal effects.")
with tab3:
    st.subheader("Baseline Logistic Regression")
    st.write("Model metrics below are calculated on a stratified holdout from the full loaded dataset, not just the visual filters. The bundled demo target is simulated.")
    m1,m2,m3,m4=st.columns(4); m1.metric("ROC-AUC", f"{metrics['roc_auc']:.3f}"); m2.metric("Default precision", f"{metrics['precision_default']:.3f}"); m3.metric("Default recall", f"{metrics['recall_default']:.3f}"); m4.metric("Default F1", f"{metrics['f1_default']:.3f}")
    cm=metrics["confusion_matrix"]; st.write("Confusion matrix — rows are actual, columns are predicted (non-default, default)")
    st.dataframe(pd.DataFrame(cm, index=["Actual non-default","Actual default"], columns=["Predicted non-default","Predicted default"]), use_container_width=True)
    st.caption("Threshold = 0.50 for demonstration only. No model should be used for lending decisions without temporal validation, calibration, cost/threshold review, fairness/legal review, and monitoring.")
with tab4:
    st.subheader("Data quality checks")
    q=result["quality"]; st.write({k:v for k,v in q.items() if k != "missing_pct"})
    st.dataframe(pd.DataFrame({"column":list(q["missing_pct"].keys()),"missing_pct":list(q["missing_pct"].values())}), use_container_width=True, hide_index=True)
    st.subheader("Interpretation guardrails")
    st.markdown("- Demo data is synthetic; its patterns are not evidence about actual LendingClub borrowers.\n- For real data, define the default label from the source data dictionary and exclude unresolved outcomes.\n- Keep predictors restricted to information available at origination to avoid leakage.\n- Use a time-based test set for real historical data; review calibration and subgroup performance.\n- Correlation is not causation; do not use this educational dashboard to approve, deny, price, or rank individual applicants.")
    st.download_button("Download filtered CSV", filtered.to_csv(index=False).encode("utf-8"), file_name="filtered_loan_demo.csv", mime="text/csv")
