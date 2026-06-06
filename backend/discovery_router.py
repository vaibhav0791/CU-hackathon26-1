# backend/discovery_router.py
"""
Pharma AI - Dynamic Automated Routing Gateway
Exposes a single universal path to retrieve any dataset programmatically.
"""

from fastapi import APIRouter, HTTPException, Query
from run_discovery_audit import PharmaAIDiscoveryAudit

router = APIRouter(tags=["Universal Data Retrieval"])

@router.get("/discovery/retrieve")
async def dynamic_data_retrieval(
    category: str = Query(..., description="The category name (e.g., respiratory, pain, diabetes, cancer)"),
    limit: int = 100
):
    """
    🌐 AUTOMATED MASTER GATEWAY:
    Accepts any category request, triggers dynamic extraction, removes history duplication,
    and automatically hands over the data payload to Damini/Tech Team.
    """
    try:
        audit_engine = PharmaAIDiscoveryAudit()
        
        # Build keyword search arrays based on request input
        category_clean = category.strip().upper()
        keywords = [category_clean]
        
        # Map sub-targets if common terms are parsed
        if "CANCER" in category_clean or "ONCOLOGY" in category_clean:
            keywords.extend(["TUMOR", "BRCA", "EGFR", "KINASE"])
        elif "RESPIRATORY" in category_clean:
            keywords.extend(["ADRB2", "PDE4D", "CHRM3", "HRH1", "IL5"])
        elif "PAIN" in category_clean:
            keywords.extend(["OPRM1", "TRPV1", "SCN9A", "FAAH"])

        # Fetch clean, filtered structural lists
        pristine_dataset = await audit_engine.fetch_dynamic_category(keywords=keywords, limit=limit)
        
        return {
            "status": "success",
            "requested_category": category,
            "total_records_retrieved": len(pristine_dataset),
            "data": pristine_dataset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Universal Ingestion Gateway Error: {str(e)}")