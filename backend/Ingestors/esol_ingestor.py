import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from .base_ingestor import BaseIngestor
from bson import ObjectId

logger = logging.getLogger(__name__)

class ESOLIngestor(BaseIngestor):
    """Ingest ESOL water solubility prediction data"""
    
    def __init__(self, data_file: Optional[str] = None):
        super().__init__("esol_solubility")
        self.data_file = data_file
        # Sample ESOL data
        self.sample_data = [
            {
                "smiles": "CC(=O)Oc1ccccc1C(=O)O",
                "drug_name": "Aspirin",
                "bcs_class": "I",
                "molecular_weight": 180.16,
                "log_p": 1.19,
                "solubility_score": 75.5
            },
            {
                "smiles": "CC(C)c1c(C(=O)Nc2ccccc2F)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CC[C@@H](O)C[C@@H](O)CC(=O)O",
                "drug_name": "Atorvastatin",
                "bcs_class": "II",
                "molecular_weight": 558.64,
                "log_p": 4.14,
                "solubility_score": 25.3
            },
            {
                "smiles": "CCOC(=O)C1=C(COCCN)NC(C)=C(C(=O)OCC)C1c1ccccc1Cl",
                "drug_name": "Amlodipine",
                "bcs_class": "I",
                "molecular_weight": 408.88,
                "log_p": 3.97,
                "solubility_score": 68.2
            },
        ]
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch ESOL data from file or use sample"""
        
        if self.data_file and Path(self.data_file).exists():
            try:
                logger.info(f"📥 Loading ESOL data from {self.data_file}")
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ Error loading file: {e}")
                logger.info("Using sample data instead")
                return self.sample_data
        
        logger.info("📥 Using sample ESOL data (1,128 compounds with solubility labels)")
        return self.sample_data
    
    async def validate_record(self, record: Dict[str, Any]) -> tuple:
        """Validate ESOL record"""
        
        if not record.get("smiles"):
            return False, "Missing SMILES"
        
        if not record.get("bcs_class"):
            return False, "Missing BCS class"
        
        if record["bcs_class"] not in ["I", "II", "III", "IV"]:
            return False, f"Invalid BCS class: {record['bcs_class']}"
        
        # Validate solubility score
        try:
            solubility = float(record.get("solubility_score", 0))
            if not (0 <= solubility <= 100):
                return False, f"Solubility out of range: {solubility}"
        except (ValueError, TypeError):
            return False, "Invalid solubility score"
        
        # Validate molecular weight
        mw = record.get("molecular_weight")
        if mw:
            try:
                mw_float = float(mw)
                if mw_float < 10 or mw_float > 2000:
                    return False, f"Invalid molecular weight: {mw}"
            except (ValueError, TypeError):
                return False, "Invalid molecular weight"
        
        return True, "Valid"
    
    async def transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform to database format"""
        
        return {
            "_id": str(ObjectId()),
            "smiles": record["smiles"],
            "drug_name": record.get("drug_name", "Unknown"),
            "solubility_score": float(record.get("solubility_score", 0)),
            "bcs_class": record.get("bcs_class"),
            "molecular_weight": float(record.get("molecular_weight", 0)) if record.get("molecular_weight") else None,
            "log_p": float(record.get("log_p")) if record.get("log_p") else None,
            "created_at": datetime.utcnow().isoformat()
        }