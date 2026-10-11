"""Render the static README-style dashboard image from the synthetic sample."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
COLORS = {"navy":"#10243A", "teal":"#1F6175", "teal2":"#3A8D91", "gold":"#E5A95B", "muted":"#66788A", "bg":"#F4F7F9", "line":"#DDE6EC"}

def create_preview(input_path=None, output_path=None):
    input_path = Path(input_path or ROOT / "data/sample/synthetic_loans.csv")
    output_path = Path(output_path or ROOT / "reports/dashboard_preview.png")
    df = pd.read_csv(input_path)
    df["issue_date"] = pd.to_datetime(df["issue_date"])
    df["issue_year"] = df["issue_date"].dt.year
    grade = df.groupby("grade").default_flag.agg(["count", "mean"]).reindex(list("ABCDEFG"))
    income = pd.cut(df.annual_inc, [-float("inf"),25000,50000,75000,100000,float("inf")], labels=["<$25k","$25–50k","$50–75k","$75–100k","$100k+"])
    dti = pd.cut(df.dti, [-float("inf"),10,20,25,35,float("inf")], labels=["<10","10–20","20–25","25–35","35+"])
    plt.rcParams.update({"font.family":"DejaVu Sans","axes.titleweight":"bold","axes.titlesize":12,"axes.labelsize":9,"xtick.labelsize":8,"ytick.labelsize":8})
    fig = plt.figure(figsize=(16,9), facecolor=COLORS["bg"])
    header = fig.add_axes([.035,.83,.93,.14]); header.set_axis_off()
    header.add_patch(FancyBboxPatch((0,0),1,1,boxstyle="round,pad=0.012,rounding_size=0.04",facecolor=COLORS["navy"],edgecolor="none"))
    header.text(.035,.69,"CREDIT RISK & LOAN ANALYTICS",fontsize=19,fontweight="bold",color="white",va="center")
    header.text(.035,.35,"PORTFOLIO CASE STUDY  •  SQL  •  PYTHON  •  POWER BI ASSETS  •  EXCEL",fontsize=9,fontweight="bold",color="#CFE6EC",va="center")
    header.text(.965,.36,"SYNTHETIC DEMO DATA",fontsize=9,fontweight="bold",color=COLORS["gold"],ha="right",va="center")
    kpis=[("LOANS IN DEMO",f"{len(df):,}"),("DEFAULT RATE",f"{df.default_flag.mean():.1%}"),("AVG. LOAN",f"${df.loan_amnt.mean():,.0f}"),("DEFAULTED ORIGINAL AMOUNT",f"${df.loc[df.default_flag.eq(1),'loan_amnt'].sum()/1e6:.1f}M")]
    for i,(label,value) in enumerate(kpis):
        ax=fig.add_axes([.035+i*.237,.715,.22,.09]); ax.set_axis_off()
        ax.add_patch(FancyBboxPatch((0,0),1,1,boxstyle="round,pad=0.015,rounding_size=0.06",facecolor="white",edgecolor=COLORS["line"],linewidth=1))
        ax.text(.07,.68,label,fontsize=8,color=COLORS["muted"],fontweight="bold",va="center")
        ax.text(.07,.30,value,fontsize=17,color=COLORS["navy"],fontweight="bold",va="center")
    a1=fig.add_axes([.055,.39,.42,.26],facecolor="white")
    a1.bar(list("ABCDEFG"),grade["mean"]*100,color=[COLORS["teal"] if g not in "FG" else COLORS["gold"] for g in "ABCDEFG"],width=.62)
    a1.set_title("Default rate by loan grade",loc="left",color=COLORS["navy"],pad=12); a1.set_ylabel("Default rate (%)",color=COLORS["muted"])
    a1.spines[["top","right","left"]].set_visible(False); a1.spines["bottom"].set_color(COLORS["line"]); a1.grid(axis="y",alpha=.16); a1.set_axisbelow(True); a1.tick_params(length=0,colors=COLORS["muted"]); a1.set_ylim(0,max(grade["mean"]*100)*1.22)
    for i,v in enumerate(grade["mean"]*100): a1.text(i,v+.7,f"{v:.1f}%",ha="center",fontsize=8,color=COLORS["navy"])
    a2=fig.add_axes([.545,.39,.40,.26],facecolor="white"); annual=df.groupby("issue_year").size()
    a2.plot(annual.index.astype(str),annual.values,marker="o",linewidth=2.2,color=COLORS["teal"]); a2.fill_between(range(len(annual)),annual.values,alpha=.13,color=COLORS["teal"])
    a2.set_title("Originations by issue year",loc="left",color=COLORS["navy"],pad=12); a2.set_ylabel("Loan records",color=COLORS["muted"])
    a2.spines[["top","right","left"]].set_visible(False); a2.spines["bottom"].set_color(COLORS["line"]); a2.grid(axis="y",alpha=.16); a2.set_axisbelow(True); a2.tick_params(length=0,colors=COLORS["muted"])
    a3=fig.add_axes([.055,.095,.42,.23],facecolor="white")
    income_rate=df.assign(income_band=income).groupby("income_band",observed=False).default_flag.mean()*100
    a3.bar([str(x) for x in income_rate.index],income_rate.values,color=COLORS["teal2"],width=.65)
    a3.set_title("Default rate by annual income",loc="left",color=COLORS["navy"],pad=12); a3.set_ylabel("Default rate (%)",color=COLORS["muted"])
    a3.spines[["top","right","left"]].set_visible(False); a3.spines["bottom"].set_color(COLORS["line"]); a3.grid(axis="y",alpha=.16); a3.set_axisbelow(True); a3.tick_params(length=0,colors=COLORS["muted"])
    a4=fig.add_axes([.545,.095,.40,.23],facecolor="white")
    dti_rate=df.assign(dti_band=dti).groupby("dti_band",observed=False).default_flag.mean()*100
    a4.bar([str(x) for x in dti_rate.index],dti_rate.values,color=COLORS["gold"],width=.65)
    a4.set_title("Default rate by DTI band",loc="left",color=COLORS["navy"],pad=12); a4.set_ylabel("Default rate (%)",color=COLORS["muted"])
    a4.spines[["top","right","left"]].set_visible(False); a4.spines["bottom"].set_color(COLORS["line"]); a4.grid(axis="y",alpha=.16); a4.set_axisbelow(True); a4.tick_params(length=0,colors=COLORS["muted"])
    fig.text(.035,.025,"Illustrative static preview only. All included records are synthetic; rates are not real LendingClub findings.",fontsize=8,color=COLORS["muted"])
    output_path.parent.mkdir(parents=True,exist_ok=True); fig.savefig(output_path,dpi=150,bbox_inches="tight",facecolor=fig.get_facecolor()); plt.close(fig)
    print(f"Saved synthetic dashboard preview to {output_path}")

if __name__ == "__main__": create_preview()
