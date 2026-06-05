# backend/fetchers/base_fetcher.py
"""Base fetcher class for all data sources"""
import logging
import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseFetcher:
    """Base class for all pharmaceutical data fetchers"""
    
    def __init__(self, db_path: str = None, cache_dir: str = None):
        self.db_path = db_path
        self.cache_dir = cache_dir or "ingestion_cache"
        self.cache_file = None
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            logger.info(f"✅ Created cache directory: {self.cache_dir}")
    
    def _get_cache_path(self, dataset_name: str) -> str:
        """Get cache file path for dataset"""
        return os.path.join(self.cache_dir, f"{dataset_name}_{datetime.now().strftime('%Y%m%d')}.json")
    
    def _load_from_cache(self, dataset_name: str) -> Optional[List[Dict[str, Any]]]:
        """Load data from local cache"""
        cache_path = self._get_cache_path(dataset_name)
        
        try:
            # Look for any cached file for this dataset
            cache_files = [f for f in os.listdir(self.cache_dir) if f.startswith(dataset_name)]
            
            if cache_files:
                latest_cache = os.path.join(self.cache_dir, sorted(cache_files)[-1])
                with open(latest_cache, 'r') as f:
                    data = json.load(f)
                    logger.info(f"✅ Loaded {len(data)} records from cache: {latest_cache}")
                    return data
        except Exception as e:
            logger.warning(f"⚠️ Could not load from cache: {e}")
        
        return None
    
    def _save_to_cache(self, dataset_name: str, data: List[Dict[str, Any]]):
        """Save data to local cache"""
        try:
            cache_path = self._get_cache_path(dataset_name)
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"✅ Cached {len(data)} records to: {cache_path}")
        except Exception as e:
            logger.warning(f"⚠️ Could not save to cache: {e}")
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """
        Main fetch method - override in subclasses
        Returns list of dictionaries with fetched data
        """
        raise NotImplementedError("Subclasses must implement fetch()")
    
    async def fetch_from_api(self) -> List[Dict[str, Any]]:
        """Fetch data from external API - override in subclasses"""
        raise NotImplementedError("Subclasses must implement fetch_from_api()")
    
    def _add_metadata(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add metadata to records"""
        for record in records:
            if 'ingestion_date' not in record:
                record['ingestion_date'] = datetime.now().isoformat()
        return records