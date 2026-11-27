---
name: evidence-report
description: Audit retained evidence and experiment artifacts in this Data Mining final project repository, then produce a concise, reproducible English final report.
---

# Evidence Report: Writing, Audit, and Reproduction Rules

## 1. Evidence Boundary and Claim Discipline

- Treat `data/SOURCE_PROVENANCE.md`, retained files under `data/`, and `experiment/evidence_table.csv` as the evidence boundary. Every number, label, date, and missing value must be traceable to a retained record. Never infer a missing count, score, frequency, PMID, assay call, or date.

- Define **observed** as a curated database record, a verified bioassay record, or a peer-reviewed record with a verified PMID. Mark analyst synthesis, network-neighbor propagation, and unverified pathway bridges as **inferred**.

- Distinguish a missing record from a zero biological effect. For Open Targets, report the disease ID and exact returned disease name; do not conflate related terms or IDs.

- Keep the Permethrin direction consistent: CTD / PMID 24548679 records CYP2C19 and CYP3A4 as increasing Permethrin metabolism, a substrate/metabolism relationship. Do not describe this as CYP induction or inhibition.

- Use source retrieval dates, not filesystem modification times. Every cited source must have a direct URL, relevant record or query scope, local file path, and retrieval/check date in the report or its references.

## 2. Length, Language, and Compression

- Write the full report in English and target **exactly four pages**; allow a fifth page only when necessary for legible figures or references, and never exceed five pages. Compress repeated prose and avoid redundant tables.

- Use the exact title hyphenation **Insecticide–Benzodiazepine** (en dash).

- Table 1 must have exactly these four columns: `Database / Source`, `Evidence Scope`, `Retained Records`, and `Retrieval / Provenance Date`. Do not add `Local file` or `Source URL` columns. Use concise scope/count statements and put paths and URLs in captions, body citations, or References.

- Summarize the 18 Open Targets GABA-A scores and the PGx frequencies in their figures. In prose, give the main pattern and only the most useful maximum or comparison; do not reproduce all plotted numbers as bullets.

- Place these caveats together exactly once in Section 6: the ranking is not a clinical interaction prediction; no mixed-exposure empirical data are available and Bliss classification is unavailable; population frequency is not individual risk; Open Targets scores are not causal evidence. Do not repeat these caveats elsewhere. Section 2 may include the specifically required hypothesis counterpoint without restating the Section 6 caveat list.

- Keep ClinicalTrials.gov and INCB to one short background sentence each. Do not include legacy haloperidol LINCS or TCGA figures.

## 3. Required Report Structure and Content

Use these sections in this order.

### `## 1. Study Scope and Databases`

- Begin with 1–2 sentences explaining why the five candidates were selected: three insecticides (Permethrin, Prallethrin, PBO) and two INCB Schedule IV benzodiazepines (Diazepam, Alprazolam), for a shared-metabolism / GABA-A evidence screen.

- Include compact Table 1 using only the required four columns. Include every source used: CTD, PubChem, ChEMBL, UniProt, Ensembl / 1000 Genomes, Open Targets, KEGG Drug, PMID literature, STRING, AOP-Wiki, INCB, ClinicalTrials.gov, and GEO / PMID 40253403 as applicable. Show the actual retained scope and status; do not imply a failed query succeeded.

- For PubChem, state that the seven unique AIDs were checked through PUG-REST on 2026-11-27 and all returned one assay summary record. For ChEMBL, UniProt, Ensembl, Open Targets, and KEGG Drug, use the verified 2026-11-27 live-query date and report retained results or failures from their audit records.

- CTD dates must remain unambiguous in Table 1, body, Section 6, and References. The 33-gene Neurotoxicity Syndromes file is a **local extract with retrieval date exactly `Local extract (original query date unrecorded)`**. The CTD live recheck was attempted on 2026-11-27 and failed / yielded no parseable disease-gene result; never assign that live date to the 33 local rows. The Permethrin CTD interaction direction is supported by retained PMID-linked local evidence, not a successful 2026-11-27 CTD API response.

- Cite ClinicalTrials.gov and INCB in one background sentence apiece, not as primary interaction evidence.

### `## 2. Evidence Integration and Ranked Pair Matrix`

- State the observed definition and say that shared-node count is a screening heuristic. Cite `experiment/pair_matrix_2x3.csv` and use one 3-insecticide × 2-benzodiazepine table; separate observed and inferred nodes/counts.

- Use the `observed_rank` field as the joint evidence rank. **Permethrin × Diazepam and Prallethrin × Diazepam are both Joint Rank 1 (Tied 1), each with two observed shared nodes: CYP2C19 and CYP3A4.** Do not describe Prallethrin × Diazepam as a unique rank 2. State that the ordering preference for PMID support before bioassay support is an analyst-defined tie-break, not an additional observed measurement.

- Include a 2–3 sentence, explicitly labeled **hypothesis** paragraph: treating Permethrin and Prallethrin as sharing CYP2C19/CYP3A4 substrate routes, concurrent exposure could create metabolic competition and alter clearance. Counterbalance it in one sentence: retained in-vitro assay records, including Prallethrin records with species listed as Unknown, do not establish substrate competition, inhibition, or synergy at relevant human exposure levels.

- Include this heuristic limitation and alternative in one sentence: shared-node count ignores direction (substrate versus inhibitor), so PBO—despite CYP3A4 activity/inhibition assay signals—falls in the tied fourth-place group; mechanistically, PBO × benzodiazepine is an alternative candidate for follow-up.

- Preserve the mixed PBO–CYP3A4 calls exactly: 501.2 nM Potency has one Active and one Not Active record, plus two 3000 nM IC50 records. Describe these as retained assay records; do not collapse them into one active claim.

- Label POR as an inferred STRING CYP3A4–POR network-neighbor relationship, not direct compound–POR evidence. Do not repeat the Section 6 caveat list here.

### `## 3. Integrated Mechanism and AOP Context`

- Insert only `../experiment/fig1_integrated_network.png`. Figure 1 is a single integrated network; do not add the former right-side heatmap or duplicate Table 2.

- State briefly that solid links are observed and dashed links are inferred or unreported. Follow `experiment/evidence_table.csv`; identify the missing KE669→KE682 KER continuity as unreported, not observed. Name `experiment/build_evidence_figures.py` in the caption or adjacent text.

### `## 4. Bonus 1: Psychiatric Disease Association`

- Insert `../experiment/fig2_neuro_psych_overlap.png`; cite `experiment/gene_overlap_summary.csv`, `data/psychiatric_disease_evidence.csv`, and `data/psychiatric_cyp_check.csv`.

- Report the exact-symbol result as **0/9**: the 33-gene CTD local extract (MeSH `MESH:D020258`) has zero exact-symbol matches to the nine candidate targets. Call it a local-extract intersection, not a live CTD result; retain the exact CTD provenance label above.

- Report **18 observed GABA-A gene–disease pairs** across MDD (`MONDO_0002009`), schizophrenia (`MONDO_0005090`), and anxiety disorder (`MONDO_0005618`). Explain in one sentence that similar MDD/anxiety scores around 0.61 coincide with a shared, near-saturated `clinical_precedence` component (~0.995–0.997); no `known_drug` component appeared in the 18 returned arrays, and GABRA1’s higher MDD score includes genetic-association evidence. Do not list all 18 scores in prose.

- Summarize the direct CYP/POR lookups with disease IDs and names kept distinct. Verified examples include CYP3A4 MDD 0.02670, epilepsy 0.02119, and neurotoxicity (`EFO_0011057`) 0.00776; CYP2C19 MDD 0.09820 and epilepsy 0.04821; the 0.00148 CYP2C19 result is **focal impaired awareness seizure** (`HP_0002384`), not the generic seizure row (0.02870). POR MDD is 0.00776 and epilepsy 0.00277; POR also has a broad anxiety record (`MONDO_0011918`, 0.00294), while the exact anxiety-disorder ID (`MONDO_0005618`) was not returned. Cite `data/psychiatric_cyp_check.csv` and report the returned associations descriptively.

- The complete direct disease lists contained 802 CYP3A4, 536 CYP2C19, and 540 POR associations across pages 0 and 1. None contained exact MeSH `MESH:D020258`; CYP2C19 and POR also had no neurotoxicity-named record in their complete lists. Describe this as no matching Open Targets record in the complete returned lists, not biological absence.

- State the GSE208338 audit in one sentence only: the DEG CSV has zero data rows and cannot be recomputed because the expression matrix, sample metadata, and DEG script are absent.

### `## 5. Bonus 2: Pharmacogenomic Population Frequencies`

- Insert `../experiment/fig3_pgx_population_diff.png` and cite `data/pgx_cyp2c19_cyp3a4.csv`.

- Summarize in 2–3 sentences, not a repeated bullet list: the largest EAS frequency is `CYP2C19*2` at 31.25% versus 22.14% Global; `CYP2C19*17` shows the reverse population pattern; `CYP3A4*22` is 1.50% Global and **N/R (1000G)** for EAS. Keep each star-allele name in inline code, including `CYP2C19*2`, `CYP2C19*3`, `CYP2C19*17`, and `CYP3A4*22` wherever they appear. Never convert N/R to 0%.

- Do not include work-history explanations such as “previously copied from an identified local evidence-table row and marked unverified there.” Attribute the Global `CYP3A4*22` value to the retained Ensembl variation API response (`rs35599367`, `pops=1`, retrieval 2026-11-27). Describe Diazepam metabolism only to the extent supported by retained KEGG Drug / PMID records.

### `## 6. Limitations and Process Audit`

- In Section 6 only, state these four caveats together exactly once: “not a clinical interaction prediction”; “no mixed-exposure empirical data / Bliss unavailable”; “population frequency is not individual risk”; “Open Targets scores are not causal evidence.” Do not repeat these caveat statements in Sections 2, 4, or 5. Section 2 may retain only its single required hypothesis counterpoint sentence.

- Record process gaps concisely: CTD live recheck failed on 2026-11-27, while its 33-row gene set remains `Local extract (original query date unrecorded)`; GSE208338 DEG recomputation inputs are absent; CYP3A4*22 EAS is N/R (1000G). Do not say the CTD overlap is omitted or unreportable—the local exact intersection is 0/9 and must be reported in Section 4.

### `## Reproducibility Metadata`

- Keep this to a few lines: coding environment/agent **OpenCode**, model **Solar Pro 4**, report date **2026-11-27**, and scripts `experiment/build_ranked_matrix.py` and `experiment/build_evidence_figures.py`.

- The `Prompt` field must contain the exact English prompt actually entered into Solar Pro 4, verbatim from a retained prompt/log. Do not replace it with a summary or reconstruct it from this skill. If the original prompt is not retained, state exactly: `Original Solar Pro 4 prompt not retained; verbatim prompt cannot be recovered.`

### `## References`

- End with `## References`. Include all sources actually used: STRING v12.5; AOP-Wiki (AOP 10, KE 64, AO 613); PubChem PUG-REST; CTD; ChEMBL; UniProt; Ensembl / 1000 Genomes; Open Targets; KEGG Drug; INCB; ClinicalTrials.gov; and GEO / PMID 40253403.

- Give each reference a direct URL, relevant scope/identifier, retrieval or check date, and repository-relative local path with its directory prefix (`data/...` or `experiment/...`). Do not use absolute local paths. Keep Table 1 free of URL/path columns and do not duplicate long identifier inventories or PubChem AIDs across references.

- References 5 (UniProt) and 8 (KEGG Drug) must use the local path `data/expanded_db_evidence.csv`.

- CTD references must distinguish the live-query attempt (2026-11-27; failed / no parseable gene result) from the 33-row local gene extract (`Local extract (original query date unrecorded)`). Apply the exact local-extract wording in Table 1, Section 4, Section 6, and References.

- Reference 1 must say **“CYP2C19 and CYP3A4 increase Permethrin metabolism (PMID 24548679)”** with the correct direction. Include STRING v12.5 CYP3A4–POR combined score 0.979, `https://string-db.org/`, local `experiment/evidence_table.csv`, checked 2026-11-06. Include AOP-Wiki URLs `https://aopwiki.org/aops/10`, `https://aopwiki.org/events/64`, and `https://aopwiki.org/events/613`, local `experiment/evidence_table.csv`, checked 2026-11-22 / 2026-11-23.

## 4. Tables, Figures, and Reproduction

- Use `experiment/pair_matrix_2x3.csv`, `experiment/gene_overlap_summary.csv`, `data/psychiatric_disease_evidence.csv`, `data/psychiatric_cyp_check.csv`, `data/pubchem_aids.csv`, and `data/pgx_cyp2c19_cyp3a4.csv` as the authoritative retained tables for their respective claims.

- Insert exactly these three figures, each near its first interpretation:

  1. `../experiment/fig1_integrated_network.png`
  2. `../experiment/fig2_neuro_psych_overlap.png`
  3. `../experiment/fig3_pgx_population_diff.png`

- Name `experiment/build_ranked_matrix.py` and `experiment/build_evidence_figures.py` near the generated tables/figures. Confirm the PNGs and source CSVs exist before delivery. Do not use legacy substitutes.

- Keep observed and inferred links visually distinct and missing data visibly missing (for example, `N/R (1000G)`). Never turn absent rows into zero values.

## 5. Final Audit and Scope Control

- Before delivering a requested report, check that it is English, exactly four pages if feasible (five maximum), has all required sections, uses the four-column Table 1, contains only the three current figures, preserves the joint rank and tie-break distinction, applies CTD provenance consistently, formats all star alleles in code, uses no LaTeX `$...$`, includes all required references, and ends with `## References`.

- Put a blank line before every Markdown bullet list, including nested lists.

- Do not modify `report/Final_Report.md` unless the user explicitly asks for that file to be edited. When the user requests only this skill or another preparatory artifact, edit only the requested artifact and its explicitly requested copy.
