import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from .base_ingestor import BaseIngestor
from bson import ObjectId

logger = logging.getLogger(__name__)

class GRASIngestor(BaseIngestor):
    """Ingest FDA GRAS (Generally Recognized As Safe) excipients"""
    
    def __init__(self, data_file: Optional[str] = None):
        super().__init__("gras_excipients")
        self.data_file = data_file
        # Sample GRAS excipients
        self.sample_data = [
            {
                "name": "Microcrystalline Cellulose",
                "fda_registry_number": "9004-34-6",
                "cas_number": "9004-34-6",
                "category": "Binder & Diluent",
                "max_usage": "up to 90%",
                "compatible_with": ["tablets", "capsules", "powders"]
            },
            {
                "name": "Lactose Monohydrate",
                "fda_registry_number": "5989-81-1",
                "cas_number": "5989-81-1",
                "category": "Diluent & Binder",
                "max_usage": "up to 80%",
                "compatible_with": ["tablets", "capsules"]
            },
            {
                "name": "Magnesium Stearate",
                "fda_registry_number": "557-04-0",
                "cas_number": "557-04-0",
                "category": "Lubricant",
                "max_usage": "0.5-5%",
                "compatible_with": ["tablets", "capsules", "powders"]
            },
            {
                "name": "Croscarmellose Sodium",
                "fda_registry_number": "74811-65-7",
                "cas_number": "74811-65-7",
                "category": "Disintegrant",
                "max_usage": "1-5%",
                "compatible_with": ["tablets", "capsules"]
            },
            {
                "name": "Sodium Starch Glycolate",
                "fda_registry_number": "9005-84-9",
                "cas_number": "9005-84-9",
                "category": "Disintegrant",
                "max_usage": "2-8%",
                "compatible_with": ["tablets", "capsules"]
            },
        ]
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch GRAS excipient data from file or use sample"""
        
        if self.data_file and Path(self.data_file).exists():
            try:
                logger.info(f"📥 Loading GRAS data from {self.data_file}")
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ Error loading file: {e}")
                logger.info("Using sample data instead")
                return self.sample_data
        
        logger.info("📥 Using sample GRAS excipient data (500+ excipients in FDA GRAS list)")
        return self.sample_data
    
    async def validate_record(self, record: Dict[str, Any]) -> tuple:
        """Validate GRAS excipient record"""
        
        if not record.get("name"):
            return False, "Missing excipient name"
        
        if not record.get("category"):
            return False, "Missing category"
        
        # Validate category is reasonable
        valid_categories = [
            "Binder", "Diluent", "Disintegrant", "Lubricant",
            "Glidant", "Colorant", "Preservative", "Emulsifier"
        ]
        
        if not any(cat in record.get("category", "") for cat in valid_categories):
            logger.warning(f"⚠️ Unusual category: {record.get('category')}")
        
        return True, "Valid"
    
    async def transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform to database format"""
        
        compatible_with = record.get("compatible_with", [])
        
        return {
            "_id": str(ObjectId()),
            "name": record["name"],
            "fda_registry_number": record.get("fda_registry_number"),
            "cas_number": record.get("cas_number"),
            "category": record.get("category"),
            "max_usage": record.get("max_usage"),
            "compatible_with": json.dumps(compatible_with) if compatible_with else None,
            "created_at": datetime.utcnow().isoformat()
        }