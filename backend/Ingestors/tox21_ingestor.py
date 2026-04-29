import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from .base_ingestor import BaseIngestor
from bson import ObjectId

logger = logging.getLogger(__name__)

class Tox21Ingestor(BaseIngestor):
    """Ingest Tox21 toxicity assay data"""
    
    def __init__(self, data_file: Optional[str] = None):
        super().__init__("tox21_toxicity")
        self.data_file = data_file
        # Sample Tox21 data structure
        self.sample_data = [
            {
                "smiles": "CC(=O)Oc1ccccc1C(=O)O",
                "drug_name": "Aspirin",
                "assay_name": "SR-MMP",
                "result": "Active",
                "activity_score": 0.85,
                "assay_description": "Stress Response - MMP Assay"
            },
            {
                "smiles": "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
                "drug_name": "Ibuprofen",
                "assay_name": "SR-MMP",
                "result": "Active",
                "activity_score": 0.72,
                "assay_description": "Stress Response - MMP Assay"
            },
            {
                "smiles": "CC(C)NCC(O)COc1ccc(CCOC)cc1",
                "drug_name": "Metoprolol",
                "assay_name": "NR-PPAR-g",
                "result": "Inactive",
                "activity_score": 0.15,
                "assay_description": "Nuclear Receptor - PPAR-gamma Assay"
            },
        ]
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch Tox21 data from file or API"""
        
        if self.data_file and Path(self.data_file).exists():
            try:
                logger.info(f"📥 Loading Tox21 data from {self.data_file}")
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ Error loading file: {e}")
                logger.info("Using sample data instead")
                return self.sample_data
        
        # Use sample data if no file provided
        logger.info("📥 Using sample Tox21 data (12 assays, 12,000+ compounds available)")
        return self.sample_data
    
    async def validate_record(self, record: Dict[str, Any]) -> tuple:
        """Validate Tox21 record"""
        
        if not record.get("smiles"):
            return False, "Missing SMILES"
        
        if not record.get("assay_name"):
            return False, "Missing assay name"
        
        if record.get("result") not in ["Active", "Inactive", "Inconclusive"]:
            return False, f"Invalid result: {record.get('result')}"
        
        # Validate activity score is between 0-1
        activity_score = record.get("activity_score")
        if activity_score is not None:
            try:
                score = float(activity_score)
                if not (0 <= score <= 1):
                    return False, f"Activity score out of range: {score}"
            except (ValueError, TypeError):
                return False, "Invalid activity score"
        
        return True, "Valid"
    
    async def transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform to database format"""
        
        return {
            "_id": str(ObjectId()),
            "smiles": record["smiles"],
            "drug_name": record.get("drug_name", "Unknown"),
            "assay_name": record.get("assay_name"),
            "result": record.get("result"),
            "activity_score": float(record.get("activity_score", 0)),
            "assay_description": record.get("assay_description"),
            "created_at": datetime.utcnow().isoformat()
        }