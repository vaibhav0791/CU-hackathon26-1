import asyncio
import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base_ingestor import BaseIngestor
from bson import ObjectId

logger = logging.getLogger(__name__)

class ClinicalTrialsIngestor(BaseIngestor):
    """Ingest clinical trial data from ClinicalTrials.gov API"""
    
    def __init__(self, condition: str = "cancer", status: str = "RECRUITING"):
        super().__init__("clinical_trials")
        self.condition = condition
        self.status = status
        self.base_url = "https://clinicaltrials.gov/api/v2/studies"
        self.timeout = 20.0
        self.page_size = 100
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch clinical trial data from ClinicalTrials.gov"""
        
        trials = []
        page_token = None
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while len(trials) < 500:  # Limit to 500 trials
                try:
                    logger.info(f"📥 Fetching clinical trials page...")
                    
                    params = {
                        "query.cond": self.condition,
                        "query.status": self.status,
                        "pageSize": self.page_size,
                        "countTotal": True
                    }
                    
                    if page_token:
                        params["pageToken"] = page_token
                    
                    response = await client.get(self.base_url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        studies = data.get("studies", [])
                        
                        if not studies:
                            logger.info("✅ No more trials found")
                            break
                        
                        for study in studies:
                            protocol = study.get("protocolSection", {})
                            trial = {
                                "nct_id": protocol.get("identificationModule", {}).get("nctId"),
                                "title": protocol.get("identificationModule", {}).get("officialTitle"),
                                "condition": self.condition,
                                "phase": self._extract_phase(protocol),
                                "status": protocol.get("statusModule", {}).get("overallStatus"),
                                "enrollment": protocol.get("designModule", {}).get("enrollmentInfo", {}).get("count"),
                                "start_date": protocol.get("statusModule", {}).get("startDateStruct", {}).get("date"),
                                "primary_outcome": self._extract_primary_outcome(protocol),
                                "source": "ClinicalTrials.gov"
                            }
                            trials.append(trial)
                        
                        logger.info(f"✅ Retrieved {len(studies)} trials (total: {len(trials)})")
                        
                        # Check for next page
                        page_token = data.get("nextPageToken")
                        if not page_token:
                            break
                        
                        await asyncio.sleep(1)
                    
                    else:
                        logger.error(f"❌ API error: {response.status_code}")
                        break
                
                except Exception as e:
                    logger.error(f"❌ Error fetching trials: {type(e).__name__}: {e}")
                    break
        
        return trials
    
    def _extract_phase(self, protocol: Dict) -> str:
        """Extract trial phase"""
        phases = protocol.get("designModule", {}).get("phases", [])
        return phases[0] if phases else "Unknown"
    
    def _extract_primary_outcome(self, protocol: Dict) -> str:
        """Extract primary outcome"""
        outcomes = protocol.get("outcomesModule", {}).get("primaryOutcomes", [])
        if outcomes:
            return outcomes[0].get("measure", "")
        return ""
    
    async def validate_record(self, record: Dict[str, Any]) -> tuple:
        """Validate clinical trial record"""
        
        if not record.get("nct_id"):
            return False, "Missing NCT ID"
        
        if not record.get("title"):
            return False, "Missing trial title"
        
        return True, "Valid"
    
    async def transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform to database format"""
        
        return {
            "_id": str(ObjectId()),
            "nct_id": record["nct_id"],
            "title": record.get("title"),
            "drug_name": "Unknown",  # Not always available
            "condition": record.get("condition"),
            "phase": record.get("phase"),
            "status": record.get("status"),
            "enrollment": record.get("enrollment"),
            "start_date": record.get("start_date"),
            "primary_outcome": record.get("primary_outcome"),
            "adverse_events": None,
            "created_at": datetime.utcnow().isoformat()
        }