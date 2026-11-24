import csv
import pathlib
import sys

sys.path.insert(0, "/Users/kdy20069/.geo_overlap_python")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib_venn import venn2


DATA_DIR = pathlib.Path("/Users/kdy20069/Downloads/Datamining/data")
CTD_FILE = DATA_DIR / "ctd_neurotoxicity_genes.csv"
MDD_FILE = DATA_DIR / "GSE208338_MDD_vs_Control_DEGs_log2FC_gt1_FDR_lt0.05.csv"
OUTPUT_FILE = pathlib.Path("/Users/kdy20069/gene_overlap_venn.png")


def load_symbols(path: pathlib.Path, column: str) -> set[str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if column not in (reader.fieldnames or []):
            raise ValueError(f"Missing {column!r} in {path}; columns: {reader.fieldnames}")
        return {
            row[column].strip().upper()
            for row in reader
            if row.get(column, "").strip()
        }


ctd = load_symbols(CTD_FILE, "GeneSymbol")
mdd = load_symbols(MDD_FILE, "Gene")
overlap = sorted(ctd & mdd)

print("Overlapping genes:", ", ".join(overlap) if overlap else "None")
print(f"Set sizes: CTD={len(ctd)}, MDD DEGs={len(mdd)}, overlap={len(overlap)}")

fig, ax = plt.subplots(figsize=(9, 6), facecolor="white")
venn2(
    [ctd, mdd],
    set_labels=(
        f"CTD neurotoxicity genes (n={len(ctd)})",
        f"GSE208338 MDD DEGs\n(log2FC > 1, FDR < 0.05; n={len(mdd)})",
    ),
    set_colors=("#4C78A8", "#F58518"),
    alpha=0.62,
    ax=ax,
    subset_label_formatter=lambda count: str(int(count)),
)
for label in ax.texts:
    label.set_fontsize(11)
    label.set_color("#222222")

ax.set_title(
    "Gene overlap: neurotoxicity targets and MDD DEGs",
    fontsize=15,
    fontweight="semibold",
    pad=18,
    color="#222222",
)
ax.text(
    0.5,
    -0.06,
    f"Shared gene symbols: {len(overlap)}",
    transform=ax.transAxes,
    ha="center",
    va="top",
    fontsize=11,
    color="#444444",
)
ax.set_axis_off()
fig.tight_layout()
fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight", facecolor="white")
print(f"Saved: {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size:,} bytes)")
