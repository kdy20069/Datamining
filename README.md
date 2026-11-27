# Data Mining Final Project

Evidence-bounded assessment of three insecticides (Permethrin, Prallethrin, PBO) and two INCB Schedule IV benzodiazepines (Diazepam, Alprazolam), integrating shared metabolism, GABA-A target evidence, AOP 10 / AO 613 context, psychiatric associations, and pharmacogenomic population frequencies.

## Repository Structure
- `data/`: Retained database extracts and provenance boundary (`SOURCE_PROVENANCE.md`).
- `experiment/`: Unified evidence table (`evidence_table.csv`), ranked pair matrix (`pair_matrix_2x3.csv`), gene overlap summary (`gene_overlap_summary.csv`), and reproducible analysis/figure scripts.
- `skill/evidence-report/SKILL.md` (mirrored in `.agents/skills/evidence-report/SKILL.md`): Reproducible report-writing and verification skill.
- `report/`: Final English report source (`Final_Report.md`) and generated PDF / DOCX.

## Reproducing the Ranked Matrix and Figures

The pair matrix classifies observed evidence as curated database/verified bioassay records or peer-reviewed records with a verified PMID, and keeps inferred links separate. The three current report figures are: an integrated observed/inferred network plus 3×2 observed shared-node matrix, Open Targets psychiatric association scores for six GABA-A subunits, and Ensembl 1000 Genomes Global vs EAS variant frequencies (including N/R for CYP3A4*22 EAS).

```bash
pip install -r requirements.txt
python3 experiment/build_ranked_matrix.py
python3 experiment/build_evidence_figures.py
```

Outputs: `experiment/pair_matrix_2x3.csv`, `experiment/gene_overlap_summary.csv`, `experiment/fig1_integrated_network.png`, `experiment/fig2_neuro_psych_overlap.png`, and `experiment/fig3_pgx_population_diff.png`. Figure generation uses Matplotlib; run with an environment that has Matplotlib and NumPy installed.

## Building the Report

After generating the three figures, build the PDF and editable DOCX from the unchanged Markdown source:

```bash
python3 report/build_report.py
```

The script reads `report/Final_Report.md` and writes `report/Final_Report.pdf` and `report/Final_Report.docx`.
