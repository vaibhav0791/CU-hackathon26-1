# backend/discovery_router.py
"""
Pharma AI - Automated Discovery Data Gateway
Exposes a live API endpoint for the AI team to fetch pristine ChEMBL + PubChem data automatically.
"""

from fastapi import APIRouter, HTTPException
from run_discovery_audit import PharmaAIDiscoveryAudit

router = APIRouter(tags=["Discovery Ingestion"])

@router.get("/discovery/pristine-data")
async def get_pristine_training_data(limit: int = 50):
    """
    Automated API Gateway for the AI Training Team.
    Dynamically tests endpoints, references training metrics history, and drops old target blocks.
    """
    try:
        audit_engine = PharmaAIDiscoveryAudit()
        
        # 1. Fetch from live endpoints
        chembl_data = await audit_engine.test_and_fetch_chembl(limit=limit)
        pubchem_data = await audit_engine.test_and_fetch_pubchem_properties(cid=3672) # Ibuprofen validation verification
        
        # 2 & 3. Combine ChEMBL + PubChem data arrays and run history validation cleanup
        pristine_dataset = audit_engine.join_and_deduplicate(
            chembl_list=chembl_data, 
            pubchem_profile=pubchem_data
        )
        
        if not pristine_dataset:
            return {
                "status": "success",
                "total_records": 0,
                "message": "All retrieved items matched previously trained data arrays. No new data generated.",
                "data": []
            }
            
        return {
            "status": "success",
            "total_records": len(pristine_dataset),
            "data": pristine_dataset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Automated Ingestion Gateway Error: {str(e)}")