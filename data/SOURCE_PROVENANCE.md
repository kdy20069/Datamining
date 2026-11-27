# Source provenance and audit notes

Provenance audit performed: **2026-11-23**. “Locator audit” means the local identifier and source URL fields were checked; it does not imply that every linked record or paper was independently re-reviewed. Source acquisition dates are reported only where preserved in the source artifact metadata.

| File / record set | Record identifiers and source | Date and status |
|---|---|---|
| `GSE208338_MDD_vs_Control_candidate_panel_stats.csv` | GEO Series **GSE208338**, platform **GPL5188**, paper **PMID 40253403**, DOI `10.1038/s41398-025-03366-8`; [GEO Series](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE208338), [PubMed](https://pubmed.ncbi.nlm.nih.gov/40253403/) | GEO metadata checked 2026-11-23. The GEO page describes postmortem human DLPFC, MDD n=24 and controls n=62. The 13-row candidate panel is a local derived table; its analysis script and original expression matrix are not present, so the statistics are not independently reproducible from this repository alone. |
| `GSE208338_MDD_vs_Control_DEGs_log2FC_gt1_FDR_lt0.05.csv` | Same GSE208338 / GPL5188 / PMID 40253403 source locators | Metadata locator added 2026-11-23. The file has **zero data rows**; it must not be cited as a populated DEG result. |
| `ctd_neurotoxicity_genes.csv` | 33 rows carry NCBI Gene IDs, MeSH disease ID `MESH:D020258`, per-row PubMed IDs/URLs, NCBI Gene URLs, and CTD Gene URLs | Locator-field completeness reviewed 2026-11-23. Original CTD extraction date/query is not embedded; the audit date is not represented as the original download date. |
| `chembl_availability_data.json` | ChEMBL compound IDs and CAS values; target scope includes **CHEMBL220** (human acetylcholinesterase) and **CHEMBL340** (CYP3A4). [ChEMBL API](https://www.ebi.ac.uk/chembl/api/data/), [CHEMBL220 cross-reference](https://pubchem.ncbi.nlm.nih.gov/protein/P22303), [CYP3A4 target/assay example](https://www.ebi.ac.uk/chembl/explore/assay/CHEMBL1103662) | The PBO target-query artifact `/Users/kdy20069/chembl_work/activities/Piperonyl_butoxide.json` has filesystem mtime 2026-09-09 12:44 KST; exact HTTP request time was not preserved. Original query scripts are outside this repository. Counts are returned activity-record counts, not counts of active effects or potency evidence. Peppermint oil was resolved to **CHEMBL2108758** through its [PubChem record](https://pubchem.ncbi.nlm.nih.gov/compound/PEPPERMINT%20OIL); 0/0 is scoped to the archived target-keyword activity query documented in `chembl_peppermint_oil_activity_snapshot.json`, not a general no-risk finding. |
| `Insecticide_Ingredient_Combinations_Classroom.xlsx` | Workbook properties identify creator “Classroom dataset,” title “Insecticide Ingredient Combinations,” and 111 Case IDs/CAS values | Workbook creation metadata: 2026-09-08; description says ingredient concentrations with direct product identifiers removed, classroom use only. No external publisher, publication, or source URL is present in the workbook; that original provenance cannot be recovered from this file. |
| `CTD_ixns_20260921021313.xlsx` | CTD chemical IDs, Gene IDs, PMIDs, species, and interaction text in 560 rows | Workbook metadata creation time 2026-09-21 06:13 KST; original CTD query/filter and exact source retrieval time are not recorded. Filename timestamp is not treated as proof of query time. |
| INCB Schedule IV record in `experiment/evidence_table.csv` | IDs **PA 004** (alprazolam) and **PD 006** (diazepam), with matching CAS numbers; [INCB Green List, 36th edition (2025)](https://www.incb.org/incb/uploads/documents/Psychotropics/forms/greenlist/2026/2510307E.pdf) | Official document and Schedule IV rows checked 2026-11-23. The older 2024 PDF was not retained as the evidence source because it is the 35th edition; the evidence table now points to the verified 36th edition. |

## ChEMBL activity snapshot for PBO

`experiment/chembl_pbo_cyp3a4_activities.csv` transcribes the four returned PBO/CYP3A4 records from the archived local JSON. The API locator is `molecule_chembl_id=CHEMBL1201131&target_chembl_id=CHEMBL340`; target **CHEMBL340** is CYP3A4 and **CHEMBL220** is human acetylcholinesterase. The saved JSON file timestamp is shown in each row; this is an artifact timestamp, not a proven server retrieval timestamp.

These four activity rows should not be described as four independent active findings: they include a `Not Active` call, two rows with the same ChEMBL `record_id`, and a 2015 tissue-based assay whose description discusses pig liver microsomes/general CYP activity. The source data support the presence of ChEMBL activity records in the query scope; interpretation requires assay-level review.

## Remaining source/provenance gaps

- `experiment/haloperidol_signature.csv` and `experiment/enrichr_top_pathways.csv`: `LINCSCP_22231` and stable pathway term IDs are now recorded, but no original LINCS/iLINCS request URL, raw response, or Enrichr request payload/run date was preserved. The pathway p-values remain inherited local values and have not been rerun.
- PubChem’s AID pages required a browser verification challenge during this audit; the six AID URLs in the evidence table are standard PubChem BioAssay locators, and their assay values are retained from the local `assays.csv`/`joined.csv` extracts. The URL locator pattern is documented by [PubChem BioAssays](https://pubchem.ncbi.nlm.nih.gov/docs/bioassays).
- `experiment/joined.csv` is generated by `experiment/join.py`; its source locators are retained in the output, but the CTD page could not be independently opened during this audit. It remains traceable by CTD Chemical ID `D026023`, Gene IDs, and PMID `24548679`.
- Several legacy PNGs (`pbo_cyp3a4_network*.png`, `chembl_ingredient_target_availability.png`, `cleaned_heatmap.png`, and `Code_Generated_Image.png`) have no matching generator among the scripts currently present in `experiment/`; their data source / original generation path remains unresolved.

## Additional evidence run (2026-11-27)

All new derived rows store `query`, `source_url`, and `retrieval_date=2026-11-27`. HTTP calls use a 10 second timeout and one attempt; endpoint errors are recorded in the output tables.

| File | Query | Source URL / provenance | Retrieval date |
|---|---|---|---|
| `ctd_direction_audit.csv` | Permethrin CTD interactions for CYP3A4 (1576) and CYP2C19 (1557), checked against PMID 24548679 | [CTD chemical D026023](https://ctdbase.org/detail.go?type=chem&acc=D026023); [PubMed 24548679](https://pubmed.ncbi.nlm.nih.gov/24548679/); local `experiment/ctd.csv` | 2026-11-27 |
| `chembl_today_query_log.json` | PBO/CHEMBL1201131, Permethrin/CHEMBL1525, Prallethrin/CHEMBL1876311 x CYP3A4/CHEMBL340, limit 20 | ChEMBL activity API URLs recorded per query | 2026-11-27 |
| `expanded_db_evidence.csv` | 5 named compounds x 9 fixed targets in limited ChEMBL activity lookups; PubChem compound summaries; one UniProt entry lookup per fixed target | PubChem PUG and ChEMBL/UniProt REST URLs stored on each row | 2026-11-27 |
| `psychiatric_disease_evidence.csv` | Local GSE208338 input audit; psychiatric API calls intentionally not sent because safe exact target lookups were unavailable | [GEO GSE208338](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE208338) | 2026-11-27 |
| `pgx_cyp2c19_cyp3a4.csv` | Curated star allele identifiers; CYP3A4*22 frequency copied from identified local evidence-table row and marked unverified today | ClinPGx variant URLs and local `experiment/evidence_table.csv` row 9; URLs/queries stored per row | 2026-11-27 |
| `ctd_neurotoxicity_gene_audit.csv` | Existing 33 CTD GeneSymbol/GeneID rows and NCBI Gene locators | NCBI Gene URL per row from `ctd_neurotoxicity_genes.csv` | 2026-11-27 |
| `pubchem_aids.csv` | Unique AIDs from local `experiment/assays.csv` | PubChem AID URL per row | 2026-11-27 |

## Additional evidence run (2026-11-27)

All new derived rows store `query`, `source_url`, and `retrieval_date=2026-11-27`. HTTP calls use a 10 second timeout and one attempt; endpoint errors are recorded in the output tables.

| File | Query | Source URL / provenance | Retrieval date |
|---|---|---|---|
| `ctd_direction_audit.csv` | Permethrin CTD interactions for CYP3A4 (1576) and CYP2C19 (1557), checked against PMID 24548679 | [CTD chemical D026023](https://ctdbase.org/detail.go?type=chem&acc=D026023); [PubMed 24548679](https://pubmed.ncbi.nlm.nih.gov/24548679/); local `experiment/ctd.csv` | 2026-11-27 |
| `chembl_today_query_log.json` | PBO/CHEMBL1201131, Permethrin/CHEMBL1525, Prallethrin/CHEMBL1876311 x CYP3A4/CHEMBL340, limit 20 | ChEMBL activity API URLs recorded per query | 2026-11-27 |
| `expanded_db_evidence.csv` | 5 named compounds x 9 fixed targets in limited ChEMBL activity lookups; PubChem compound summaries; one UniProt entry lookup per fixed target | PubChem PUG and ChEMBL/UniProt REST URLs stored on each row | 2026-11-27 |
| `psychiatric_disease_evidence.csv` | Local GSE208338 input audit; psychiatric API calls intentionally not sent because safe exact target lookups were unavailable | [GEO GSE208338](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE208338) | 2026-11-27 |
| `pgx_cyp2c19_cyp3a4.csv` | Curated star allele identifiers; CYP3A4*22 frequency copied from identified local evidence-table row and marked unverified today | ClinPGx variant URLs and local `experiment/evidence_table.csv` row 9; URLs/queries stored per row | 2026-11-27 |
| `ctd_neurotoxicity_gene_audit.csv` | Existing 33 CTD GeneSymbol/GeneID rows and NCBI Gene locators | NCBI Gene URL per row from `ctd_neurotoxicity_genes.csv` | 2026-11-27 |
| `pubchem_aids.csv` | Unique AIDs from local `experiment/assays.csv` | PubChem AID URL per row | 2026-11-27 |

## Missing-evidence supplement (2026-11-27)

| Output / query | Source URL | Retrieval date |
|---|---|---|
| `pgx_cyp2c19_cyp3a4.csv`: Ensembl variation populations for rs4244285, rs4986893, rs12248560, rs35599367 (`pops=1`) | Per-variant URL stored in each output row; endpoint [Ensembl variation API](https://rest.ensembl.org/documentation/info/variation_id) | 2026-11-27 |
| `psychiatric_disease_evidence.csv`: Open Targets associated targets for MDD MONDO_0002009, schizophrenia MONDO_0005090, anxiety disorder MONDO_0005618; exact candidate-symbol filter and first page | [Open Targets GraphQL](https://api.platform.opentargets.org/api/v4/graphql); GraphQL query string stored in rows; Ensembl symbol mapping endpoint `https://rest.ensembl.org/lookup/symbol/homo_sapiens` | 2026-11-27 |
| `psychiatric_disease_evidence.csv`: exact symbol set intersection with local 33-gene audit | `data/ctd_neurotoxicity_gene_audit.csv` | 2026-11-27 |
| `expanded_db_evidence.csv`: KEGG Drug TARGET/METABOLISM fields for Diazepam dr:D00293 and Alprazolam dr:D00225 | [KEGG REST API](https://rest.kegg.jp/get/dr:D00293), [Alprazolam](https://rest.kegg.jp/get/dr:D00225) | 2026-11-27 |
| `expanded_db_evidence.csv`: four PBO/CYP3A4 ChEMBL activity rows copied from archived local source with assay, standard type, value and units | [ChEMBL activity query](https://www.ebi.ac.uk/chembl/api/data/activity.json?molecule_chembl_id=CHEMBL1201131&target_chembl_id=CHEMBL340); source artifact `experiment/chembl_pbo_cyp3a4_activities.csv` | 2026-11-27 |

All new rows include a query, source URL and retrieval date. Ensembl frequencies are retained only when the requested population appears in the API response. Open Targets rows are positive returned candidate associations; absence from the first 500 rows is not treated as proof of no association. API failures are recorded with their reason.

## Live source recheck and score audit (2026-11-27)

All HTTP requests in this recheck used a **15-second timeout and one attempt**; no request was retried.

| Output | Query and source | Result / retrieval provenance |
|---|---|---|
| `ctd_neurotoxicity_live.csv` | CTD chemical D026023 interactions for GeneIDs 1576/1557; CTD disease MESH:D020258 genes; CTD chemical-gene and gene-disease report downloads | The CTD detail URLs returned HTTP 302 and the report requests did not yield parseable matching gene rows (one report header was not recognized; the other exceeded the parser's supported integer size). No live CTD interaction or disease-gene result is claimed. Each request URL, query, date, status and failure is recorded. The previous CTD rows remain local-only; their `retrieval_date` now reads **“Local extract (original query date unrecorded)”**. |
| `pubchem_aids.csv` | PUG-REST assay summary endpoint `https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{AID}/summary/JSON` for the seven unique local AIDs | All seven returned one assay summary record. `PUG_REST_URL`, `verification_retrieval_date=2026-11-27`, status, and response count are stored per row. The original assay-value rows remain local extracts; their original `retrieval_date` is explicitly marked “Local extract (original query date unrecorded)”. |
| `psychiatric_disease_evidence.csv` | Open Targets GraphQL, 6 GABA-A targets × MDD MONDO_0002009, schizophrenia MONDO_0005090, and anxiety MONDO_0005618; first 500 associated targets per disease | Returned overall scores plus `datatypeScores` and `datasourceScores` in each evidence summary. For MDD and anxiety, all six GABA-A targets have a near-saturated `clinical` / `clinical_precedence` component (~0.995–0.997); literature (`europepmc`) varies by target and is a notable source of score spread. No `known_drug` component occurs in the 18 returned component arrays. GABRA1's higher MDD score also includes a returned genetic-association / GWAS credible-set score. Thus the similar total scores coincide with a common, high clinical-precedence component; this describes the observed score components and does not assert causal effects. |
| `psychiatric_cyp_check.csv` | Direct `target(ensemblId) → associatedDiseases` lookups for CYP3A4 ENSG00000160868, CYP2C19 ENSG00000165841 and POR ENSG00000127948, pages 0 and 1 | The complete lists contained 802, 536 and 540 associations, respectively. CYP3A4 and CYP2C19 each returned direct MDD, schizophrenia, anxiety and epilepsy scores: CYP3A4 0.02670, 0.01509, 0.01180, 0.02119; CYP2C19 0.09820, 0.04788, 0.01557, 0.04821. CYP3A4 also returned EFO_0011057 “neurotoxicity” (0.00776); both CYP3A4 and CYP2C19 returned focal impaired awareness seizure (0.00148) in addition to their epilepsy associations. POR returned MDD 0.00776, schizophrenia 0.00924, epilepsy 0.00277 and seizure-related syndromic rows; its complete list had no anxiety or neurotoxicity-named row. None of the three complete lists contained exact MeSH `MESH:D020258`. These are counts of Open Targets associated-disease records, not biological proof of absence. Returned rows include component scores, query and URL. |

`experiment/gene_overlap_summary.csv` records the CTD fallback intersection from the 33-row local gene extract: 0 exact symbol matches among the nine candidates. It is explicitly labeled as local-only and not a live CTD result. `experiment/pair_matrix_2x3.csv` now separates the observed-count joint rank from deterministic evidence-source tie-break order. The three refreshed evidence figures are 300 dpi; Figure 1 is one network panel with no Table 2 heatmap duplicate and uses node, edge-label, and legend font sizes of at least 9 pt at the 18 cm figure width.
