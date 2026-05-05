"""
aggregate.py
------------
Merge NCBI gene/variant data and KEGG pathway data into a unified dataset
ready for analysis or inclusion in the final report.

Run after fetch_ncbi.py and fetch_kegg.py.

Outputs:
    data/processed/aggregate_summary.csv  — one row per gene with all info
    data/processed/aggregate_long.csv     — long-format gene × pathway × variant
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"


def main() -> None:
    genes = pd.read_csv(PROCESSED_DIR / "ncbi_genes.csv")
    variants = pd.read_csv(PROCESSED_DIR / "ncbi_variants.csv")
    pathways = pd.read_csv(PROCESSED_DIR / "kegg_pathways.csv")

    # Per-gene summary: counts of variants and pathways
    variant_counts = variants.groupby("gene_symbol").size().rename("n_pathogenic_variants")
    pathway_counts = pathways.groupby("gene_symbol").size().rename("n_pathways")

    summary = (
        genes
        .merge(variant_counts, on="gene_symbol", how="left")
        .merge(pathway_counts, on="gene_symbol", how="left")
        .fillna({"n_pathogenic_variants": 0, "n_pathways": 0})
    )
    summary.to_csv(PROCESSED_DIR / "aggregate_summary.csv", index=False)

    # Long format: useful for plotting and the final report's tables
    long_df = pathways.merge(
        genes[["gene_symbol", "gene_id", "chromosome", "map_location"]],
        on="gene_symbol",
        how="left",
    )
    long_df.to_csv(PROCESSED_DIR / "aggregate_long.csv", index=False)

    print(f"[aggregate] {len(summary)} genes summarized, "
          f"{len(long_df)} gene-pathway rows in long format")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
