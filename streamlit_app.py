from __future__ import annotations
from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.analyze import run_analysis, add_bands
from src.validate_data import validate_dataframe

st.set_page_config(page_title="Credit Risk | Portfolio Analytics", page_icon="📈", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
  .block-container {padding-top: 1.5rem; padding-bottom: 2.5rem; max-width: 1500px;}
  .hero {padding: 1.35rem 1.5rem; border-radius: 18px; background: linear-gradient(115deg,#10243A 0%,#173E5C 56%,#236B73 100%); color: white; margin-bottom: 1rem;}
  .hero-eyebrow {font-size:.73rem;letter-spacing:.16em;text-transform:uppercase;opacity:.78;font-weight:700;}
  .hero h1 {font-size:2rem;line-height:1.15;margin:.55rem 0 .45rem;color:white;}
  .hero p {margin:0;color:#DDEBF4;font-size:.98rem;}
  .source-note {font-size:.83rem;color:#667085;padding:.25rem 0 .75rem;}
  div[data-testid="stMetric"] {background:#F7FAFC;border:1px solid #E4EAF0;padding:15px 16px;border-radius:14px;}
  div[data-testid="stMetricLabel"] p {font-size:.78rem;}
  div[data-testid="stMetricValue"] {font-size:1.65rem;}
  .section-title {font-size:1.13rem;font-weight:750;margin:.4rem 0 .2rem;color:#152A3B;}
  @media (prefers-color-scheme: dark) { div[data-testid="stMetric"] {background:#152536;border-color:#2D4051;} .section-title{color:#E7EDF2;} }
</style>
<div class="hero">
  <div class="hero-eyebrow">Credit portfolio intelligence · Portfolio case study</div>
  <h1>Credit Risk &amp; Loan Analytics</h1>
  <p>Understand portfolio composition, compare default rates across borrower segments, and evaluate a leakage-aware baseline model.</p>
</div>
""", unsafe_allow_html=True)

DEFAULT_FILE = ROOT / "data/sample/synthetic_loans.csv"
with st.sidebar:
    st.markdown("### DATA SOURCE")
    upload = st.file_uploader("Load a normalized loan CSV", type=["csv"], help="Required fields are documented in docs/DATA_DICTIONARY.md. Avoid uploading personal or confidential borrower data.")
    st.caption("Demo data is synthetic. It is not real LendingClub data.")
    st.divider()
    st.markdown("### PORTFOLIO FILTERS")

@st.cache_data(show_spinner=False)
def load_frame(file_bytes: bytes | None) -> pd.DataFrame:
    if file_bytes is None:
        return pd.read_csv(DEFAULT_FILE)
    from io import BytesIO
    return pd.read_csv(BytesIO(file_bytes))

try:
    raw = load_frame(upload.getvalue() if upload is not None else None)
    quality = validate_dataframe(raw)
    if not quality["passed"]:
        st.error("The supplied file did not pass required data-quality checks.")
        st.json({"problems": quality["problems"]})
        st.stop()
    data = add_bands(raw)
    analysis = run_analysis(raw)
except Exception as exc:
    st.error(f"The data could not be analyzed: {exc}")
    st.stop()

with st.sidebar:
    grade_options = sorted(data["grade"].dropna().astype(str).unique())
    purpose_options = sorted(data["purpose"].dropna().astype(str).unique())
    term_options = sorted(data["term_months"].dropna().astype(int).unique())
    selected_grades = st.multiselect("Loan grade", grade_options, default=grade_options)
    selected_purposes = st.multiselect("Loan purpose", purpose_options, default=purpose_options)
    selected_terms = st.multiselect("Loan term (months)", term_options, default=term_options)
    if st.button("Reset filters", use_container_width=True):
        st.rerun()

filtered = data[
    data["grade"].astype(str).isin(selected_grades)
    & data["purpose"].astype(str).isin(selected_purposes)
    & pd.to_numeric(data["term_months"], errors="coerce").isin(selected_terms)
].copy()
if filtered.empty:
    st.warning("No records match these filters. Change one or more selections in the sidebar.")
    st.stop()

st.markdown('<div class="source-note">Dataset: ' + ("Uploaded normalized CSV" if upload else "Bundled synthetic sample") + ' · Displayed portfolio metrics respond to filters. Model metrics use the full eligible dataset and a separate time-based holdout where possible.</div>', unsafe_allow_html=True)

n = len(filtered)
defaults = int(filtered["default_flag"].sum())
rate = float(filtered["default_flag"].mean())
exposure = float(filtered.loc[filtered["default_flag"].eq(1), "loan_amnt"].sum())
col1,col2,col3,col4,col5 = st.columns(5)
col1.metric("Loans in view", f"{n:,}")
col2.metric("Default rate", f"{rate:.1%}")
col3.metric("Defaulted loans", f"{defaults:,}")
col4.metric("Average loan", f"${filtered.loan_amnt.mean():,.0f}")
col5.metric("Defaulted loan amount", f"${exposure:,.0f}")

overview, segments, modeltab, qualitytab = st.tabs(["01 · Portfolio overview", "02 · Risk segments", "03 · Model evaluation", "04 · Data quality"])

with overview:
    left,right = st.columns((1.15,1))
    grade = filtered.groupby("grade", dropna=False).agg(loans=("loan_id","count"), defaults=("default_flag","sum"), default_rate=("default_flag","mean")).reset_index()
    grade["default_rate_pct"] = grade.default_rate * 100
    grade_order = list("ABCDEFG")
    grade["_sort"] = grade.grade.astype(str).map({g:i for i,g in enumerate(grade_order)})
    grade = grade.sort_values("_sort")
    with left:
        st.markdown('<div class="section-title">Default rate by loan grade</div>', unsafe_allow_html=True)
        fig = px.bar(grade, x="grade", y="default_rate_pct", text=grade.default_rate_pct.map(lambda v:f"{v:.1f}%"),
                     hover_data={"loans":True,"defaults":True,"default_rate_pct":":.2f","_sort":False},
                     labels={"grade":"Loan grade","default_rate_pct":"Default rate (%)","loans":"Loans","defaults":"Defaults"})
        fig.update_traces(textposition="outside", cliponaxis=False, marker_color="#2C7185")
        fig.update_layout(height=370, margin=dict(l=10,r=18,t=20,b=10), yaxis=dict(rangemode="tozero",ticksuffix="%"), xaxis=dict(categoryorder="array",categoryarray=grade_order), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown('<div class="section-title">Originations over time</div>', unsafe_allow_html=True)
        monthly = filtered.assign(issue_month=pd.to_datetime(filtered.issue_date).dt.to_period("M").astype(str)).groupby("issue_month").size().reset_index(name="loans")
        fig = px.area(monthly, x="issue_month", y="loans", labels={"issue_month":"Issue month","loans":"Loan count"})
        fig.update_traces(line_color="#2C7185", fillcolor="rgba(44,113,133,0.18)")
        fig.update_layout(height=370, margin=dict(l=10,r=18,t=20,b=10), xaxis_title=None, yaxis_title="Loans", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="section-title">Portfolio snapshot</div>', unsafe_allow_html=True)
    summary = pd.DataFrame({"Metric":["Average DTI","Average interest rate","Average annual income","Total original loan amount","Defaulted original loan amount"],
      "Value":[f"{filtered.dti.mean():.1f}%",f"{filtered.int_rate.mean():.2f}%",f"${filtered.annual_inc.mean():,.0f}",f"${filtered.loan_amnt.sum():,.0f}",f"${exposure:,.0f}"]})
    st.dataframe(summary, hide_index=True, use_container_width=True)

with segments:
    metric_select = st.selectbox("Analyze default rates by", ["Loan grade","Income band","DTI band","Loan term","Loan purpose"], index=0)
    key_map = {"Loan grade":"grade_segments","Income band":"income_segments","DTI band":"dti_segments","Loan term":"term_segments","Loan purpose":"purpose_segments"}
    col = {"Loan grade":"grade","Income band":"income_band","DTI band":"dti_band","Loan term":"term_months","Loan purpose":"purpose"}[metric_select]
    seg = filtered.groupby(col, dropna=False, observed=False).agg(loans=("loan_id","count"),defaults=("default_flag","sum"),default_rate=("default_flag","mean"),average_loan=("loan_amnt","mean")).reset_index()
    seg["default_rate_pct"] = seg.default_rate * 100
    seg["average_loan"] = seg.average_loan.round(0)
    if metric_select == "Loan grade":
        seg["sort_order"] = seg[col].astype(str).map({g:i for i,g in enumerate(list("ABCDEFG"))})
        seg = seg.sort_values("sort_order")
    else:
        seg = seg.sort_values("default_rate_pct", ascending=False)
    left,right=st.columns((1.1,1))
    with left:
        fig=px.bar(seg, x=col, y="default_rate_pct", color="default_rate_pct", color_continuous_scale="Teal",
          labels={col:metric_select,"default_rate_pct":"Default rate (%)"}, hover_data={"loans":True,"defaults":True,"average_loan":True})
        fig.update_layout(height=390,margin=dict(l=10,r=20,t=25,b=10),yaxis=dict(rangemode="tozero",ticksuffix="%"),coloraxis_showscale=False)
        st.plotly_chart(fig,use_container_width=True)
    with right:
        st.markdown("#### Segment detail")
        view=seg[[col,"loans","defaults","default_rate_pct","average_loan"]].copy()
        view["default_rate_pct"]=view["default_rate_pct"].map(lambda x: round(x,2))
        view=view.rename(columns={col:metric_select,"loans":"Loans","defaults":"Defaults","default_rate_pct":"Default rate (%)","average_loan":"Avg. loan amount ($)"})
        st.dataframe(view,hide_index=True,use_container_width=True)
    st.caption("Always compare default rates alongside the segment size. The 95% Wilson intervals are available in exported segment CSVs. Differences are descriptive associations, not causal effects.")
    de = filtered[filtered.grade.astype(str).isin(["D","E"]) & (filtered.dti > 25)]
    st.info(f"Grades D/E with DTI >25%: {len(de):,} records; {int(de.default_flag.sum()):,} defaults; {de.default_flag.mean():.1%} default rate. **This is only a result from the data currently loaded**—the bundled data is synthetic.")
    st.download_button("Download current filtered records (CSV)", filtered.to_csv(index=False).encode("utf-8"), "filtered_loan_records.csv", "text/csv")

with modeltab:
    m=analysis["metrics"]
    st.markdown("#### Baseline model — Logistic Regression")
    st.write(f"Temporal evaluation: **{m['split_method']}**. Train: {m['train_rows']:,} · Validation: {m['validation_rows']:,} · Test: {m['test_rows']:,}. Threshold was selected on validation data by F1 and then evaluated once on the later test set.")
    a,b,c,d,e = st.columns(5)
    a.metric("ROC-AUC",f"{m['roc_auc']:.3f}",help="Ranking quality; 0.5 is chance-level, 1.0 is perfect ranking.")
    b.metric("PR-AUC / AP",f"{m['average_precision']:.3f}",help="Average precision is more informative than accuracy when the positive class is uncommon.")
    c.metric("Default recall",f"{m['recall_default']:.1%}")
    d.metric("Default precision",f"{m['precision_default']:.1%}")
    e.metric("Brier score",f"{m['brier_score']:.3f}",help="Lower is better for probability quality, but calibration needs deeper review.")
    mleft,mright=st.columns(2)
    with mleft:
        cm=m["confusion_matrix"]
        cdf=pd.DataFrame(cm,index=["Actual non-default","Actual default"],columns=["Predicted non-default","Predicted default"])
        st.markdown("#### Confusion matrix")
        st.dataframe(cdf,use_container_width=True)
    with mright:
        compare=pd.DataFrame({"Metric":["ROC-AUC","Average precision","Brier score"],"Logistic regression":[m["roc_auc"],m["average_precision"],m["brier_score"]],"Prior-only baseline":[m["baseline_roc_auc"],m["baseline_average_precision"],m["baseline_brier_score"]]})
        fig=px.bar(compare.melt(id_vars="Metric",var_name="Model",value_name="Score"),x="Metric",y="Score",color="Model",barmode="group",labels={"Score":"Score"},color_discrete_sequence=["#2C7185","#A7B8C4"])
        fig.update_layout(height=325,margin=dict(l=5,r=5,t=25,b=5),legend_orientation="h",legend_y=-.2)
        st.markdown("#### Compared with a simple baseline")
        st.plotly_chart(fig,use_container_width=True)
    st.warning(f"Threshold selected on validation: {m['threshold']:.2f}. This is a portfolio exercise, **not** a lending policy. Do not use this model to approve, deny, price, or rank real applicants.")

with qualitytab:
    st.markdown("#### Data-quality summary")
    q=analysis["quality"]
    q1,q2,q3,q4=st.columns(4)
    q1.metric("Rows",f"{q['rows']:,}")
    q2.metric("Duplicate loan IDs",f"{q['duplicate_loan_ids']:,}")
    q3.metric("Invalid target rows",f"{q['invalid_target_rows']:,}")
    q4.metric("Invalid date rows",f"{q['invalid_issue_dates']:,}")
    miss=pd.DataFrame({"Column":list(q["missing_pct"]),"Missing (%)":list(q["missing_pct"].values())})
    st.dataframe(miss,hide_index=True,use_container_width=True)
    st.markdown("#### Interpretation & limitations")
    st.markdown("- The packaged dataset is synthetic and has no empirical meaning about real lending.")
    st.markdown("- If using LendingClub source files, only resolved outcomes `Fully Paid` and `Charged Off` are retained by the included preparation script; all other statuses are excluded from binary modeling.")
    st.markdown("- Features are limited to information intended to be available at or before origination. Payment/recovery/final-outcome fields must not enter the feature set.")
    st.markdown("- Time-based holdout is preferred. Thresholds, calibration, fairness, drift, reason codes, governance and legal review are required for any real-world model.")
    st.download_button("Download data-quality report (JSON)", pd.Series(q).to_json(indent=2).encode("utf-8"), "data_quality_report.json", "application/json")

st.divider()
st.caption("Portfolio learning project · Python + SQL + Power BI build assets + Excel workbook · Synthetic demo data unless a permitted external dataset is supplied.")
