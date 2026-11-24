---
name: evidence-report
description: Audit evidence tables and experiment artifacts in this Data Mining final project repository and generate a concise, reproducible English final report (<= 20 pages).
---

# Writing & Verification Rules

## 1. Strict Evidence & Traceability Gate
- **Stop if source IDs are missing:** Before drafting any claim, verify that every database record in `data/` and `experiment/` has a real record ID (e.g., PubChem CID, NCBI GeneID, KEGG ID, Reactome R-HSA ID, STRING ID, ClinPGx PA/rs ID, NCT ID, GEO GSE ID, LINCS signature ID, or AOP-Wiki ID) and check date.
- **No fabricated or unverified sources:** Never invent assay values, PMIDs, or database hits. Do not cite blogs or unverified websites; external literature must be peer-reviewed or from authoritative institutions with full citations.
- **Separate observation from inference:** Explicitly distinguish database-recorded facts (solid directed edges in diagrams) from analyst-proposed hypotheses (dashed undirected edges). Never treat coverage gaps ("no pathway link", "no entry", "no PGx annotation") as proof of "not metabolized" or "no risk". Never treat tumor expression (TCGA-LIHC) or malaria trial endpoints (NCT02288637) as neurotoxicity evidence.

## 1A. Provenance Boundary, Figure Eligibility & Claim Language
- Draft against `data/SOURCE_PROVENANCE.md` and `experiment/evidence_table.csv` as the controlling provenance boundary. Do not cite metadata that is no longer retained locally or cannot be restored, or empty files with no data rows (including the GSE208338 DEG file), as analysis results. Record them only in a limitations/process table.
- Include only figures whose generation has been confirmed from a Python script in `experiment/` (for example, `network_audit_plot.png`, `gene_overlap_venn.png`, `haloperidol_lincs_plot.png`, or `tcga_cyp3a4_plot.png` only when the corresponding script is verified). Exclude any image without a generator script in `experiment/`.
- Do not repeat uncited assertions from legacy hypothesis notes (e.g., “clearance is severely delayed” or “uniquely vulnerable”). Separate observed evidence from inference hypotheses and label each accordingly.

## 2. Artifact Linking
- Every table and figure in the report must explicitly reference its generating script or data file in `experiment/` or `data/` (e.g., `experiment/evidence_table.csv`, `experiment/network_audit_plot.png`, `experiment/assay_plot.png`, `experiment/haloperidol_lincs_plot.png`, `experiment/tcga_cyp3a4_plot.png`).
- Before finalizing, confirm that all figures and tables can be regenerated from scripts in `experiment/`.

## 3. Mandatory Report Structure (English ONLY, Max 20 Pages — Shorter Is Better)
Place tables and figures FIRST in each section, followed by only 1–2 concise sentences of interpretation. Enforce strict section page budgets (target total: 8–12 pages):

1. **Databases Used & Extracted Information (Max 2 pages):**
   - Present one compact summary table listing: Database, Research Question Answered, Extracted Record IDs & Scope, and Check Date. Do not just list database names.
2. **Cross-Database Integration Methodology (Max 2 pages):**
   - Include the connection map (`experiment/network_audit_plot.png`) showing exact joining keys (e.g., GeneID 1576 / UniProt P08684 / Ensembl ENSP00000498939 / PA130 / PubChem CIDs), species (`Homo sapiens`), conditions, and solid vs. dashed edge legend.
3. **Proposed Pair, Interaction Basis & Limits (Max 3 pages):**
   - State the candidate pair (e.g., Prallethrin/Permethrin/PBO + INCB Schedule IV Alprazolam/Diazepam).
   - Explain the primary interaction criterion: **high convergence on shared nodes** (e.g., CYP3A4 metabolic hub).
   - Address interaction types (additive, synergistic, antagonistic / Bliss independence concept) strictly as an advanced discussion while explicitly stating that current DB records alone cannot empirically classify the mixture type.
   - Present supporting evidence alongside counter-evidence, missingness, and inference limits.
4. **Authoritative External Literature & Process Audit (Max 2 pages):**
   - Summarize peer-reviewed / authoritative citations supporting CYP3A4 clearance and pyrethroid/PBO metabolism (only cite verified references present in the repo or verified PMIDs).
   - Include **one summary table** documenting: Attempted Method, Mistake/Issue Encountered, Lesson Learned, and Improvement Applied (e.g., LINCS/KEGG/Reactome/ClinPGx gaps, cBioPortal `skiprows=4` header parsing, separating functional vs. physical STRING scores, separating observed vs. inferred edges).
5. **Bonus Analysis — Psychiatric Disease Association & Individual Side-Effect Differences (Max 3 pages):**
   - **Psychiatric Disease Association:** 1 figure + 1 compact table linking MDD (`GSE208338`), LINCS (`LINCSCP_22231`), CTD disease literature, and ClinicalTrials.gov scope (explicitly noting NCT02288637 is malaria-only, not neurotoxicity).
   - **Individual Side-Effect Differences:** 1 figure + 1 compact table summarizing pharmacogenomic variation (`ClinPGx PA130`, `rs35599367` / `CYP3A4*22` Level 1A quetiapine PK context, gnomAD v4 frequencies) and TCGA-LIHC CYP3A4 mRNA spread within diploid samples (`n=361`), explicitly stating all inference limits (population AF != personal risk; tumor mRNA != neurotoxicity).
6. **Reproducibility Metadata (Max 1 page):**
   - Record the coding agent name, model version, exact prompt used, and date of report generation.

## 3A. Required Completion Rules for Shared-Node and Bonus Analyses
- **Shared-node interaction table:** Use `experiment/evidence_table.csv` to calculate shared-node counts for every candidate chemical pair. Report observed shared nodes and inferred shared nodes in separate columns, with node names/IDs and source row IDs. Apply the course rule explicitly: pairs connected to more shared nodes are considered more likely to interact as a screening heuristic. If a chemical has no direct observed link, report observed shared nodes as **0 (evidence gap)**; do not promote an inferred edge to observed. For PBO, report observed shared nodes as zero and label any CYP3A4 overlap as inferred only when an explicit inferred row supports it. State that current database records cannot classify Bliss independence, additivity, synergy, or antagonism.
- **Bonus 1 — psychiatric disease association:** Complete this section even when the conclusion is that an association was not established. Use one summary table and one figure, `experiment/haloperidol_lincs_plot.png`. The table must include locally retained GSE208338 metadata, LINCS `LINCSCP_22231`, the local CTD neurotoxicity/disease-gene table when present, and the ClinicalTrials.gov PBO search scope (12 records; distinguish malaria/lice scope from psychiatric or neurotoxicity endpoints). If the DEG file has zero data rows, state exactly: **“Not performed / No quantifiable DEG overlap (0 data rows in repository)”**. Do not invent overlap statistics. Distinguish psychiatric-disease evidence from neurotoxicity context and from liver-cell perturbation results.
- **Bonus 2 — individual side-effect differences:** Include one comparison summary table and one figure, `experiment/tcga_cyp3a4_plot.png`. Use only locally recorded values to compare ClinPGx CYP3A4 PA130 / rs35599367 / CYP3A4*22 Level 1A quetiapine pharmacokinetic annotation, the recorded gnomAD v4 frequency, absence of curated annotations for prallethrin/PBO, and TCGA-LIHC paired CYP3A4 mRNA/CNA distribution (n=361, including diploid samples). Include a row-specific inference limit for every comparison: population frequency is not individual risk; pharmacokinetics is not neurotoxicity; tumor mRNA is not neurotoxicity. Do not infer a person's side-effect probability from these population/tumor data.

## 4. Iteration Rule
- If the generated report has missing items, weak wording, or exceeds length budgets, do **not** hand-edit the report text; update this `SKILL.md` or the analysis scripts in `experiment/` and regenerate the report.
