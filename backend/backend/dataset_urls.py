# backend/dataset_urls.py
"""
Centralized dataset URL configuration
V-13: All 19 datasets with their API endpoints
"""

DATASET_URLS = {
    # ===== DRUG DISCOVERY (4) =====
    "CHEMBL": {
        "url": "https://www.ebi.ac.uk/chembl/",
        "api": "https://www.ebi.ac.uk/chembl/api/data/activity.json",
        "docs": "https://chembl.gitbook.io/chembl-interface-documentation/",
        "records": "2M+",
        "format": "JSON/CSV"
    },
    "PUBCHEM": {
        "url": "https://pubchem.ncbi.nlm.nih.gov/",
        "api": "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/JSON",
        "docs": "https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest/",
        "records": "100M+",
        "format": "JSON/XML/CSV"
    },
    "ZINC15": {
        "url": "https://zinc15.docking.org/",
        "api": "https://zinc.docking.org/api/substances/",
        "docs": "https://zinc.docking.org/doc/",
        "records": "750M+",
        "format": "CSV/SDF"
    },
    "QM9": {
        "url": "https://huggingface.co/datasets/deepchem/qm9",
        "api": "HuggingFace Datasets",
        "docs": "https://huggingface.co/docs/datasets/",
        "records": "134K",
        "format": "CSV/Parquet"
    },
    
    # ===== TARGET DISCOVERY (4) =====
    "UNIPROT": {
        "url": "https://www.uniprot.org/",
        "api": "https://rest.uniprot.org/uniprotkb/search",
        "docs": "https://www.uniprot.org/help/rest_api",
        "records": "500K+",
        "format": "FASTA/JSON"
    },
    "PDB": {
        "url": "https://www.rcsb.org/",
        "api": "https://search.rcsb.org/rcsbsearch/v2/query",
        "docs": "https://www.rcsb.org/docs/developement/web-service-overview",
        "records": "200K+",
        "format": "PDB/mmCIF"
    },
    "GEO": {
        "url": "https://www.ncbi.nlm.nih.gov/geo/",
        "api": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        "docs": "https://www.ncbi.nlm.nih.gov/books/NBK25499/",
        "records": "100K+",
        "format": "CSV/JSON"
    },
    "STRING": {
        "url": "https://string-db.org/",
        "api": "https://string-db.org/api/json/network",
        "docs": "https://string-db.org/help/",
        "records": "1M+ interactions",
        "format": "JSON"
    },
    
    # ===== CLINICAL TRIALS (3) =====
    "CLINICALTRIALS_GOV": {
        "url": "https://clinicaltrials.gov/",
        "api": "https://clinicaltrials.gov/api/v2/studies",
        "docs": "https://clinicaltrials.gov/api/gui",
        "records": "500K+",
        "format": "JSON"
    },
    "MIMIC_III": {
        "url": "https://physionet.org/content/mimiciii/",
        "api": "N/A - Requires registration",
        "docs": "https://mimic.physionet.org/",
        "records": "40K+ patients",
        "format": "CSV",
        "note": "Free but requires credentialing"
    },
    "AACT": {
        "url": "https://aact.ctti-clinicaltrials.org/",
        "api": "PostgreSQL database",
        "docs": "https://aact.ctti-clinicaltrials.org/documentation",
        "records": "500K+",
        "format": "CSV/SQL"
    },
    
    # ===== FORMULATION (4) =====
    "DRUGBANK": {
        "url": "https://go.drugbank.com/",
        "api": "https://go.drugbank.com/api/v1/drugs",
        "docs": "https://go.drugbank.com/releases/latest",
        "records": "15K+",
        "format": "JSON/XML"
    },
    "ESOL": {
        "url": "https://huggingface.co/datasets/deepchem/ESOL",
        "api": "HuggingFace Datasets",
        "docs": "https://huggingface.co/docs/datasets/",
        "records": "1,128",
        "format": "CSV"
    },
    "TOX21": {
        "url": "https://tripod.nih.gov/tox21/",
        "api": "HuggingFace: tox21",
        "docs": "https://huggingface.co/datasets/tox21",
        "records": "12K",
        "format": "CSV"
    },
    "GRAS": {
        "url": "https://www.fda.gov/food/generally-recognized-safe-gras/",
        "api": "N/A - Manual data",
        "docs": "https://www.fda.gov/food/food-ingredients-additives/generally-recognized-safe-gras",
        "records": "500+",
        "format": "CSV/Manual"
    }
}

# Export function
def get_dataset_url(dataset_name: str) -> dict:
    """Get URL for a specific dataset"""
    return DATASET_URLS.get(dataset_name, {})

def get_all_urls() -> dict:
    """Get all dataset URLs"""
    return DATASET_URLS