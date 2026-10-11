"""Create a standalone interactive HTML report and README preview from demo data."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.analyze import run_analysis, add_bands

ROOT=Path(__file__).resolve().parents[1]
NAVY="#10243A"; TEAL="#1F6175"; PALE="#EAF2F5"; GOLD="#E5A95B"; RED="#D96A62"

def create_report(input_path: str = "data/sample/synthetic_loans.csv", output_path: str = "reports/demo_analysis.html"):
    df=pd.read_csv(input_path); data=add_bands(df); result=run_analysis(df); m=result["metrics"]
    grade=data.groupby("grade").agg(loans=("loan_id","count"),defaults=("default_flag","sum"),rate=("default_flag","mean")).reset_index()
    grade["rate_pct"]=grade.rate*100; grade["label"]=grade.rate_pct.map(lambda v:f"{v:.1f}%")
    grade["order"]=grade.grade.map({g:i for i,g in enumerate("ABCDEFG")}); grade=grade.sort_values("order")
    income=data.groupby("income_band",observed=False).agg(loans=("loan_id","count"),defaults=("default_flag","sum"),rate=("default_flag","mean")).reset_index(); income["rate_pct"]=income.rate*100
    dti=data.groupby("dti_band",observed=False).agg(loans=("loan_id","count"),defaults=("default_flag","sum"),rate=("default_flag","mean")).reset_index(); dti["rate_pct"]=dti.rate*100
    monthly=data.assign(issue_month=pd.to_datetime(data.issue_date).dt.to_period("M").astype(str)).groupby("issue_month").size().reset_index(name="loans")
    figs=[]
    f1=px.bar(grade,x="grade",y="rate_pct",text="label",hover_data={"loans":True,"defaults":True,"rate_pct":":.2f","order":False},labels={"grade":"Loan grade","rate_pct":"Default rate (%)"},title="Default rate by loan grade")
    f1.update_traces(marker_color=TEAL,textposition="outside",cliponaxis=False); f1.update_layout(height=390,margin=dict(l=20,r=20,t=60,b=20),yaxis=dict(rangemode="tozero",ticksuffix="%"),xaxis=dict(categoryorder="array",categoryarray=list("ABCDEFG")),showlegend=False)
    figs.append(f1)
    f2=px.bar(income,x="income_band",y="rate_pct",hover_data={"loans":True,"defaults":True,"rate_pct":":.2f"},labels={"income_band":"Annual income band","rate_pct":"Default rate (%)"},title="Default rate by annual income band")
    f2.update_traces(marker_color=GOLD); f2.update_layout(height=390,margin=dict(l=20,r=20,t=60,b=20),yaxis=dict(rangemode="tozero",ticksuffix="%"),showlegend=False)
    figs.append(f2)
    f3=px.bar(dti,x="dti_band",y="rate_pct",hover_data={"loans":True,"defaults":True,"rate_pct":":.2f"},labels={"dti_band":"Debt-to-income band (%)","rate_pct":"Default rate (%)"},title="Default rate by DTI band")
    f3.update_traces(marker_color=RED); f3.update_layout(height=390,margin=dict(l=20,r=20,t=60,b=20),yaxis=dict(rangemode="tozero",ticksuffix="%"),showlegend=False)
    figs.append(f3)
    f4=px.area(monthly,x="issue_month",y="loans",labels={"issue_month":"Issue month","loans":"Originations"},title="Monthly originations")
    f4.update_traces(line_color=TEAL,fillcolor="rgba(31,97,117,0.18)"); f4.update_layout(height=390,margin=dict(l=20,r=20,t=60,b=20),showlegend=False)
    figs.append(f4)
    sections=[]
    for i,fig in enumerate(figs):
        sections.append(fig.to_html(full_html=False,include_plotlyjs=(i==0),config={"responsive":True,"displaylogo":False}))
    lo=max(float(df.loc[df.default_flag.eq(1),"loan_amnt"].sum()),0)
    de=result["grade_de_target"]
    body=f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Credit Risk &amp; Loan Analytics — Demo Report</title>
<style>
:root{{--navy:{NAVY};--teal:{TEAL};--ink:#172B3A;--muted:#657584;--line:#E3EAF0;--panel:#FFFFFF;--bg:#F3F7F9;--gold:{GOLD};}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);font:15px/1.55 Inter,Segoe UI,Arial,sans-serif;color:var(--ink)}}.wrap{{max-width:1200px;margin:auto;padding:28px 22px 50px}}header{{padding:30px;border-radius:18px;color:white;background:linear-gradient(115deg,var(--navy),var(--teal))}}.eyebrow{{letter-spacing:.16em;text-transform:uppercase;font-size:.72rem;color:#CFE6EC;font-weight:700}}h1{{font-size:clamp(1.7rem,4vw,2.5rem);line-height:1.15;margin:.5rem 0}}header p{{color:#DAE8EE;margin:0;max-width:850px}}.notice{{background:#FFF7E8;border:1px solid #F1D6A6;color:#73531C;border-radius:12px;padding:13px 15px;margin:16px 0}}.kpis{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:16px 0}}.kpi{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px}}.kpi span{{display:block;color:var(--muted);font-size:.82rem}}.kpi b{{display:block;font-size:1.55rem;margin-top:5px;color:var(--navy)}}.section{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px;margin:16px 0}}h2{{margin:0 0 9px;font-size:1.22rem}}.chart{{width:100%}}.cols{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}.small{{color:var(--muted);font-size:.9rem}}footer{{color:var(--muted);font-size:.82rem;margin-top:20px}}@media(max-width:760px){{.kpis{{grid-template-columns:repeat(2,minmax(0,1fr))}}.cols{{grid-template-columns:1fr}}.wrap{{padding:14px}}header{{padding:22px}}}}
</style></head><body><main class="wrap"><header><div class="eyebrow">Portfolio case study · Demo output</div><h1>Credit Risk &amp; Loan Analytics</h1><p>Resolved-outcome loan segmentation, risk rates with denominators, and a chronological model-evaluation demonstration.</p></header>
<div class="notice"><b>Read before interpreting:</b> This report uses synthetic demo records generated by this repository. These numbers are software-test outputs, not LendingClub findings and not evidence about real borrowers.</div>
<div class="kpis"><div class="kpi"><span>Loans in demo</span><b>{len(df):,}</b></div><div class="kpi"><span>Synthetic default rate</span><b>{df.default_flag.mean():.1%}</b></div><div class="kpi"><span>Average loan amount</span><b>${df.loan_amnt.mean():,.0f}</b></div><div class="kpi"><span>Defaulted original amount</span><b>${lo:,.0f}</b></div></div>
<section class="section"><h2>1. Risk differs across simulated segments</h2><p class="small">Bars show default rate; hover to inspect loan counts and default counts. Small samples can have volatile rates; compare denominators and confidence intervals in exported tables.</p>{sections[0]}</section>
<div class="cols"><section class="section"><h2>2. Income segmentation</h2><p class="small">Fixed annual-income bands support consistent comparisons across runs.</p>{sections[1]}</section><section class="section"><h2>3. Debt-to-income segmentation</h2><p class="small">DTI is stored in percentage points: 25 means 25%.</p>{sections[2]}</section></div>
<section class="section"><h2>4. Origination trend</h2><p class="small">Monthly origination volume is descriptive. No conclusion is drawn about macroeconomic drivers from synthetic data.</p>{sections[3]}</section>
<section class="section"><h2>5. Model evaluation</h2><p>The Logistic Regression baseline achieved <b>ROC-AUC {m['roc_auc']:.3f}</b> and average precision <b>{m['average_precision']:.3f}</b> on a held-out later period (split: {m['split_method']}). Its prior-only reference model scored ROC-AUC {m['baseline_roc_auc']:.3f} and average precision {m['baseline_average_precision']:.3f}. The illustrative threshold ({m['threshold']:.2f}) was selected on validation data using F1 before testing on the final holdout.</p><p class="small">Do not interpret these synthetic scores as real-world model performance or use this model to make individual credit decisions. Probability calibration, threshold costs, fairness/legal review, reason codes, drift monitoring and governance are not production-validated here.</p></section>
<section class="section"><h2>6. Target segment to recompute on actual source data</h2><p>The project calculates the default rate for Grade D/E loans with DTI &gt;25%. In this run: <b>{de['loans']:,}</b> synthetic loans, <b>{de['defaults']:,}</b> defaults, rate <b>{de['default_rate_pct']:.1f}%</b>. Recompute this on a permitted real dataset before sharing any empirical statement or adding a percentage to a resume.</p></section>
<footer>Generated from the project's synthetic sample · Data prep and methods documented in README.md, docs/METHODOLOGY.md and docs/DATA_DICTIONARY.md · Model metrics follow scikit-learn documentation.</footer></main></body></html>'''
    out=Path(output_path); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(body,encoding="utf-8")
    print(f"Wrote self-contained interactive report: {out}")

if __name__ == "__main__": create_report()
