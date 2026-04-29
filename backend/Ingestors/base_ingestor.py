import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseIngestor(ABC):
    """Base class for all dataset ingestors"""
    
    def __init__(self, dataset_type: str):
        self.dataset_type = dataset_type
        self.total_records = 0
        self.processed_records = 0
        self.failed_records = 0
        self.errors: List[str] = []
    
    @abstractmethod
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch data from source (API, file, database)"""
        pass
    
    @abstractmethod
    async def validate_record(self, record: Dict[str, Any]) -> tuple:
        """Validate a single record. Returns (is_valid, error_message)"""
        pass
    
    @abstractmethod
    async def transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw record to standardized format"""
        pass
    
    async def ingest(self, dry_run: bool = False) -> Dict[str, Any]:
        """Main ingestion pipeline"""
        try:
            logger.info(f"🔄 Starting ingestion for {self.dataset_type}...")
            
            # Fetch data
            raw_data = await self.fetch_data()
            self.total_records = len(raw_data)
            logger.info(f"📥 Fetched {self.total_records} records")
            
            processed_records = []
            
            for i, record in enumerate(raw_data):
                # Validate
                is_valid, error_msg = await self.validate_record(record)
                if not is_valid:
                    self.failed_records += 1
                    self.errors.append(f"Record {i}: {error_msg}")
                    continue
                
                # Transform
                transformed = await self.transform_record(record)
                processed_records.append(transformed)
                self.processed_records += 1
            
            logger.info(f"✅ Processed: {self.processed_records} records")
            logger.info(f"❌ Failed: {self.failed_records} records")
            
            return {
                "status": "success",
                "dataset_type": self.dataset_type,
                "total_records": self.total_records,
                "processed_records": self.processed_records,
                "failed_records": self.failed_records,
                "errors": self.errors if self.errors else None,
                "dry_run": dry_run,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ Ingestion failed: {type(e).__name__}: {e}")
            return {
                "status": "error",
                "dataset_type": self.dataset_type,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }