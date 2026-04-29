# 🚀 V-9: Dataset Integration Implementation Guide

## Quick Start

### 1. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### 2. **Initialize Databases**
```bash
python
>>> from dataset_db import dataset_db
>>> # Tables are auto-created on import
>>> exit()
```

### 3. **Start the Server**
```bash
python -m uvicorn server:app --reload --port 8000
```

### 4. **Verify Installation**
```bash
curl http://localhost:8000/api/datasets/available
curl http://localhost:8000/api/datasets/stats
```

---

## Usage Examples

### Example 1: Get Compound Profile

Get all available data for a drug (PubChem, ChEMBL, Tox21, ESOL):

```bash
curl "http://localhost:8000/api/datasets/compound-profile?smiles=CC(=O)Oc1ccccc1C(=O)O"
```

**Response:**
```json
{
  "status": "success",
  "smiles": "CC(=O)Oc1ccccc1C(=O)O",
  "data": {
    "pubchem_properties": {
      "molecular_weight": 180.16,
      "log_p": 1.19,
      "h_bond_donors": 1,
      "h_bond_acceptors": 3
    },
    "chembl_bioactivity": {
      "target_name": "Cyclooxygenase-1",
      "bioactivity_value": 6000.0,
      "bioactivity_type": "IC50"
    },
    "toxicity_profile": {...},
    "solubility_prediction": {
      "solubility_score": 75.5,
      "bcs_class": "I"
    }
  },
  "response_time_ms": 125.3
}
```

### Example 2: Validate Formulation

Check if excipients are GRAS-approved and compatible:

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

**Response:**
```json
{
  "valid": true,
  "warnings": [],
  "metadata": {
    "Microcrystalline Cellulose": {
      "category": "Binder & Diluent",
      "max_usage": "up to 90%",
      "compatible_with": ["tablets", "capsules", "powders"]
    },
    "Lactose Monohydrate": {...},
    "Magnesium Stearate": {...}
  }
}
```

### Example 3: Search Clinical Trials

Find recruiting cancer trials in phase 2:

```bash
curl "http://localhost:8000/api/datasets/trials?condition=cancer&status=RECRUITING&phase=2"
```

**Response:**
```json
{
  "status": "success",
  "total_trials": 127,
  "trials": [
    {
      "nct_id": "NCT04123456",
      "title": "Phase 2 Trial of Drug X in NSCLC",
      "condition": "Non-Small Cell Lung Cancer",
      "phase": "2",
      "status": "RECRUITING",
      "enrollment": 150,
      "start_date": "2024-01-15"
    }
  ]
}
```

### Example 4: Ingest New Dataset

Trigger ingestion of ESOL solubility data:

```bash
curl -X POST "http://localhost:8000/api/datasets/ingest/esol_solubility"
```

**Response:**
```json
{
  "status": "success",
  "dataset_type": "esol_solubility",
  "total_records": 1128,
  "processed_records": 1125,
  "failed_records": 3,
  "saved_records": 1125,
  "response_time_ms": 234.5
}
```

---

## Testing

### Run Full Dataset Test Suite

```bash
python test_v9_datasets.py
```

This will test:
- ✅ Available datasets listing
- ✅ Dataset statistics
- ✅ Compound profile retrieval
- ✅ Solubility predictions
- ✅ Toxicity assays
- ✅ Formulation validation
- ✅ Dataset ingestion (dry run)

### Run Individual Tests

```python
# Test compound profile
import asyncio
from dataset_service import DatasetService

async def test():
    profile = await DatasetService.get_compound_profile("CC(=O)Oc1ccccc1C(=O)O")
    print(profile)

asyncio.run(test())
```

---

## API Reference

### Ingest Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/datasets/ingest/pubchem_properties` | Ingest PubChem properties |
| POST | `/datasets/ingest/chembl_bioactivity` | Ingest ChEMBL bioactivity |
| POST | `/datasets/ingest/uniprot_sequences` | Ingest UniProt sequences |
| POST | `/datasets/ingest/clinical_trials` | Ingest clinical trials |
| POST | `/datasets/ingest/tox21_toxicity` | Ingest Tox21 data |
| POST | `/datasets/ingest/esol_solubility` | Ingest ESOL data |
| POST | `/datasets/ingest/gras_excipients` | Ingest GRAS excipients |

### Query Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/datasets/available` | List all available datasets |
| GET | `/datasets/stats` | Get statistics for all datasets |
| GET | `/datasets/compound-profile` | Get complete compound profile |
| GET | `/datasets/solubility` | Get solubility prediction |
| GET | `/datasets/toxicity` | Get toxicity profile |
| GET | `/datasets/bioactivity` | Get ChEMBL bioactivity |
| GET | `/datasets/protein/{uniprot_id}` | Get protein information |
| GET | `/datasets/trials` | Search clinical trials |
| POST | `/datasets/validate-formulation` | Validate formulation |
| GET | `/datasets/export` | Export all datasets |

---

## Architecture

```
┌─────────────────────────────────────────┐
│      FastAPI Server (server.py)         │
│                                         │
│  /api/datasets/* routes                 │
└──────────────┬──────────────────────────┘
               │
        ┌──────▼───────┐
        │Dataset Manager│
        │(orchestrator) │
        └──────┬────────┘
               │
        ┌──────┴─────────┐
        │                │
   ┌────▼────┐   ┌──────▼──────┐
   │Ingestors│   │Database     │
   │(7 types)│   │(SQLite)     │
   └─────────┘   └─────────────┘
```

---

## File Structure

```
backend/
├── server.py                          # Main FastAPI app (updated)
├── dataset_manager.py                 # Central orchestrator ✨ NEW
├── dataset_models.py                  # Pydantic schemas ✨ NEW
├── dataset_service.py                 # Query API ✨ NEW
├── dataset_db.py                      # SQLite database ✨ NEW
├── Ingestors/                         # Dataset ingestors ✨ NEW
│   ├── __init__.py
│   ├── base_ingestor.py
│   ├── pubchem_ingestor.py
│   ├── chembl_ingestor.py
│   ├── uniprot_ingestor.py
│   ├── clinical_trials_ingestor.py
│   ├── tox21_ingestor.py
│   ├── esol_ingestor.py
│   └── gras_ingestor.py
├── DATASETS.md                        # Dataset documentation ✨ NEW
├── IMPLEMENTATION_GUIDE.md            # This file ✨ NEW
├── test_v9_datasets.py               # Dataset tests ✨ NEW
└── requirements.txt                   # Updated with new deps
```

---

## Troubleshooting

### Issue: "Module not found" error

**Solution:**
```bash
pip install -r requirements.txt
python -c "from Ingestors.base_ingestor import BaseIngestor; print('✅ OK')"
```

### Issue: Database locked

**Solution:**
```bash
# Close all connections and restart
rm pharma_datasets.db
python -c "from dataset_db import dataset_db; print('✅ DB initialized')"
```

### Issue: API timeout on large dataset ingest

**Solution:**
```bash
# Use dry_run first to validate
POST /datasets/ingest/chembl_bioactivity?dry_run=true

# Then ingest with explicit timeout
curl --max-time 300 -X POST "http://localhost:8000/api/datasets/ingest/chembl_bioactivity"
```

---

## Next Steps

- [ ] Add batch ingestion scheduler (celery/APScheduler)
- [ ] Create frontend dashboard for dataset browser
- [ ] Add caching layer (Redis) for frequent queries
- [ ] Implement incremental updates (sync only new records)
- [ ] Add data quality monitoring
- [ ] Create automated daily ingestion jobs
- [ ] Add GraphQL endpoint for dataset queries

---

## Support

For issues or questions:
1. Check `/api/datasets/stats` to verify datasets are loaded
2. Review logs in `server.py` output
3. Test individual endpoints with `test_v9_datasets.py`
4. Check database integrity: `sqlite3 pharma_datasets.db ".tables"`