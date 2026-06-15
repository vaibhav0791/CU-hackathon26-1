# H-7: DrugBank Integration Research

## Summary
Research into DrugBank API for automated drug property fetching.

## DrugBank API Overview
- **Website**: https://go.drugbank.com/
- **API Docs**: https://docs.drugbank.com/
- **Access**: Requires academic or commercial license (not free/open)
- **Alternative**: DrugBank Open Data (subset) is freely available

## Available Data Fields via API

| Field | Description |
|-------|-------------|
| drugbank_id | Unique DrugBank identifier (e.g., DB00945) |
| name | Drug name |
| smiles | Canonical SMILES string |
| molecular_weight | Molecular weight (Da) |
| logp | Partition coefficient |
| pka | Acid dissociation constant |
| categories | Therapeutic categories |
| route | Administration route |
| bcs_class | Biopharmaceutical Classification |

## Current Approach (PubChem — Free)
We currently use PubChem REST API (free, no API key needed):

```
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{CID}/property/CanonicalSMILES/JSON
```

## Recommendation
1. **Short-term**: Continue using PubChem (free, reliable)
2. **Medium-term**: Apply for DrugBank Academic License for richer data
3. **Long-term**: Build automated pipeline that fetches from both sources

## Integration Plan (with Vaibhav)
- Vaibhav handles the data pipeline (`ingest_data.py`)
- Himanshu provides verified drug entries in `drugs.json`
- Future: Automate fetching MW, LogP, pKa from DrugBank API

## Status: ✅ Research Complete
