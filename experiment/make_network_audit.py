import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

rows = [
    ("STRING v12.5", "CYP3A4-POR", "CYP3A4", "9606.ENSP00000498939", "functional_association", "POR", "9606.ENSP00000419970", "Homo sapiens (9606)", "Full network >=0.700; 1st shell none", "combined=0.979 (fusion=0.899, text=0.649, exp=0.456, coexp=0.075); physical=0.597 (<0.700)", "observed", "string-db.org (checked 2026-11-06)"),
    ("KEGG", "hsa:1576->hsa00980", "CYP3A4", "hsa:1576 (NCBI:1576; UniProt:P08684)", "pathway_member", "Xenobiotic metabolism (P450)", "hsa00980", "Homo sapiens", "1 of 10 KEGG maps for CYP3A4 (B[a]P, naphthalene, NNK steps)", "present on map; prallethrin/PBO absent", "observed", "kegg.jp (checked 2026-11-06)"),
    ("KEGG COMPOUND", "C18510", "Prallethrin", "KEGG:C18510", "pathway_link_check", "KEGG Pathway", "NO_PATHWAY_LINK", "N/A", "Brite BR:br08007 (Pyrethroid insecticides)", "No Pathway field (coverage gap, != not metabolized)", "observed_gap", "kegg.jp (checked 2026-11-06)"),
    ("KEGG COMPOUND", "C18880", "Piperonyl butoxide (PBO)", "KEGG:C18880 (CAS:51-03-6; PubChem:124489552)", "pathway_link_check", "KEGG Pathway", "NO_PATHWAY_LINK", "N/A", "Brite BR:br08007 (Synergist)", "No Pathway field (coverage gap, != not metabolized)", "observed_gap", "kegg.jp (checked 2026-11-06)"),
    ("Reactome r98", "R-HSA-211948", "CYP3A4", "R-HSA-52639 (UniProt:P08684)", "catalyzes_reaction", "Loperamide -> DLOP", "R-HSA-211948 (Parent: R-HSA-211981)", "Homo sapiens", "ReviewStatus 5/5; CandidateSet R-HSA-3229233 (member CYP3A4)", "PMID:15365656 (human liver microsomes); context only", "observed", "reactome.org (checked 2026-11-06)"),
    ("Reactome r98", "NO_ENTRY_INSECTICIDE", "Prallethrin / PBO", "C18510 / C18880", "curated_reaction_check", "Reactome Reactions", "NO_ENTRY", "Homo sapiens", "Web & ContentService search", "No curated entry (coverage gap, != not metabolized)", "observed_gap", "reactome.org (checked 2026-11-06)"),
    ("cBioPortal / TCGA", "lihc_tcga_pan_can_atlas_2018", "CYP3A4", "Hugo:CYP3A4", "expression_in_cna_groups", "TCGA-LIHC tumors", "TCGA-LIHC (GDC phs000178)", "Homo sapiens", "Paired mRNA (RSEM) + CNA (GISTIC)", "n=361 paired samples (of 372); broad mRNA spread in diploid; tumor context != neurotoxicity", "observed", "cbioportal.org (checked 2026-11-06)"),
    ("ClinPGx", "PA130 / PA166157487", "CYP3A4", "PA130 (rs35599367 / CYP3A4*22)", "pgx_summary_annotation", "Quetiapine (PK context)", "Level 1A (Metabolism/PK)", "Homo sapiens", "Drug metabolism context; gnomAD v4 AF 3.172% all, 0.000% East Asian", "PK evidence != neurotoxicity; population AF != personal risk", "observed", "clinpgx.org (checked 2026-11-06)"),
    ("ClinPGx", "NO_PGX_INSECTICIDE", "Prallethrin / PBO", "C18510 / C18880", "pgx_annotation_check", "ClinPGx Curated Annotations", "NO_ANNOTATION", "Homo sapiens", "Prallethrin: no result; PBO: 0 curated annotations (lit hits only)", "No annotation != no risk", "observed_gap", "clinpgx.org (checked 2026-11-06)"),
    ("ClinicalTrials.gov", "NCT02288637", "Piperonyl butoxide (PBO)", "Intervention:PBO", "registered_trial_endpoint", "Malaria prevalence / EIR", "NCT02288637", "Homo sapiens (children 6m-14y)", "Randomized 2x2 factorial LLIN/IRS trial (n=3,840, Completed)", "hasResults=false; 12 PBO trials (11 malaria, 1 lice); NOT neurotoxicity", "observed_gap", "clinicaltrials.gov (checked 2026-11-06)"),
    ("INCB Green List", "Schedule_IV", "Alprazolam / Diazepam", "INCB IDS: PA 004 (CAS:28981-97-7; CID:2118) / PD 006 (CAS:439-14-5; CID:3016)", "controlled_psychotropic", "Benzodiazepines (Schedule IV)", "INCB_Green_List_36th", "Homo sapiens", "International psychotropic control list", "Schedule IV status", "observed", "INCB Green List, 36th edition (2025), Schedule IV, pp. 9-10: https://www.incb.org/incb/uploads/documents/Psychotropics/forms/greenlist/2026/2510307E.pdf (checked 2026-11-23)"),
    ("AOP-Wiki AOP 10", "KER 667", "KE 64: Reduction, ionotropic GABA receptor chloride channel conductance", "https://aopwiki.org/events/64", "key_event_relationship", "KE 669: Reduction, neuronal synaptic inhibition", "https://aopwiki.org/events/669", "Homo sapiens; cellular/neuron/brain context", "AOP 10; adjacent key events", "Evidence: High", "observed", "AOP-Wiki AOP 10 / KER 667 (Gong & Perkins; checked 2026-11-22/2026-11-23)"),
    ("AOP-Wiki AOP 10", "KER 684", "KE 682: Generation, amplified excitatory postsynaptic potential (EPSP)", "https://aopwiki.org/events/682", "key_event_relationship", "KE 616: Occurrence, a paroxysmal depolarizing shift", "https://aopwiki.org/events/616", "Homo sapiens; brain/neuron context", "AOP 10; adjacent key events", "Evidence: Moderate", "observed", "AOP-Wiki AOP 10 / KER 684 (Gong & Perkins; checked 2026-11-22/2026-11-23)"),
    ("AOP-Wiki AOP 10", "KER 630", "KE 616: Occurrence, a paroxysmal depolarizing shift", "https://aopwiki.org/events/616", "key_event_relationship", "AO 613: Occurrence, epileptic seizure", "https://aopwiki.org/events/613", "Homo sapiens; adult brain / individual", "AOP 10; adjacent key events", "Evidence: High", "observed", "AOP-Wiki AOP 10 / KER 630 (Gong & Perkins; checked 2026-11-22/2026-11-23)"),
    ("Analyst Hypothesis", "INFERRED_01", "Prallethrin / Permethrin / PBO", "Prallethrin CID:9839306; CYP3A4 GeneID:1576 AID:1671201 (Potency, Active, 8.8776 uM), AID:2283680 (AC50, Active, 2.84101 uM), AID:2283689 (AC50, Active, 4.63614 uM), AID:2283698 (AC50, Active, 14.0582 uM), AID:2284096 (AC50, Active, 7.59824 uM); CYP2C19 GeneID:1557 AID:2284395 (AC50, Active, 5.28977 uM); CTD PMID:24548679", "proposed_inhibition_link", "CYP3A4 / CYP2C19", "NCBI:1576 / NCBI:1557", "Homo sapiens", "Joined assay records (AssaySpecies: Unknown); CTD action: CYP3A4/CYP2C19 increases permethrin metabolism (Homo sapiens), PMID:24548679", "Inferred cross-dataset metabolic association; does not establish Prallethrin inhibition or an in-vivo interaction", "inferred", "PubChem CID: https://pubchem.ncbi.nlm.nih.gov/compound/9839306; AID:1671201 https://pubchem.ncbi.nlm.nih.gov/bioassay/1671201; AID:2283680 https://pubchem.ncbi.nlm.nih.gov/bioassay/2283680; AID:2283689 https://pubchem.ncbi.nlm.nih.gov/bioassay/2283689; AID:2283698 https://pubchem.ncbi.nlm.nih.gov/bioassay/2283698; AID:2284096 https://pubchem.ncbi.nlm.nih.gov/bioassay/2284096; AID:2284395 https://pubchem.ncbi.nlm.nih.gov/bioassay/2284395; CTD Chemical D026023 / PMID:24548679 https://pubmed.ncbi.nlm.nih.gov/24548679/; local IDs/locators reviewed 2026-11-23"),
    ("Analyst Hypothesis", "INFERRED_02", "Alprazolam / Diazepam", "CID:2118 / CID:3016", "proposed_clearance_convergence", "CYP3A4", "NCBI:1576", "Homo sapiens", "Alprazolam 4-hydroxylation as a CYP3A4 activity marker in hemodialysis patients with persistent inflammation; patient PK context, not direct interaction evidence", "Proposed shared-node interaction; PMID:22159869; DOI:10.1007/s00228-011-1163-8", "inferred", "PubMed PMID:22159869 https://pubmed.ncbi.nlm.nih.gov/22159869/; DOI:10.1007/s00228-011-1163-8 (checked 2026-11-23)"),
    ("Analyst Hypothesis", "INFERRED_03", "CYP3A4 metabolic bottleneck / MDD-LINCS context", "NCBI:1576; GSE208338; LINCSCP_22231", "proposed_toxicity_link", "AO 613: Occurrence, epileptic seizure (AOP 10)", "AOP 10 / https://aopwiki.org/aops/10", "Homo sapiens; adult brain / organism-level AO context", "Analyst-proposed CYP3A4 metabolic bottleneck and MDD/LINCS convergence to AO 613; AOP 10 checked 2026-11-22/2026-11-23. Registered prototypical stressors: picrotoxin, lindane, dieldrin, heptachlor, endosulfan, RDX, fipronil; Prallethrin, Permethrin, PBO, and Alprazolam are not registered stressors", "Inference only; no registered-stressor match or direct chemical-to-AOP evidence", "inferred", "Analyst interpretation using AOP-Wiki AOP 10: https://aopwiki.org/aops/10 (Gong & Perkins; checked 2026-11-22/2026-11-23)")
]

cols = ["source_db", "record_id", "source_node", "source_id", "relation", "target_node", "target_id", "species", "condition_or_scope", "value_unit_or_status", "link_type", "reference_or_date"]
df = pd.DataFrame(rows, columns=cols)
df.to_csv("evidence_table.csv", index=False)

fig, ax = plt.subplots(figsize=(13, 9))
ax.set_xlim(-0.5, 11.0)
ax.set_ylim(-3.0, 7.2)
ax.axis("off")

nodes = {
    "ClinicalTrials.gov\n(NCT02288637:\nMalaria only)": (1.2, 6.2, "#eeeeee", "#666666"),
    "Insecticides\n(Prallethrin C18510 /\nPBO C18880)": (1.2, 4.3, "#d9edf7", "#31708f"),
    "Psychotropics\n(Alprazolam CID:2118 /\nDiazepam CID:3016)": (1.2, 1.5, "#f2dede", "#a94442"),
    "CYP3A4\n(hsa:1576 / PA130 /\nP08684)": (5.3, 3.2, "#fcf8e3", "#8a6d3b"),
    "POR\n(ENSP...419970)": (5.3, 6.1, "#dff0d8", "#3c763d"),
    "KEGG hsa00980 /\nReactome R-HSA-211948": (9.3, 5.6, "#dff0d8", "#3c763d"),
    "ClinPGx CYP3A4*22\n(rs35599367, PK context)": (9.3, 3.2, "#e8daef", "#6c3483"),
    "CNS Neurotoxicity /\nMDD Context\n(GSE208338 / LINCS)": (9.3, 1.0, "#fdebd0", "#b9770e"),
}

for label, (x, y, fc, ec) in nodes.items():
    box = mpatches.FancyBboxPatch(
        (x - 1.25, y - 0.50), 2.5, 1.0,
        boxstyle="round,pad=0.06,rounding_size=0.15",
        facecolor=fc, edgecolor=ec, linewidth=1.8, zorder=3
    )
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#222222", zorder=4)

def draw_edge(p1, p2, style, color, label, offset=(0, 0.2), directed=True):
    arrowstyle = "-|>,head_width=0.35,head_length=0.55" if directed else "-"
    ax.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle=arrowstyle, linestyle=style, color=color, linewidth=2.0), zorder=2)
    mx, my = (p1[0] + p2[0]) / 2 + offset[0], (p1[1] + p2[1]) / 2 + offset[1]
    ax.text(mx, my, label, ha="center", va="center", fontsize=7.8, color=color,
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.9), zorder=5)

draw_edge((5.3, 3.78), (5.3, 5.52), "-", "#2e7d32", "STRING 0.979\n(phys 0.597)", offset=(-0.95, 0.0), directed=True)
draw_edge((6.62, 3.60), (8.00, 5.20), "-", "#2e7d32", "Curated pathway /\nreaction (loperamide)", offset=(-0.15, 0.35), directed=True)
draw_edge((6.62, 3.20), (7.98, 3.20), "-", "#6c3483", "Level 1A PK\n(quetiapine)", offset=(0.0, 0.32), directed=True)
draw_edge((1.2, 4.88), (1.2, 5.62), "-", "#666666", "PBO LLIN trial\n(no neuro endpoint)", offset=(1.15, 0.0), directed=True)

draw_edge((2.52, 4.10), (3.98, 3.45), "--", "#c0392b", "Proposed inhibition\nAID 1671201 / 2284395; PMID 24548679", offset=(0.0, 0.38), directed=False)
draw_edge((2.52, 1.80), (3.98, 2.85), "--", "#c0392b", "Proposed clearance\nconvergence", offset=(0.0, -0.40), directed=False)
draw_edge((6.62, 2.75), (7.98, 1.35), "--", "#b9770e", "Inferred AOP 10: KE 616 → AO 613\n(no registered stressor link)", offset=(-0.15, -0.42), directed=False)

# AOP-Wiki curated KERs are shown as observed, directed links in a separate strip.
aop_nodes = [
    (0.9, "KE 64\n↓ GABA Cl⁻ conductance"),
    (3.0, "KE 669\n↓ synaptic inhibition"),
    (5.1, "KE 682\n↑ EPSP"),
    (7.2, "KE 616\nparoxysmal depolarizing shift"),
    (9.7, "AO 613\nepileptic seizure\n(adult brain)")
]
for x, label in aop_nodes:
    box = mpatches.FancyBboxPatch((x - 0.9, -2.55), 1.8, 0.95,
        boxstyle="round,pad=0.05,rounding_size=0.12", facecolor="#dff0d8",
        edgecolor="#3c763d", linewidth=1.5, zorder=3)
    ax.add_patch(box)
    ax.text(x, -2.075, label, ha="center", va="center", fontsize=7.2,
            fontweight="bold", color="#222222", zorder=4)
draw_edge((1.82, -2.075), (2.08, -2.075), "-", "#2e7d32", "KER 667 · High", offset=(0, 0.43))
draw_edge((6.02, -2.075), (6.28, -2.075), "-", "#2e7d32", "KER 684 · Moderate", offset=(0, 0.43))
draw_edge((8.12, -2.075), (8.78, -2.075), "-", "#2e7d32", "KER 630 · High", offset=(0, 0.43))

legend_elements = [
    Line2D([0], [0], color="#2e7d32", lw=2, linestyle="-", label="Observed DB record (solid, directed, verified ID)"),
    Line2D([0], [0], color="#666666", lw=2, linestyle="-", label="Observed non-neuro context / coverage gap (solid)"),
    Line2D([0], [0], color="#c0392b", lw=2, linestyle="--", label="Analyst-inferred link (dashed, requires confirmation)")
]
ax.legend(handles=legend_elements, loc="center left", bbox_to_anchor=(0.02, 0.27), frameon=True, fontsize=8.5)
ax.set_title("Shared-Node Evidence Network Around CYP3A4: Observed DB Links vs. Analyst-Inferred Links", fontsize=12.5, fontweight="bold", pad=10)

plt.tight_layout()
plt.savefig("network_audit_plot.png", dpi=300)
print("Done: evidence_table.csv and network_audit_plot.png saved.")
