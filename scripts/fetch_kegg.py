"""
fetch_kegg.py
-------------
Query the KEGG REST API for pathways linked to Alzheimer's-related genes.

KEGG REST docs: https://www.kegg.jp/kegg/rest/keggapi.html

Usage:
    python scripts/fetch_kegg.py

Outputs:
    data/raw/kegg_<gene>.txt        — raw KEGG flat files
    data/processed/kegg_pathways.csv — gene → pathway mapping
"""
import argparse
import os
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

KEGG_BASE = "https://rest.kegg.jp"
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def find_kegg_gene_id(gene_symbol: str, organism: str = "hsa") -> str | None:
    """Look up the KEGG gene identifier (e.g. 'hsa:351' for APP)."""
    url = f"{KEGG_BASE}/find/genes/{gene_symbol}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()

    for line in r.text.strip().splitlines():
        if not line:
            continue
        kegg_id, description = line.split("\t", 1)
        if kegg_id.startswith(f"{organism}:") and gene_symbol.upper() in description.upper().split(";")[0]:
            return kegg_id
    return None


def fetch_gene_record(kegg_gene_id: str) -> str:
    """Fetch the raw KEGG gene flat file."""
    r = requests.get(f"{KEGG_BASE}/get/{kegg_gene_id}", timeout=30)
    r.raise_for_status()
    return r.text


def parse_pathways(kegg_record: str) -> list[tuple[str, str]]:
    """Extract (pathway_id, pathway_name) tuples from a KEGG gene record."""
    pathways = []
    in_pathway_section = False

    for line in kegg_record.splitlines():
        if line.startswith("PATHWAY"):
            in_pathway_section = True
            line = line[len("PATHWAY"):]
        elif line and not line.startswith(" "):
            in_pathway_section = False

        if in_pathway_section:
            stripped = line.strip()
            if stripped:
                parts = stripped.split(maxsplit=1)
                if len(parts) == 2:
                    pathways.append((parts[0], parts[1]))
    return pathways


def main(genes: list[str]) -> None:
    rows = []
    for gene in genes:
        print(f"[fetch_kegg] {gene} ...")
        try:
            kegg_id = find_kegg_gene_id(gene)
            if not kegg_id:
                print(f"  ! no KEGG match for {gene}")
                continue

            time.sleep(0.5)  # KEGG asks for ~3 req/s max
            record = fetch_gene_record(kegg_id)
            (RAW_DIR / f"kegg_{gene}.txt").write_text(record)

            for pid, pname in parse_pathways(record):
                rows.append({
                    "gene_symbol": gene,
                    "kegg_gene_id": kegg_id,
                    "pathway_id": pid,
                    "pathway_name": pname,
                })

            time.sleep(0.5)
        except Exception as e:
            print(f"  ! error on {gene}: {e}")

    df = pd.DataFrame(rows)
    df.to_csv(PROCESSED_DIR / "kegg_pathways.csv", index=False)
    print(f"[fetch_kegg] wrote {len(df)} gene-pathway links")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    default_genes = os.getenv("TARGET_GENES", "APP,PSEN1,PSEN2").split(",")
    parser.add_argument("--genes", nargs="+", default=default_genes)
    args = parser.parse_args()
    main(args.genes)
