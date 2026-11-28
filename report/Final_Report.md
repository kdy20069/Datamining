# Evidence-Bounded Integrated Audit of a Candidate Insecticide–Benzodiazepine Combination

2026-11-28

## 1. Study Scope and Databases

Five compounds were selected for a focused, source-bounded audit: widely used pyrethroid/synergist insecticides (Permethrin, Prallethrin, piperonyl butoxide [PBO]) plus INCB Schedule IV benzodiazepines metabolized by CYP2C19/CYP3A4 (Diazepam, Alprazolam). Evidence was compiled from retained project databases and verified where possible against live source endpoints.

**Table 1.** Retained evidence sources and record scope.

| Database / Source | Evidence Scope | Retained Records | Date |
|---|---|---|---|
| CTD (local extract) | Permethrin CYP2C19/CYP3A4 interaction direction | 2 PMID-mapped rows | Undated local extract |
| PubMed / NCBI E-utilities (PMID 24548679) | Permethrin CYP2C19/CYP3A4 metabolism verification | 1 verified abstract result sentence | 2026-11-28 |
| PubChem (PUG-REST) | Prallethrin CYP2C19/CYP3A4 bioassay AIDs | 7 AIDs (2 CYP2C19 antagonist-type; 5 CYP3A4 [2 antagonist-type, 3 CLD gene-expression]) | 2026-11-28 |
| ChEMBL (activity + archived activity) | CYP3A4/CYP2C19 activity lookups; archived PBO CYP3A4 records | 4 archived PBO/CYP3A4 activity rows; timeout-limited lookups for other compound–target pairs | 2026-11-27 |
| UniProt (REST) | Reviewed human target identity for CYP3A4, CYP2C19, POR, and 6 GABA-A subunits | 9 entries (`P08684`, `P33261`, `P10510`, `P14867`, `P47869`, `P34903`, `P31644`, `P47870`, `P18507`) | 2026-11-27 |
| KEGG Drug (REST) | Diazepam and Alprazolam METABOLISM and TARGET fields | 5 observed curation rows | 2026-11-27 |
| Ensembl Variation / 1000 Genomes phase 3 | `CYP2C19*2`, `CYP2C19*3`, `CYP2C19*17`, `CYP3A4*22` population frequencies | 8 returned population/allele rows | 2026-11-27 |
| Open Targets GraphQL | Direct CYP3A4/CYP2C19/POR disease association scores; GABA-A psychiatric association scores | 47 CYP/POR rows; 19 GABA-A psychiatric rows | 2026-11-27 |
| INCB Green List (36th edition, 2025) | Alprazolam and Diazepam Schedule IV status | 1 controlled-psychotropic record | 2026-11-23 |
| ClinicalTrials.gov | PBO intervention trials; neurotoxicity-relevant endpoint screen | 1 worked example (NCT02288637) and coverage-gap note | 2026-11-27 |
| GEO (GSE208338, PMID 40253403) | MDD vs control candidate-panel statistics and DEG file status audit | 13-row candidate panel; DEG file header-only | 2026-11-23 / 2026-11-27 |
| STRING v12.5 | CYP3A4–POR functional association | 1 edge (combined score 0.979) | 2026-11-06 |
| AOP-Wiki (AOP 10) | KE 64, KE 669, KE 682, KE 616, AO 613 and retained KER rows | 3 KER rows (KER 667, KER 684, KER 630) | 2026-11-22 / 2026-11-23 |

CTD direction audit verification of PMID 24548679 was completed on 2026-11-28 and returned the abstract result: "Coincubation with the CYP inhibitor ketoconazole and time course experiments with liver microsomes and recombinant CYP2C19 and CYP3A4 indicated CYP-catalyzed stereoselective cleavage of the ester followed by 4-hydroxylation to 3,4' PBOH." CTD direction is recorded as enzyme-mediated metabolism, not induction or inhibition.

Prallethrin's seven PubChem AIDs are summarized as 2 CYP2C19 antagonist-type and 5 CYP3A4 [2 antagonist-type, 3 CLD gene-expression], with AC50/Potency values of 2.84–14.06 µM. Assay species is recorded as Unknown in the retained table, and human exposure concentrations have not been established. AID activity does not establish substrate status. Detailed AID rows are retained in `data/pubchem_aids.csv`.

## 2. Evidence Integration and Ranked Pair Matrix

In this report, **Observed** means a curated database record, a verified bioassay record, or a verified PMID-based finding that directly connects a compound to a target. **Inferred** means an analyst synthesis, a network-neighbor propagation, or an explicitly labeled inference that is not itself a direct compound–target observation. Shared-node counting is used only as a screening heuristic, and the heuristic does not distinguish substrate from inhibitor relationships.

Two distinct hypothesis statements are retained:

(a) Permethrin × Diazepam may involve CYP2C19/CYP3A4 substrate competition. CTD PMID 24548679 records CYP2C19 and CYP3A4 as contributors to permethrin metabolism, and KEGG Drug lists both enzymes in Diazepam metabolism. This pair is a plausible metabolic-competition candidate for follow-up, but the retained evidence is metabolic association, not a measured interaction.

(b) Prallethrin × Diazepam may involve diazepam metabolism inhibition or modulation associated with the 2.84–14.06 µM in-vitro assay activity. Prallethrin has seven PubChem AIDs across CYP2C19 and CYP3A4; the five CYP3A4 records include CLD gene-expression AC50/Potency values of 2.84–14.06 µM. The assay species is Unknown in the retained records, and human exposure concentrations have not been established, so this signal does not establish an in-vivo interaction.

The GABA-A connection exists only on the benzodiazepine side through KEGG receptor-target curation; no retained insecticide-side record establishes GABA-A action, so pharmacodynamic synergy is unsupported by the retained evidence.

PBO × cytochrome P450 evidence is preserved once here. PBO CYP3A4 records in `data/expanded_db_evidence.csv` include a 501.2 nM Potency row with one Active and one Not Active record, plus two 3000 nM IC50 records. These are mixed archived calls and are not collapsed into a single active claim. POR appears only as an inferred STRING CYP3A4–POR network neighbor.

**Table 2.** Ranked 2×3 insecticide–benzodiazepine pair matrix.

| Rank | Insecticide | Benzodiazepine | Observed shared nodes (count) | Inferred shared nodes (count) | Evidence type |
|---|---|---|---|---|---|
| 1 (tie) | Permethrin | Diazepam | CYP2C19; CYP3A4 (2) | POR (1) | PMID-supported: CYP2C19; CYP3A4; Bioassay-supported: — |
| 1 (tie) | Prallethrin | Diazepam | CYP2C19; CYP3A4 (2) | POR (1) | PMID-supported: —; Bioassay-supported: CYP2C19; CYP3A4 |
| 3 (tie) | Permethrin | Alprazolam | CYP3A4 (1) | POR (1) | PMID-supported: —; Bioassay-supported: — |
| 3 (tie) | PBO | Alprazolam | CYP3A4 (1) | POR (1) | PMID-supported: —; Bioassay-supported: CYP3A4 |
| 3 (tie) | PBO | Diazepam | CYP3A4 (1) | CYP2C19; POR (2) | PMID-supported: —; Bioassay-supported: CYP3A4 |
| 3 (tie) | Prallethrin | Alprazolam | CYP3A4 (1) | POR (1) | PMID-supported: —; Bioassay-supported: CYP3A4 |

The observed and inferred node lists are carried from `experiment/pair_matrix_2x3.csv`. Empty shared-node cells are represented as `—`. In Evidence type, PMID-supported and Bioassay-supported shared nodes are shown from the source fields; empty fields are shown as `—`, and no additional evidence is inferred.

PBO remains 3 (tie) despite its CYP3A4 activity/inhibition signals because the ranking is based on observed shared-node counts and the tie-break order in the source matrix, not on a single assay call. PBO × benzodiazepine is a mechanistic alternative candidate for follow-up. Where paired rows share an observed count, PMID support precedes bioassay support as a display tie-break; that ordering is a display convention, not a measurement.

## 3. Integrated Mechanism and AOP Context

![Figure 1. Integrated insecticide–benzodiazepine evidence network](experiment/fig1_integrated_network.png)

**Figure 1.** Integrated insecticide–benzodiazepine evidence network. Solid links are observed records or AOP KER rows; dashed links are inferred or unverified bridges. The figure is generated by `experiment/build_evidence_figures.py` from the retained CSVs. CYP3A4 and CYP2C19 are linked to Permethrin from CTD PMID 24548679 and to Prallethrin from PubChem AIDs; benzodiazepine-to-CYP edges use KEGG Drug METABOLISM curation, and GABA-A subunits reflect KEGG TARGET curation for Diazepam and Alprazolam. POR is shown as a network-neighbor inference from STRING.

The integrated network in Figure 1 places the three insecticides and two benzodiazepines against shared metabolic and receptor nodes, then links those nodes to AOP 10 concepts where retained rows allow it. The strongest retained metabolic links are Permethrin CYP2C19/CYP3A4 metabolism from CTD PMID 24548679 and Prallethrin CYP2C19/CYP3A4 assay activity from PubChem. Diazepam and Alprazolam carry KEGG Drug metabolism and receptor-target curation, including GABA-A subunit target sets.

The supplied AOP-Wiki rows include KER 667 (KE 64 → KE 669), KER 684 (KE 682 → KE 616), and KER 630 (KE 616 → AO 613). Those retained KER rows do not report KE 669 → KE 682 continuity. That missing step is therefore left as a dashed, unverified bridge in Figure 1 rather than represented as an observed relationship.

The GABA-A side is supported only for the benzodiazepines through KEGG TARGET curation. There is no retained insecticide-side evidence for ionotropic GABA-A action, so pharmacodynamic synergy is not supported here. The inferred GABA-A → KE 64 and CYP3A4 → KE 64 bridges in Figure 1 are analytic hypotheses, not measured effects.

## 4. Bonus 1: Psychiatric Disease Association

![Figure 2. Direct Open Targets associations for ranked metabolic enzymes](experiment/fig2_neuro_psych_overlap.png)

**Figure 2.** Direct Open Targets associations for ranked metabolic enzymes. The CYP/POR heatmap covers MDD, Schizophrenia, Anxiety disorder, Epilepsy, Neurotoxicity, and Focal impaired awareness seizure; the appended row is the six-gene GABA-A mean for MDD, Schizophrenia, and Anxiety disorder, with em dashes elsewhere. The CYP heatmap scale is 0–0.12. The GABA-A genes' MDD and anxiety scores are near 0.61, and their returned `clinical_precedence` component is near 0.995–0.997.

Section 4 uses the integrated Figure 2 and one concise GSE208338 limitation sentence. The DEG CSV `data/GSE208338_MDD_vs_Control_DEGs_log2FC_gt1_FDR_lt0.05.csv` has zero data rows, and recomputation is impossible because the expression matrix, sample metadata, and DEG script are absent from the retained files. The underlying five-decimal CYP/POR values are retained in `data/psychiatric_cyp_check.csv`.

## 5. Bonus 2: Pharmacogenomic Population Frequencies

The retained population-frequency evidence is summarized in prose. CYP2C19 is shared by both 1 (tie) pairs, so its allelic distribution is relevant to both top-ranked combinations. In the retained Ensembl/1000 Genomes rows, `CYP2C19*2` and `CYP2C19*3` are more frequent in the East Asian population than in the Global population: `CYP2C19*2` is 31.25% in East Asian versus 22.14% Global, and `CYP2C19*3` is 5.56% in East Asian versus 1.42% Global. `CYP2C19*17` is more frequent globally (15.32%) than in East Asian (1.49%).

`CYP3A4*22` is retained from `data/pgx_cyp2c19_cyp3a4.csv` with a Global frequency of 1.50% and no returned East Asian frequency; missing coverage is recorded as `N/R (1000G)`, not zero. The Global `CYP3A4*22` value is attributed to the Ensembl variation API record `rs35599367` (`pops=1`).

![Figure 3. 1000 Genomes variant-allele frequency for CYP2C19 and CYP3A4 star alleles](experiment/fig3_pgx_population_diff.png)

**Figure 3.** 1000 Genomes variant-allele frequency for CYP2C19 and CYP3A4 star alleles, comparing Global and East Asian populations.

## 6. Limitations and Process Audit

This audit is not a clinical interaction prediction. No mixed-exposure data are available, so Bliss-type combination assessment is unavailable. Population frequency is not individual risk. Open Targets scores are not causal evidence.

The complete Open Targets list sizes from `data/psychiatric_cyp_check.csv` are 802 for CYP3A4, 536 for CYP2C19, and 540 for POR. These are returned association-record counts, not biological proof of absence for any unlisted disease term.

The CTD 33-gene neurotoxicity set in `data/ctd_neurotoxicity_genes.csv` is an undated local extract, and its live recheck failed on 2026-11-27.

## Reproducibility Metadata

| Field | Value |
|---|---|
| Coding environment / agent | OpenCode |
| Model | Solar Pro 4 |
| Report date | 2026-11-28 |
| Ranking script | `experiment/build_ranked_matrix.py` |
| Figure script | `experiment/build_evidence_figures.py` |
| Prompt | Follow skill/evidence-report/SKILL.md to audit the retained files in data/ and experiment/ and generate the final English report at report/Final_Report.md. Include the required figures, tables, reproducibility metadata, and references. |

## References

1. Comparative Toxicogenomics Database (CTD). Permethrin chemical–gene interactions, chemical ID D026023; CYP2C19 GeneID 1557; CYP3A4 GeneID 1576; PMID 24548679. https://ctdbase.org/detail.go?type=chem&acc=D026023 — local extract `data/ctd_direction_audit.csv`, retrieval date 2026-11-28.
2. PubMed / NCBI E-utilities. PMID 24548679, "Evaluation of the stereoselective biotransformation of permethrin in human liver microsomes: contributions of cytochrome P450 monooxygenases to the formation of estrogenic metabolites." https://pubmed.ncbi.nlm.nih.gov/24548679/ — verified 2026-11-28 via https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=24548679&retmode=xml; abstract result sentence retained in `data/ctd_direction_audit.csv`.
3. PubChem PUG-REST. Prallethrin CID 9839306; AIDs 1671197, 2284395, 1671201, 2283680, 2283689, 2283698, 2284096. https://pubchem.ncbi.nlm.nih.gov/compound/9839306 — assay summary and concise-result verification 2026-11-28; retained in `data/pubchem_aids.csv`.
4. ChEMBL. CYP3A4 target CHEMBL340; CYP2C19 target CHEMBL3622; activity queries for Prallethrin CHEMBL1876311, Permethrin CHEMBL1525, PBO CHEMBL1201131, Alprazolam CHEMBL3095, Diazepam CHEMBL521. https://www.ebi.ac.uk/chembl/api/data/activity.json — 2026-11-27; archived PBO records retained in `data/expanded_db_evidence.csv`.
5. UniProt. Human reviewed entries: CYP3A4 P08684; CYP2C19 P33261; POR P10510; GABRA1 P14867; GABRA2 P47869; GABRA3 P34903; GABRA5 P31644; GABRB2 P47870; GABRG2 P18507. https://rest.uniprot.org/uniprotkb/P08684.json — 2026-11-27; accessions retained in `data/expanded_db_evidence.csv`.
6. Ensembl Variation API / 1000 Genomes phase 3. CYP2C19 rs4244285 (`CYP2C19*2`), rs4986893 (`CYP2C19*3`), rs12248560 (`CYP2C19*17`); CYP3A4 rs35599367 (`CYP3A4*22`). https://rest.ensembl.org/variation/human/rs35599367?pops=1 — 2026-11-27; retained in `data/pgx_cyp2c19_cyp3a4.csv`.
7. Open Targets GraphQL. Direct target associations for CYP3A4 ENSG00000160868, CYP2C19 ENSG00000165841, POR ENSG00000127948; GABA-A psychiatric associated targets for MDD MONDO_0002009, Schizophrenia MONDO_0005090, Anxiety disorder MONDO_0005618. https://api.platform.opentargets.org/api/v4/graphql — 2026-11-27; retained in `data/psychiatric_cyp_check.csv` and `data/psychiatric_disease_evidence.csv`.
8. KEGG Drug. Diazepam dr:D00293; Alprazolam dr:D00225; METABOLISM and TARGET field inspection. https://rest.kegg.jp/get/dr:D00293 — 2026-11-27; retained in `data/expanded_db_evidence.csv`.
9. INCB Green List, 36th edition (2025). Alprazolam PA 004 (Schedule IV); Diazepam PD 006 (Schedule IV). https://www.incb.org/incb/uploads/documents/Psychotropics/forms/greenlist/2026/2510307E.pdf — checked 2026-11-23; retained in `experiment/evidence_table.csv`.
10. ClinicalTrials.gov. PBO intervention trial NCT02288637. https://clinicaltrials.gov/study/NCT02288637 — checked 2026-11-27; evidence retained in `experiment/evidence_table.csv` and `experiment/clinpgx_clinicaltrials_evidence.txt`.
11. GEO / PubMed. GSE208338, platform GPL5188, PMID 40253403. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE208338 — metadata checked 2026-11-23; candidate panel and DEG file retained in `data/GSE208338_MDD_vs_Control_candidate_panel_stats.csv` and `data/GSE208338_MDD_vs_Control_DEGs_log2FC_gt1_FDR_lt0.05.csv`; PMID 40253403 https://pubmed.ncbi.nlm.nih.gov/40253403/.
12. STRING v12.5. CYP3A4–POR functional association, combined score 0.979. https://string-db.org/ — checked 2026-11-06; retained in `experiment/evidence_table.csv`.
13. AOP-Wiki. AOP 10 (https://aopwiki.org/aops/10); KE 64 (https://aopwiki.org/events/64), KE 669 (https://aopwiki.org/events/669), KE 682 (https://aopwiki.org/events/682), KE 616 (https://aopwiki.org/events/616), AO 613 (https://aopwiki.org/events/613); KER 667, KER 684, KER 630. https://aopwiki.org/aops/10 — checked 2026-11-22 / 2026-11-23; retained in `experiment/evidence_table.csv`.
