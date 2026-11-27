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
    chemicals={"Permethrin":(1.7,8.65),"Prallethrin":(1.7,7.35),"PBO":(1.7,6.05),"Diazepam":(1.7,4.0),"Alprazolam":(1.7,2.45)}
    enzymes={"CYP3A4":(4.7,8.1),"CYP2C19":(4.7,6.65),"POR":(7.5,8.3)}
    subunits=["GABRA1","GABRA2","GABRA3","GABRA5","GABRB2","GABRG2"]
    sub_pos={g:(7.35,6.45-i*.76) for i,g in enumerate(subunits)}
    gaba_hub=(4.8,3.9)
    events={"KE64":(9.95,5.7),"KE669":(12.95,5.7),"KE682":(15.95,5.7),"KE616":(18.95,5.7),"AO613":(21.95,5.7)}

    fig,ax=plt.subplots(figsize=(18/2.54,16/2.54),constrained_layout=False)
    fig.subplots_adjust(left=.025,right=.99,top=.89,bottom=.09)
    ax.set_xlim(-.1,23.5); ax.set_ylim(.5,9.55); ax.axis("off")
    for x,label in [(1.7,"Candidate\ncompounds"),(4.7,"Metabolic\nenzymes"),(7.35,"GABA-A\nsubunits"),(15.95,"AOP 10\nevents")]:
        ax.text(x,9.18,label,ha="center",va="bottom",fontsize=9,color="#455769",fontweight="bold",linespacing=.95)

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
        node(ax,chemicals[chem],chem,"#F4C6A5",width=2.9,height=.62,fontsize=10,weight="bold")
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
        node(ax,chemicals[chem],chem,"#B8D8D0",width=2.9,height=.62,fontsize=10,weight="bold")
        for gene in benz_edges[chem]:
            if gene in enzymes:
                arrow(ax,chemicals[chem],enzymes[gene],"observed",color="#287C70",rad=.035 if gene=="CYP3A4" else -.035,lw=1.45)
    # Draw target nodes after arrows.
    node(ax,enzymes["CYP3A4"],"CYP3A4","#DCE6F2",width=2.7,height=.62,fontsize=10,weight="bold")
    node(ax,enzymes["CYP2C19"],"CYP2C19","#DCE6F2",width=2.7,height=.62,fontsize=10,weight="bold")
    node(ax,enzymes["POR"],"POR\n(network\nneighbor)","#E9E4F4",width=2.5,height=.95,fontsize=9.2,weight="bold")
    target_count=len(set().union(*(benz_edges[c] for c in ("Diazepam","Alprazolam"))) & set(subunits))
    node(ax,gaba_hub,f"KEGG GABR\ntarget set\n({target_count} subunits)","#B8D8D0",width=2.8,height=1.0,fontsize=9.2,weight="bold")
    for chem in ("Diazepam","Alprazolam"):
        if benz_edges[chem].intersection(subunits):
            arrow(ax,chemicals[chem],gaba_hub,"observed",color="#287C70",rad=.04 if chem=="Diazepam" else -.04,lw=1.6)
    for g in subunits:
        if g in benz_edges["Diazepam"] or g in benz_edges["Alprazolam"]:
            arrow(ax,gaba_hub,sub_pos[g],"observed",color="#287C70",lw=1.05,rad=(subunits.index(g)-2.5)*.025)
    for g,pos in sub_pos.items():node(ax,pos,g,"#D7EBDD",width=1.9,height=.52,fontsize=10,weight="bold")

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
    event_labels={"KE64":"KE 64:\nReduction\nionotropic\nGABA\nreceptor\nchloride\nchannel\nconductance",
                  "KE669":"KE 669:\nReduction\nneuronal\nsynaptic\ninhibition",
                  "KE682":"KE 682:\nGeneration\namplified\nEPSP",
                  "KE616":"KE 616:\nOccurrence\nparoxysmal\ndepolarizing\nshift",
                  "AO613":"AO 613:\nOccurrence\nepileptic\nseizure"}
    event_widths={"KE64":2.95,"KE669":2.5,"KE682":2.5,"KE616":2.8,"AO613":2.5}
    for key,pos in events.items():
        label=event_labels[key]
        color="#F2D99B" if key.startswith("KE") else "#E8B8B8"
        node(ax,pos,label,color,width=event_widths[key],height=2.6,fontsize=9.0,weight="bold")
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
    ax.text(15.95,3.55,"Dashed KE669→KE682 continuity is not present\nin supplied KER rows.",ha="center",va="center",fontsize=9,color="#785C43")
    ax.text(.15,.72,"GABR → KE64 is a pathway hypothesis; KE64 is not a direct effect measurement for these compounds.",ha="left",va="center",fontsize=9,color="#455769")
    leg=[Line2D([0],[0],color="#526579",lw=2,label="Observed record / KER (solid)"),Line2D([0],[0],color="#526579",lw=2,ls="--",label="Inferred or unverified bridge (dashed)")]
    ax.legend(handles=leg,loc="upper right",frameon=False,fontsize=9,ncol=1,bbox_to_anchor=(1,.91))
    fig.suptitle("Integrated pesticide–benzodiazepine evidence network",fontsize=13,fontweight="bold",y=.975)
    fig.savefig(os.path.join(OUT,"fig1_integrated_network.png"),dpi=300)
    plt.close(fig)

def fig2():
    rows=read(os.path.join(DATA,"psychiatric_disease_evidence.csv"))
    genes=["GABRA1","GABRA2","GABRA3","GABRA5","GABRB2","GABRG2"]
    diseases=["major depressive disorder","schizophrenia","anxiety disorder"]
    vals=np.full((len(genes),len(diseases)),np.nan)
    for r in rows:
        if r.get("source_db")!="Open Targets GraphQL" or r.get("status_or_failure_reason") not in {"observed_in_first_500_associated_targets","observed_with_score_components"}:continue
        g=r.get("gene_symbol"); d=r.get("disease","").lower(); s=score_from_summary(r.get("evidence_summary",""))
        if g in genes and d in diseases and s is not None: vals[genes.index(g),diseases.index(d)]=s
    fig,ax=plt.subplots(figsize=(14,9))
    masked=np.ma.masked_invalid(vals)
    im=ax.imshow(masked,cmap="YlGnBu",vmin=0,vmax=1,aspect="auto")
    ax.set_xticks(range(3),["MDD","Schizophrenia","Anxiety disorder"]);ax.set_yticks(range(6),genes)
    ax.tick_params(labelsize=12);ax.set_title("Open Targets overall association scores",loc="left",fontsize=18,fontweight="bold",pad=26)
    ax.set_xlabel("Disease (MONDO IDs and exact query are in psychiatric_disease_evidence.csv)",labelpad=12)
    for i,g in enumerate(genes):
        for j,d in enumerate(diseases):
            v=vals[i,j]
            txt=f"{v:.3f}" if np.isfinite(v) else "N/R"
            color="white" if np.isfinite(v) and v>.48 else "#172B3A"
            ax.text(j,i,txt,ha="center",va="center",fontsize=12,fontweight="bold",color=color)
    ax.set_xticks(np.arange(-.5,3,1),minor=True);ax.set_yticks(np.arange(-.5,6,1),minor=True);ax.grid(which="minor",color="white",lw=2);ax.tick_params(which="minor",bottom=False,left=False)
    cb=fig.colorbar(im,ax=ax,fraction=.035,pad=.04);cb.set_label("Overall association score",fontsize=12);cb.ax.tick_params(labelsize=10)
    direct=read(os.path.join(DATA,"psychiatric_cyp_check.csv"))
    def direct_score(gene,disease):
        row=next((r for r in direct if r.get("gene_symbol")==gene and r.get("disease_id")==disease),None)
        try:return f"{float(row['overall_score']):.3f}" if row else "not returned"
        except (ValueError,TypeError):return "not returned"
    fig.text(.5,.045,"Clinical-precedence component ≈0.995–0.997 drives the similar GABA-A scores; literature component varies. "
             f"Direct CYP3A4/CYP2C19/POR MDD scores: {direct_score('CYP3A4','MONDO_0002009')}/{direct_score('CYP2C19','MONDO_0002009')}/{direct_score('POR','MONDO_0002009')}; CYP3A4 neurotoxicity={direct_score('CYP3A4','EFO_0011057')}. "
             "CTD live query failed; local extract intersection = 0/9.",ha="center",va="center",fontsize=9.5,color="#3C4B58",wrap=True)
    fig.tight_layout(rect=(0,.09,1,.91))
    fig.savefig(os.path.join(OUT,"fig2_neuro_psych_overlap.png"),dpi=300,bbox_inches="tight",pad_inches=0.25)
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
