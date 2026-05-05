# Genomic Analysis and Pathway Data Aggregation for Alzheimer's Disease

**CS/BIOL 123A Bioinformatics — San Jose State University**

A data-engineering pipeline that programmatically aggregates genomic data, variants, and metabolic pathway information for genes implicated in Alzheimer's Disease (AD). Target genes include **APP**, **PSEN1**, and **PSEN2**, with data sourced from NCBI Entrez and KEGG.

## Team

| Name | Major | Email |
|---|---|---|
| Alan Xiao | Computer Science | alan.xiao@sjsu.edu |
| Olsen Arliawan | Data Science | olsen.arliawan@sjsu.edu |
| Shreya Jayakumar | Data Science | shreya.jayakumar@sjsu.edu |
| Saivennela Tipirneni | Data Science | saivennela.tipirneni@sjsu.edu |

## Project Goals

1. Identify the genomic basis of Alzheimer's Disease through automated NCBI queries.
2. Map target genes to their associated metabolic pathways via KEGG.
3. Aggregate variant and disease-association data into clean, analysis-ready datasets.
4. Produce a final report linking automated findings to existing literature on treatments and personalized medicine.

## Repository Structure

```
alzheimers-bioinformatics/
├── scripts/          # Python scripts for data fetching and processing
│   ├── fetch_ncbi.py     # Query NCBI Entrez for gene/variant data
│   ├── fetch_kegg.py     # Query KEGG for pathway data
│   └── aggregate.py      # Merge outputs into final datasets
├── data/
│   ├── raw/          # Raw API responses (gitignored except samples)
│   └── processed/    # Cleaned CSVs ready for analysis
├── notebooks/        # Jupyter notebooks for exploration & visualization
├── reports/          # Progress report, final report, figures
├── docs/             # Supplementary documentation
├── requirements.txt  # Python dependencies
└── README.md
```

## Setup

### Prerequisites
- Python 3.10+
- Git

### Installation

```bash
git clone https://github.com/<your-org>/alzheimers-bioinformatics.git
cd alzheimers-bioinformatics
python -m venv venv
source venv/bin/activate          # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

NCBI Entrez requires an email address (and optionally an API key) for queries. Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

## Usage

Fetch data for the default target genes (APP, PSEN1, PSEN2):

```bash
python scripts/fetch_ncbi.py
python scripts/fetch_kegg.py
python scripts/aggregate.py
```

Outputs land in `data/processed/` as CSV files.

## Roadmap

- [x] Project proposal approved
- [ ] Repo setup + environment (3/14)
- [ ] NCBI fetch script (3/21)
- [ ] KEGG fetch script (3/28)
- [ ] Data aggregation pipeline (4/4)
- [ ] Progress report (4/11)
- [ ] Analysis + visualizations (4/25)
- [ ] Final report + presentation (5/13)

## References

Pevsner, J. (2015). *Bioinformatics and Functional Genomics* (3rd ed.), Chapter 21: Neurodegenerative Diseases. Wiley-Blackwell.

## License

Academic project — for course use only.
