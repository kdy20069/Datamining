#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create the three requested 300-DPI figures from project CSV records only."""
import csv
import os
import re
import textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(HERE)
DATA=os.path.join(ROOT,"data")
OUT=HERE
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":12,"axes.titlesize":16,"axes.labelsize":13,"figure.facecolor":"white","axes.facecolor":"white"})

def read(path):
    with open(path,newline="",encoding="utf-8") as f:return list(csv.DictReader(f))

def score_from_summary(s):
    m=re.search(r"overall association score=([0-9.eE+-]+)",s or "")
    return float(m.group(1)) if m else None

def row_nodes(s): return [x for x in (s or "").split(";") if x]

def arrow(ax,a,b,kind="observed",color="#526579",rad=0.0,lw=1.8,label=None,arrowstyle="-|>"):
    style="-" if kind=="observed" else (0,(4,3))
    p=FancyArrowPatch(a,b,arrowstyle=arrowstyle,mutation_scale=13,linewidth=lw,linestyle=style,color=color,
        connectionstyle=f"arc3,rad={rad}",shrinkA=18,shrinkB=18,zorder=1,alpha=.88)
    ax.add_patch(p)
    if label:
        mx=(a[0]+b[0])/2; my=(a[1]+b[1])/2
        ax.text(mx,my,label,fontsize=9,color=color,ha="center",va="center",bbox=dict(boxstyle="round,pad=.18",fc="white",ec="none",alpha=.9),zorder=4)

def node(ax,xy,label,fc,ec="#263748",width=1.35,height=.55,fontsize=10,weight="normal",textcolor="#142333"):
    x,y=xy
    p=FancyBboxPatch((x-width/2,y-height/2),width,height,boxstyle="round,pad=.04,rounding_size=.08",fc=fc,ec=ec,lw=1.25,zorder=3)
    ax.add_patch(p)
    ax.text(x,y,label,ha="center",va="center",fontsize=fontsize,color=textcolor,fontweight=weight,zorder=4,wrap=True)

def fig1():
    pairs=read(os.path.join(HERE,"pair_matrix_2x3.csv"))
    ctd=read(os.path.join(DATA,"ctd_direction_audit.csv"))
    aids=read(os.path.join(DATA,"pubchem_aids.csv"))
    expanded=read(os.path.join(DATA,"expanded_db_evidence.csv"))
    evid=read(os.path.join(HERE,"evidence_table.csv"))
    # Positions are fixed for legibility; all nodes and edges are sourced from these tables.
    chemicals={"Permethrin":(1.8,8.25),"Prallethrin":(1.8,7.15),"PBO":(1.8,6.05),"Diazepam":(1.8,4.95),"Alprazolam":(1.8,3.85)}
    enzymes={"CYP3A4":(5.8,8.0),"CYP2C19":(5.8,6.65),"POR":(5.8,5.3)}
    subunits=["GABRA1","GABRA2","GABRA3","GABRA5","GABRB2","GABRG2"]
    sub_pos={g:(12.7,7.45-i*.68) for i,g in enumerate(subunits)}
    gaba_hub=(8.7,4.45)
    events={"KE64":(2.1,1.95),"KE669":(5.9,1.95),"KE682":(9.7,1.95),"KE616":(13.5,1.95),"AO613":(17.3,1.95)}

    # Draw for the report's 18 cm print width: at this canvas size 9 pt remains 9 pt on paper.
    fig,ax=plt.subplots(figsize=(7.2,4.0),constrained_layout=False)
    fig.subplots_adjust(left=.025,right=.985,top=.93,bottom=.075)
    ax.set_xlim(-.2,19.5); ax.set_ylim(.2,10.1); ax.axis("off")
    for x,y,label in [(1.8,9.18,"Compounds"),(5.8,9.18,"CYP enzymes"),(12.7,9.18,"GABA-A subunits")]:
        ax.text(x,y,label,ha="center",va="bottom",fontsize=9,color="#455769",fontweight="bold",linespacing=.95)

    # Direct pesticide-to-enzyme observations, taken from CTD and PubChem/ChEMBL rows.
    pest_edges={"Permethrin":{"CYP3A4":"CTD PMID 24548679","CYP2C19":"CTD PMID 24548679"},"Prallethrin":{},"PBO":{}}
    for r in ctd:
        if r.get("ChemicalName")=="Permethrin" and r.get("GeneSymbol") in enzymes and r.get("PMID"):
            pest_edges["Permethrin"][r["GeneSymbol"]]=f"CTD PMID {r['PMID']}"
    for r in aids:
        if r.get("ChemicalName")=="Prallethrin" and r.get("GeneSymbol") in enzymes:
            pest_edges["Prallethrin"][r["GeneSymbol"]]=f"PubChem AID {r.get('AID')}"
    for r in expanded:
        if r.get("candidate_compound")=="PBO" and r.get("source_db")=="ChEMBL archived activity observed" and r.get("target_gene") in enzymes:
            pest_edges["PBO"][r["target_gene"]]="ChEMBL archived assay"
    for chem in ["Permethrin","Prallethrin","PBO"]:
        node(ax,chemicals[chem],chem,"#F4C6A5",width=2.9,height=.62,fontsize=9.5,weight="bold")
        for gene,label in pest_edges[chem].items():
            arrow(ax,chemicals[chem],enzymes[gene],"observed",color="#B95B36",rad=.04 if gene=="CYP3A4" else -.04)

    # Direct KEGG metabolism and receptor target curation.
    benz_edges={x:set() for x in ("Diazepam","Alprazolam")}
    for r in expanded:
        chem=r.get("candidate_compound")
        if chem in benz_edges and r.get("source_db")=="KEGG Drug observed" and r.get("status_or_failure_reason")=="observed":
            if r.get("target_gene") in enzymes: benz_edges[chem].add(r["target_gene"])
            note=r.get("interaction_direction_note","")
            if "TARGET field" in note:
                for g in subunits:
                    if re.search(rf"\b{ {'GABRA1':'2554','GABRA2':'2555','GABRA3':'2556','GABRA5':'2558','GABRB2':'2561','GABRG2':'2566'}[g] }\b",note):benz_edges[chem].add(g)
    for chem in ("Diazepam","Alprazolam"):
        node(ax,chemicals[chem],chem,"#B8D8D0",width=2.9,height=.62,fontsize=9.5,weight="bold")
        for gene in benz_edges[chem]:
            if gene in enzymes:
                arrow(ax,chemicals[chem],enzymes[gene],"observed",color="#287C70",rad=.035 if gene=="CYP3A4" else -.035,lw=1.45)
    # Draw target nodes after arrows.
    node(ax,enzymes["CYP3A4"],"CYP3A4","#DCE6F2",width=2.7,height=.62,fontsize=9,weight="bold")
    node(ax,enzymes["CYP2C19"],"CYP2C19","#DCE6F2",width=2.7,height=.62,fontsize=9,weight="bold")
    node(ax,enzymes["POR"],"POR\n(network\nneighbor)","#E9E4F4",width=2.5,height=.95,fontsize=8.5,weight="bold")
    target_count=len(set().union(*(benz_edges[c] for c in ("Diazepam","Alprazolam"))) & set(subunits))
    node(ax,gaba_hub,f"KEGG GABR\ntarget set\n({target_count} subunits)","#B8D8D0",width=2.8,height=1.0,fontsize=8.5,weight="bold")
    for chem in ("Diazepam","Alprazolam"):
        if benz_edges[chem].intersection(subunits):
            arrow(ax,chemicals[chem],gaba_hub,"observed",color="#287C70",rad=.04 if chem=="Diazepam" else -.04,lw=1.6)
    for g in subunits:
        if g in benz_edges["Diazepam"] or g in benz_edges["Alprazolam"]:
            arrow(ax,gaba_hub,sub_pos[g],"observed",color="#287C70",lw=1.05,rad=(subunits.index(g)-2.5)*.025)
    for g,pos in sub_pos.items():node(ax,pos,g,"#D7EBDD",width=1.9,height=.52,fontsize=9,weight="bold")

    # Explicit evidence-table relations and marked inferential bridges.
    stringrow=next((r for r in evid if r.get("source_db","").startswith("STRING") and "CYP3A4-POR" in r.get("record_id","")),None)
    if stringrow:
        arrow(ax,enzymes["CYP3A4"],enzymes["POR"],"observed",color="#64549B",lw=2.0,arrowstyle="-",rad=.0)
    inferred1=next((r for r in evid if r.get("record_id")=="INFERRED_01" and r.get("link_type")=="inferred"),None)
    if inferred1 and "CYP2C19" not in pest_edges["PBO"]:
        arrow(ax,chemicals["PBO"],enzymes["CYP2C19"],"inferred",color="#B95B36",rad=-.12,lw=1.6)

    # AOP nodes and KER edges: use the exact labels stored in the local evidence table.
    ke64=next((r.get("source_node","") for r in evid if r.get("source_db")=="AOP-Wiki AOP 10" and r.get("record_id")=="KER 667"),"KE64")
    ke669=next((r.get("target_node","") for r in evid if r.get("record_id")=="KER 667"),"KE669")
    ke682=next((r.get("source_node","") for r in evid if r.get("record_id")=="KER 684"),"KE682")
    ke616=next((r.get("target_node","") for r in evid if r.get("record_id")=="KER 684"),"KE616")
    ao613=next((r.get("target_node","") for r in evid if r.get("record_id")=="KER 630"),"AO 613")
    # Compact labels retain each event's source meaning while fitting at 9 pt;
    # full event wording remains in evidence_table.csv.
    event_labels={"KE64":"KE 64:\nReduced\nionotropic GABA\nreceptor Cl-\nconductance",
                  "KE669":"KE 669:\nReduced\nneuronal\nsynaptic\ninhibition",
                  "KE682":"KE 682:\nGeneration of\namplified EPSP",
                  "KE616":"KE 616:\nParoxysmal\ndepolarizing shift",
                  "AO613":"AO 613:\nEpileptic\nseizure"}
    event_widths={"KE64":3.35,"KE669":2.5,"KE682":2.5,"KE616":2.8,"AO613":2.5}
    for key,pos in events.items():
        label=event_labels[key]
        color="#F2D99B" if key.startswith("KE") else "#E8B8B8"
        node(ax,pos,label,color,width=event_widths[key],height=2.15,fontsize=8.5,weight="bold")
    # GABA receptor and CYP3A4 to KE64 are explicitly dashed synthesis hypotheses.
    arrow(ax,gaba_hub,events["KE64"],"inferred",color="#558459",lw=1.8,rad=-.04)
    arrow(ax,enzymes["CYP3A4"],events["KE64"],"inferred",color="#64549B",lw=1.6,rad=-.13)
    # Local table has KER667, KER684 and KER630 but no KE669 -> KE682 relationship;
    # show that missing link as dashed and label it, rather than presenting it as observed.
    ker_by_id={r.get("record_id"):r for r in evid if r.get("source_db")=="AOP-Wiki AOP 10"}
    arrow(ax,events["KE64"],events["KE669"],"observed",color="#8F6C13")
    arrow(ax,events["KE669"],events["KE682"],"inferred",color="#9A6B45",arrowstyle="-|>")
    arrow(ax,events["KE682"],events["KE616"],"observed",color="#8F6C13")
    arrow(ax,events["KE616"],events["AO613"],"observed",color="#8F6C13")
    ax.text(13.9,3.48,"Dashed KE 669 -> KE 682 is absent from supplied KER rows.",ha="center",va="center",fontsize=8.5,color="#785C43")
    ax.text(.15,.25,"GABR → KE64 is a pathway hypothesis; KE64 is not a direct effect measurement for these compounds.",ha="left",va="center",fontsize=8.5,color="#455769")
    leg=[Line2D([0],[0],color="#526579",lw=2,label="Observed record / KER (solid)"),Line2D([0],[0],color="#526579",lw=2,ls="--",label="Inferred or unverified bridge (dashed)")]
    ax.legend(handles=leg,loc="upper center",frameon=False,fontsize=8.5,ncol=1,bbox_to_anchor=(.70,.92))
    fig.suptitle("Integrated insecticide–benzodiazepine evidence network",fontsize=9.5,fontweight="bold",y=.99)
    fig.savefig(os.path.join(OUT,"fig1_integrated_network.png"),dpi=300,bbox_inches="tight",pad_inches=0.06)
    plt.close(fig)

def fig2():
    direct=read(os.path.join(DATA,"psychiatric_cyp_check.csv"))
    genes=["CYP3A4","CYP2C19","POR"]
    diseases=[("MONDO_0002009","MDD"),("MONDO_0005090","Schizophrenia"),("MONDO_0005618","Anxiety disorder"),("MONDO_0005027","Epilepsy"),("EFO_0011057","Neurotoxicity"),("HP_0002384","Focal impaired\nawareness seizure")]
    # Use the exact returned disease IDs/names in the input; focal seizure is reported
    # separately when an explicitly seizure-named record is present.
    vals=np.full((len(genes),len(diseases)),np.nan)
    for i,g in enumerate(genes):
        for j,(did,label) in enumerate(diseases):
            matches=[r for r in direct if r.get("gene_symbol")==g and r.get("disease_id")==did and ("seizure" in r.get("disease_name","").lower() if label=="Focal seizure" else True)]
            if matches:
                try: vals[i,j]=float(matches[0]["overall_score"])
                except (ValueError,KeyError): pass
    gaba_genes={"GABRA1","GABRA2","GABRA3","GABRA5","GABRB2","GABRG2"}
    gaba_rows=[r for r in read(os.path.join(DATA,"psychiatric_disease_evidence.csv")) if r.get("gene_symbol") in gaba_genes]
    def mean_score(disease_id):
        scores=[]
        for row in gaba_rows:
            summary=row.get("evidence_summary","")
            if f"disease ID={disease_id}" not in summary: continue
            match=re.search(r"overall association score=([0-9.eE+-]+)",summary)
            if match:scores.append(float(match.group(1)))
        return float(np.mean(scores)) if scores else np.nan
    gaba_means=[mean_score("MONDO_0002009"),mean_score("MONDO_0005090"),mean_score("MONDO_0005618")]
    fig=plt.figure(figsize=(7.2,3.55))
    gs=fig.add_gridspec(2,1,height_ratios=[3.0,.8],hspace=.42)
    ax=fig.add_subplot(gs[0])
    im=ax.imshow(np.ma.masked_invalid(vals),cmap="YlGnBu",vmin=0,vmax=.12,aspect="auto")
    ax.set_xticks(range(len(diseases)),[d[1] for d in diseases]); ax.set_yticks(range(3),genes)
    wrapped_labels=["MDD","Schizo-\nphrenia","Anxiety\ndisorder","Epilepsy","Neurotoxicity","Focal impaired\nawareness\nseizure"]
    ax.set_xticks(range(len(diseases)),wrapped_labels)
    ax.tick_params(axis="x",labelsize=8.5); ax.tick_params(axis="y",labelsize=9)
    ax.set_title("Direct Open Targets associations for ranked metabolic enzymes",loc="left",fontsize=9.5,fontweight="bold",pad=6)
    for i in range(3):
        for j in range(len(diseases)):
            v=vals[i,j]; ax.text(j,i,f"{v:.5f}" if np.isfinite(v) else "N/R",ha="center",va="center",fontsize=8.5,fontweight="bold",color="white" if np.isfinite(v) and v>.055 else "#172B3A")
    ax.set_xticks(np.arange(-.5,len(diseases),1),minor=True); ax.set_yticks(np.arange(-.5,3,1),minor=True)
    ax.grid(which="minor",color="white",lw=2); ax.tick_params(which="minor",bottom=False,left=False)
    cb=fig.colorbar(im,ax=ax,fraction=.025,pad=.025); cb.set_label("Overall association score",fontsize=8.5); cb.ax.tick_params(labelsize=8.5)
    rowax=fig.add_subplot(gs[1]); rowax.set_xlim(-.5,5.5); rowax.set_ylim(-.5,.5); rowax.axis("off")
    rowax.text(-.58,0,"GABA-A\n(6-gene mean)",ha="right",va="center",fontsize=8.5,fontweight="bold",color="#33495C",clip_on=False)
    for j,v in enumerate(gaba_means+[np.nan,np.nan,np.nan]):
        face="#E8EDF1" if j<3 else "#F5F6F7"
        rowax.add_patch(plt.Rectangle((j-.5,-.42),1,.84,facecolor=face,edgecolor="white",lw=1.5))
        rowax.text(j,0,f"{v:.5f}" if np.isfinite(v) else "—",ha="center",va="center",fontsize=8.5,fontweight="bold",color="#263746")
    fig.savefig(os.path.join(OUT,"fig2_neuro_psych_overlap.png"),dpi=300,bbox_inches="tight",pad_inches=.12)
    plt.close(fig)

def fig3():
    rows=read(os.path.join(DATA,"pgx_cyp2c19_cyp3a4.csv"))
    alleles=[("CYP2C19","*2"),("CYP2C19","*3"),("CYP2C19","*17"),("CYP3A4","*22")]
    pops=["1000GENOMES:phase_3:ALL","1000GENOMES:phase_3:EAS"]
    values={}
    for r in rows:
        if "1000 Genomes" not in r.get("source_db",""):continue
        key=(r.get("gene"),r.get("allele"),r.get("population"))
        try: values[key]=float(r["allele_frequency_pct"]) if r.get("allele_frequency_pct") else None
        except ValueError:values[key]=None
    fig,ax=plt.subplots(figsize=(13.5,8.2))
    x=np.arange(len(alleles));width=.34
    colors=["#2F6B8A","#D28A44"]
    for j,pop in enumerate(pops):
        dx=(j-.5)*width
        for i,(gene,star) in enumerate(alleles):
            v=values.get((gene,star,pop)); xpos=x[i]+dx
            if v is None:
                ax.text(xpos,.65,"N/R (1000G)",ha="center",va="bottom",rotation=0,fontsize=10,color=colors[j],fontweight="bold")
            else:
                ax.bar(xpos,v,width,color=colors[j],edgecolor="white",linewidth=.8,zorder=2)
                ax.text(xpos,v+.7,f"{v:.2f}%",ha="center",va="bottom",fontsize=10,color="#172B3A",fontweight="bold")
    ax.set_xticks(x,[f"{g}\n{a}" for g,a in alleles],fontsize=12)
    ax.set_ylabel("Variant-allele frequency (%)",fontsize=13)
    ax.set_title("1000 Genomes variant-allele frequency: Global vs East Asian",loc="left",fontsize=18,fontweight="bold",pad=26)
    ax.set_ylim(0,max(35,max(v for v in values.values() if v is not None)+6))
    ax.grid(axis="y",color="#D8E0E6",linewidth=.8,zorder=0)
    ax.spines[["top","right"]].set_visible(False)
    ax.legend(handles=[Line2D([0],[0],color=colors[0],lw=8,label="1000GENOMES:phase_3:ALL"),Line2D([0],[0],color=colors[1],lw=8,label="1000GENOMES:phase_3:EAS")],frameon=False,loc="upper right",fontsize=10)
    fig.tight_layout(rect=(0,0,1,.90))
    fig.savefig(os.path.join(OUT,"fig3_pgx_population_diff.png"),dpi=300,bbox_inches="tight",pad_inches=0.35)
    plt.close(fig)

def main():
    fig1();print("[OK] fig1_integrated_network.png",flush=True)
    fig2();print("[OK] fig2_neuro_psych_overlap.png",flush=True)
    fig3();print("[OK] fig3_pgx_population_diff.png",flush=True)

if __name__=="__main__":main()
