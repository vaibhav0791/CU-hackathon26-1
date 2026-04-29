import asyncio
import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base_ingestor import BaseIngestor
from bson import ObjectId

logger = logging.getLogger(__name__)

class ChEMBLIngestor(BaseIngestor):
    """Ingest bioactivity data from ChEMBL API"""
    
    def __init__(self, target_organism: str = "Homo sapiens"):
        super().__init__("chembl_bioactivity")
        self.target_organism = target_organism
        self.base_url = "https://www.ebi.ac.uk/chembl/api/data"
        self.timeout = 20.0
        self.page_size = 100
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch bioactivity data from ChEMBL"""
        
        bioactivities = []
        page = 1
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while len(bioactivities) < 1000:  # Limit to 1000 records per ingestion
                try:
                    logger.info(f"📥 Fetching ChEMBL bioactivity page {page}...")
                    
                    # Query top bioactivity assays
                    url = f"{self.base_url}/activity.json?limit={self.page_size}&offset={(page-1)*self.page_size}&organism__icontains={self.target_organism}"
                    
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        activities = data.get("results", [])
                        
                        if not activities:
                            logger.info("✅ No more records found")
                            break
                        
                        for activity in activities:
                            bioactivities.append({
                                "chembl_id": activity.get("molecule_chembl_id"),
                                "smiles": activity.get("canonical_smiles"),
                                "drug_name": activity.get("compound_name", "Unknown"),
                                "target_name": activity.get("assay_description", "Unknown"),
                                "bioactivity_type": activity.get("standard_type", "IC50"),
                                "bioactivity_value": activity.get("standard_value"),
                                "standard_units": activity.get("standard_units", "nM"),
                                "assay_id": activity.get("assay_chembl_id"),
                                "source": "ChEMBL"
                            })
                        
                        logger.info(f"✅ Retrieved {len(activities)} records (total: {len(bioactivities)})")
                        page += 1
                        await asyncio.sleep(1)  # Rate limiting
                    
                    else:
                        logger.error(f"❌ API error: {response.status_code}")
                        break
                
                except Exception as e:
                    logger.error(f"❌ Error fetching page {page}: {type(e).__name__}: {e}")
                    break
        
        return bioactivities
    
    async def validate_record(self, record: Dict[str, Any]) -> tuple:
        """Validate ChEMBL record"""
        
        if not record.get("chembl_id"):
            return False, "Missing ChEMBL ID"
        
        if not record.get("smiles"):
            return False, "Missing SMILES"
        
        if not record.get("bioactivity_value"):
            return False, "Missing bioactivity value"
        
        # Validate bioactivity value is numeric
        try:
            float(record["bioactivity_value"])
        except (ValueError, TypeError):
            return False, "Invalid bioactivity value"
        
        return True, "Valid"
    
    async def transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform to database format"""
        
        return {
            "_id": str(ObjectId()),
            "chembl_id": record["chembl_id"],
            "smiles": record["smiles"],
            "drug_name": record.get("drug_name"),
            "target_name": record.get("target_name"),
            "bioactivity_type": record.get("bioactivity_type"),
            "bioactivity_value": float(record.get("bioactivity_value", 0)),
            "standard_units": record.get("standard_units"),
            "assay_id": record.get("assay_id"),
            "created_at": datetime.utcnow().isoformat()
        }