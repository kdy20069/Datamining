# Data Mining Final Project

Evidence-bounded assessment of a candidate insecticide (prallethrin, permethrin, PBO) and INCB Schedule IV benzodiazepine (alprazolam, diazepam) combination around CYP3A4 (NCBI GeneID 1576) and AOP 10 / AO 613 context.

## Repository Structure
- `data/`: Retained database extracts and provenance boundary (`SOURCE_PROVENANCE.md`).
- `experiment/`: Unified evidence table (`evidence_table.csv`), audit summary, and Python scripts to reproduce the three report figures (`make_network_audit.py`, `plot_lincs.py`, `plot_tcga_cyp3a4.py`).
- `skill/evidence-report/SKILL.md` (mirrored in `.agents/skills/evidence-report/SKILL.md`): Reproducible report-writing and verification skill.
- `report/`: Final English report (`Final_Report.pdf`, 6 pages; `Final_Report.md`).

## Reproducing Figures
```bash
pip install -r requirements.txt
cd experiment
python3 make_network_audit.py
python3 plot_lincs.py
python3 plot_tcga_cyp3a4.py
```
