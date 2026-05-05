"""
fetch_ncbi.py
-------------
Query NCBI Entrez for gene records, variants, and disease associations
for Alzheimer's-related genes (APP, PSEN1, PSEN2 by default).

Usage:
    python scripts/fetch_ncbi.py
    python scripts/fetch_ncbi.py --genes APP PSEN1 APOE

Outputs:
    data/raw/ncbi_<gene>.json     — raw API responses
    data/processed/ncbi_genes.csv — flattened summary table
"""
import argparse
import json
import os
import time
from pathlib import Path

import pandas as pd
from Bio import Entrez
from dotenv import load_dotenv

load_dotenv()

# NCBI requires an email. They use it to contact you if a script is causing problems.
Entrez.email = os.getenv("NCBI_EMAIL", "your.email@sjsu.edu")
api_key = os.getenv("NCBI_API_KEY")
if api_key:
    Entrez.api_key = api_key

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def fetch_gene_summary(gene_symbol: str, organism: str = "Homo sapiens") -> dict:
    """Search NCBI Gene for a symbol and return the top summary record."""
    query = f"{gene_symbol}[Gene Name] AND {organism}[Organism]"
    with Entrez.esearch(db="gene", term=query, retmax=1) as handle:
        search = Entrez.read(handle)

    if not search["IdList"]:
        return {"gene_symbol": gene_symbol, "error": "no results"}

    gene_id = search["IdList"][0]
    time.sleep(0.34)  # be polite — NCBI rate limit without API key is 3 req/s

    with Entrez.esummary(db="gene", id=gene_id) as handle:
        summary = Entrez.read(handle)

    record = summary["DocumentSummarySet"]["DocumentSummary"][0]
    return {
        "gene_symbol": gene_symbol,
        "gene_id": gene_id,
        "name": record.get("Name", ""),
        "description": record.get("Description", ""),
        "chromosome": record.get("Chromosome", ""),
        "map_location": record.get("MapLocation", ""),
        "summary": record.get("Summary", ""),
    }


def fetch_clinvar_variants(gene_symbol: str, retmax: int = 50) -> list[dict]:
    """Pull ClinVar variants for a gene. Returns simplified records."""
    query = f"{gene_symbol}[gene] AND clinsig_pathogenic[filter]"
    with Entrez.esearch(db="clinvar", term=query, retmax=retmax) as handle:
        search = Entrez.read(handle)

    ids = search["IdList"]
    if not ids:
        return []

    time.sleep(0.34)
    with Entrez.esummary(db="clinvar", id=",".join(ids)) as handle:
        summary = Entrez.read(handle)

    variants = []
    for rec in summary.get("DocumentSummarySet", {}).get("DocumentSummary", []):
        variants.append({
            "gene_symbol": gene_symbol,
            "variation_id": rec.attributes.get("uid", "") if hasattr(rec, "attributes") else "",
            "title": rec.get("title", ""),
            "clinical_significance": str(rec.get("clinical_significance", "")),
        })
    return variants


def main(genes: list[str]) -> None:
    gene_rows = []
    variant_rows = []

    for gene in genes:
        print(f"[fetch_ncbi] {gene} ...")
        try:
            gene_rows.append(fetch_gene_summary(gene))
            variant_rows.extend(fetch_clinvar_variants(gene))
        except Exception as e:
            print(f"  ! error on {gene}: {e}")
            gene_rows.append({"gene_symbol": gene, "error": str(e)})

        time.sleep(0.34)

    # Save raw + processed
    (RAW_DIR / "ncbi_genes.json").write_text(json.dumps(gene_rows, indent=2))
    (RAW_DIR / "ncbi_variants.json").write_text(json.dumps(variant_rows, indent=2))

    pd.DataFrame(gene_rows).to_csv(PROCESSED_DIR / "ncbi_genes.csv", index=False)
    pd.DataFrame(variant_rows).to_csv(PROCESSED_DIR / "ncbi_variants.csv", index=False)
    print(f"[fetch_ncbi] wrote {len(gene_rows)} genes, {len(variant_rows)} variants")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    default_genes = os.getenv("TARGET_GENES", "APP,PSEN1,PSEN2").split(",")
    parser.add_argument("--genes", nargs="+", default=default_genes,
                        help="Gene symbols to query (default: APP PSEN1 PSEN2)")
    args = parser.parse_args()
    main(args.genes)
