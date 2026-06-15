# 💊 PHARMA-AI Drug Database Documentation

## Overview
The drug database powers PHARMA-AI's analysis engine. Drugs are stored in three locations:
1. **drugs.json** — Source data file (ingested into SQLite)
2. **server.py → DRUG_DATABASE** — In-memory lookup for quick access
3. **pharma.db** — SQLite persistent storage (populated via ingest_data.py)

## Current Database Stats
- **Total Drugs**: 45
- **Categories**: Cardiovascular, Anticoagulant, Anti-infective, CNS, Oncology
- **Skipped**: 2 (Vancomycin, Rituximab — biologics without SMILES)

## Required Fields for Each Drug Entry

### In drugs.json

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| drug_name | string | Yes | Common drug name |
| smiles | string | Yes* | Canonical SMILES notation |
| cid | integer | Optional | PubChem Compound ID (used to fetch SMILES if missing) |
| bcs_class | string | Yes | BCS class: I, II, III, or IV |
| molecular_weight | float | Optional | Molecular weight in Daltons (Da) |
| category | string | Yes | Therapeutic category tag |

> *If smiles is missing but cid is provided, ingest_data.py will auto-fetch from PubChem.

### Example drugs.json entry

```json
{
    "drug_name": "Aspirin",
    "smiles": "CC(=O)Oc1ccccc1C(=O)O",
    "cid": 2244,
    "bcs_class": "I",
    "molecular_weight": 180.16,
    "category": "Analgesic"
}
```

### Example server.py entry

```python
"Aspirin": {
    "smiles": "CC(=O)Oc1ccccc1C(=O)O",
    "bcs_class": "I",
    "molecular_weight": 180.16,
    "category": "Analgesic"
}
```

## Valid Categories

| Category | Examples |
|----------|----------|
| Cardiovascular | Atorvastatin, Amlodipine, Diltiazem |
| Anticoagulant | Warfarin |
| Anti-infective | Azithromycin, Fluconazole, Rifampicin |
| CNS | Levetiracetam, Carbamazepine, Escitalopram |
| Oncology | Imatinib, Doxorubicin, Paclitaxel |
| Analgesic | Aspirin |

## Valid BCS Classes

| Class | Solubility | Permeability |
|-------|-----------|--------------|
| I | High | High |
| II | Low | High |
| III | High | Low |
| IV | Low | Low |

## How to Add New Drugs

### Step 1: Add to drugs.json
Add a new JSON object with all required fields at the end of the array (before the closing `]`).

### Step 2: Add to server.py
Add a matching entry inside the `DRUG_DATABASE` dictionary.

### Step 3: Run Ingestion

```bash
cd backend
python ingest_data.py
```

### Step 4: Verify
Check the output — your drug should show `[SAVED]`.

## Where to Find Drug Data

| Source | URL | Access |
|--------|-----|--------|
| PubChem | https://pubchem.ncbi.nlm.nih.gov/ | Free (SMILES + CID + MW) |
| DrugBank | https://go.drugbank.com/ | Requires license (richer data) |
| ChEMBL | https://www.ebi.ac.uk/chembl/ | Free (bioactivity data) |

## SMILES Validation

Run verify_smiles.py to check all SMILES in the database:

```bash
python verify_smiles.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `no column named category` | Delete `pharma.db` and re-run `ingest_data.py` |
| Drug shows `[SKIP]` | Missing SMILES — add manually or provide valid CID |
| `[VALIDATION FAILED]` | Check BCS class is I/II/III/IV, SMILES is not empty |

## Maintainer
**Himanshu** — Database Engineer
- Weekly target: +10 drugs/week
- Source: DrugBank / PubChem verified entries
