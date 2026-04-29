# 📊 PHARMA-AI Datasets Integration

Complete guide to integrated datasets in Pharma AI backend.

## Overview

Pharma AI integrates **7 major datasets** across 4 therapeutic areas:

| Dataset | Type | Records | Source | Purpose |
|---------|------|---------|--------|---------|
| **PubChem** | Molecular Properties | 100M+ | API | LogP, MW, H-bonds, TPSA |
| **ChEMBL** | Bioactivity | 2M+ | API | IC50, EC50, Ki values |
| **UniProt** | Protein Sequences | 500K+ | API | Target identification |
| **RCSB PDB** | 3D Structures | 200K+ | API | Protein binding sites |
| **ClinicalTrials.gov** | Trial Metadata | 500K+ | API | Phase, status, outcomes |
| **Tox21** | Toxicity Assays | 12K | File | Toxicity across 12 assays |
| **ESOL** | Solubility | 1.1K | File | Water solubility prediction |
| **GRAS** | Excipients | 500+ | File | FDA-approved excipients |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Server                           │
│                   (server.py)                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐         ┌─────────▼──────────┐
│ Dataset Routes │         │ Dataset Manager    │
│ (/api/datasets)│         │ (dataset_manager)  │
└────────────────┘         └────────┬───────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
        ┌───────▼────────┐  ┌───────▼────────┐  ┌──────▼─────────┐
        │  Ingestors     │  │  Database      │  │  Service Layer │
        │  (Ingestors/)  │  │  (dataset_db)  │  │ (dataset_svc)  │
        └────────────────┘  └────────────────┘  └────────────────┘
```

---

## Dataset Models

### 1. **PubChem Properties**
```python
{
    "cid": 2244,  # PubChem ID
    "smiles": "CC(=O)Oc1ccccc1C(=O)O",
    "drug_name": "Aspirin",
    "molecular_weight": 180.16,
    "log_p": 1.19,
    "h_bond_donors": 1,
    "h_bond_acceptors": 3,
    "rotatable_bonds": 2,
    "topological_psa": 63.60
}
```

### 2. **ChEMBL Bioactivity**
```python
{
    "chembl_id": "CHEMBL25",
    "smiles": "CC(=O)Oc1ccccc1C(=O)O",
    "drug_name": "Aspirin",
    "target_name": "Cyclooxygenase-1",
    "bioactivity_type": "IC50",
    "bioactivity_value": 6000.0,  # nM
    "standard_units": "nM",
    "assay_id": "CHEMBL1040786"
}
```

### 3. **UniProt Sequences**
```python
{
    "uniprot_id": "P05362",
    "protein_name": "Intercellular adhesion molecule 1",
    "gene_name": "ICAM1",
    "organism": "Homo sapiens",
    "sequence": "MFVGPAFL...[~450 amino acids]...NVSF",
    "sequence_length": 532,
    "function": "Cell adhesion, immune response"
}
```

### 4. **Clinical Trials**
```python
{
    "nct_id": "NCT04123456",
    "title": "Phase 3 Trial of Drug X in Cancer",
    "drug_name": "Drug X",
    "condition": "Non-Small Cell Lung Cancer",
    "phase": "3",
    "status": "RECRUITING",
    "enrollment": 500,
    "start_date": "2024-01-15",
    "primary_outcome": "Overall Survival"
}
```

### 5. **Tox21 Toxicity**
```python
{
    "smiles": "CC(=O)Oc1ccccc1C(=O)O",
    "drug_name": "Aspirin",
    "assay_name": "SR-MMP",
    "result": "Active",  # Active/Inactive/Inconclusive
    "activity_score": 0.85,  # 0-1
    "assay_description": "Stress Response - MMP Assay"
}
```

### 6. **ESOL Solubility**
```python
{
    "smiles": "CC(=O)Oc1ccccc1C(=O)O",
    "drug_name": "Aspirin",
    "solubility_score": 75.5,  # 0-100
    "bcs_class": "I",
    "molecular_weight": 180.16,
    "log_p": 1.19
}
```

### 7. **GRAS Excipients**
```python
{
    "name": "Microcrystalline Cellulose",
    "fda_registry_number": "9004-34-6",
    "cas_number": "9004-34-6",
    "category": "Binder & Diluent",
    "max_usage": "up to 90%",
    "compatible_with": ["tablets", "capsules", "powders"]
}
```

---

## API Endpoints

### Ingest Datasets

```bash
# Ingest PubChem properties
POST /api/datasets/ingest/pubchem_properties
Body: { "drug_list": ["2244", "3825"] }

# Ingest ChEMBL bioactivity
POST /api/datasets/ingest/chembl_bioactivity
Body: {}

# Ingest ESOL solubility
POST /api/datasets/ingest/esol_solubility
Body: {}

# Ingest GRAS excipients
POST /api/datasets/ingest/gras_excipients
Body: {}
```

### Query Datasets

```bash
# Get compound profile (all data for a SMILES)
GET /api/datasets/compound-profile?smiles=CC(=O)Oc1ccccc1C(=O)O

# Get solubility prediction
GET /api/datasets/solubility?smiles=CC(=O)Oc1ccccc1C(=O)O

# Get toxicity profile
GET /api/datasets/toxicity?smiles=CC(=O)Oc1ccccc1C(=O)O

# Get bioactivity data
GET /api/datasets/bioactivity?drug_name=Aspirin

# Get protein info
GET /api/datasets/protein/P05362

# Validate formulation
POST /api/datasets/validate-formulation
Body: { "excipients": ["Microcrystalline Cellulose", "Lactose"] }

# Search clinical trials
GET /api/datasets/trials?condition=cancer&status=RECRUITING

# Get dataset statistics
GET /api/datasets/stats
```

---

## Usage Examples

### Example 1: Get Compound Profile

```bash
curl "http://localhost:8000/api/datasets/compound-profile?smiles=CC(=O)Oc1ccccc1C(=O)O"
```

Response:
```json
{
  "smiles": "CC(=O)Oc1ccccc1C(=O)O",
  "data": {
    "pubchem_properties": {
      "molecular_weight": 180.16,
      "log_p": 1.19,
      "h_bond_donors": 1
    },
    "chembl_bioactivity": {
      "target_name": "Cyclooxygenase-1",
      "bioactivity_value": 6000.0,
      "bioactivity_type": "IC50"
    },
    "toxicity_profile": {
      "assay_results": [...]
    },
    "solubility_prediction": {
      "solubility_score": 75.5,
      "bcs_class": "I"
    }
  }
}
```

### Example 2: Validate Formulation

```bash
curl -X POST "http://localhost:8000/api/datasets/validate-formulation" \
  -H "Content-Type: application/json" \
  -d '{
    "excipients": [
      "Microcrystalline Cellulose",
      "Lactose Monohydrate",
      "Magnesium Stearate"
    ]
  }'
```

Response:
```json
{
  "valid": true,
  "metadata": {
    "Microcrystalline Cellulose": {
      "category": "Binder & Diluent",
      "max_usage": "up to 90%",
      "compatible_with": ["tablets", "capsules"]
    }
  }
}
```

---

## Database Schema

All datasets stored in SQLite (`pharma_datasets.db`):

```sql
-- PubChem Properties
CREATE TABLE pubchem_properties (
  _id TEXT PRIMARY KEY,
  cid INTEGER UNIQUE,
  smiles TEXT NOT NULL,
  molecular_weight REAL,
  log_p REAL,
  h_bond_donors INTEGER,
  ...
);

-- ChEMBL Bioactivity
CREATE TABLE chembl_bioactivity (
  _id TEXT PRIMARY KEY,
  chembl_id TEXT UNIQUE,
  smiles TEXT NOT NULL,
  bioactivity_type TEXT,
  bioactivity_value REAL,
  ...
);

-- [Similar for other datasets]
```

---

## Indexing Strategy

Each dataset has optimal indexes for fast queries:

| Dataset | Indexes |
|---------|---------|
| PubChem | `smiles`, `cid`, `molecular_weight` |
| ChEMBL | `smiles`, `drug_name`, `target_name` |
| UniProt | `uniprot_id`, `protein_name`, `gene_name` |
| Trials | `drug_name`, `status`, `phase` |
| Tox21 | `smiles`, `assay_name` |
| ESOL | `smiles`, `bcs_class` |
| GRAS | `name`, `category` |

---

## Implementation Status

- ✅ Dataset Models (Pydantic schemas)
- ✅ Database Schema (SQLite tables + indexes)
- ✅ Base Ingestor Class
- ✅ 7 Dataset Ingestors
- ✅ Dataset Manager (orchestration)
- ✅ Dataset Service (query API)
- ⏳ Server Integration (API routes)
- ⏳ Frontend Dashboard

---

## Next Steps

1. Integrate with `server.py` (add `/api/datasets` routes)
2. Create test suite for ingestors
3. Add batch ingestion scheduler
4. Build frontend dashboard for dataset browser
5. Add caching layer for frequent queries