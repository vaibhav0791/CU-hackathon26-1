import asyncio
import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base_ingestor import BaseIngestor
from bson import ObjectId

logger = logging.getLogger(__name__)

class UniProtIngestor(BaseIngestor):
    """Ingest protein sequences from UniProt"""
    
    def __init__(self, protein_list: Optional[List[str]] = None):
        super().__init__("uniprot_sequences")
        self.protein_list = protein_list or [
            "P05362",  # ICAM1
            "P08183",  # ABCB1 (MDR1)
            "Q92959",  # ERG
            "P35968",  # KRAS
            "P04637",  # TP53
        ]
        self.base_url = "https://rest.uniprot.org/uniprotkb"
        self.timeout = 15.0
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch protein sequences from UniProt API"""
        
        proteins = []
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for i, uniprot_id in enumerate(self.protein_list):
                try:
                    logger.info(f"[{i+1}/{len(self.protein_list)}] Fetching UniProt ID: {uniprot_id}")
                    
                    url = f"{self.base_url}/{uniprot_id}.json"
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        entry = data.get("entry", {})
                        
                        # Extract protein info
                        protein = {
                            "uniprot_id": uniprot_id,
                            "protein_name": self._extract_protein_name(entry),
                            "gene_name": self._extract_gene_name(entry),
                            "organism": self._extract_organism(entry),
                            "sequence": entry.get("sequence", {}).get("value", ""),
                            "function": self._extract_function(entry),
                            "source": "UniProt"
                        }
                        
                        proteins.append(protein)
                        logger.info(f"✅ Retrieved {protein['protein_name']}")
                    
                    elif response.status_code == 404:
                        logger.warning(f"⚠️ UniProt ID {uniprot_id} not found")
                    
                    elif response.status_code == 429:
                        logger.warning("⏳ Rate limited. Waiting...")
                        await asyncio.sleep(5)
                        continue
                    
                    await asyncio.sleep(0.5)
                
                except Exception as e:
                    logger.error(f"❌ Error fetching {uniprot_id}: {type(e).__name__}: {e}")
                    continue
        
        return proteins
    
    def _extract_protein_name(self, entry: Dict) -> str:
        """Extract protein name from UniProt entry"""
        protein_names = entry.get("proteinDescription", {}).get("recommendedName", {})
        return protein_names.get("fullName", {}).get("value", "Unknown")
    
    def _extract_gene_name(self, entry: Dict) -> str:
        """Extract gene name from UniProt entry"""
        genes = entry.get("genes", [])
        if genes and "geneName" in genes[0]:
            return genes[0]["geneName"].get("value", "Unknown")
        return "Unknown"
    
    def _extract_organism(self, entry: Dict) -> str:
        """Extract organism from UniProt entry"""
        organism = entry.get("organism", {})
        return organism.get("names", [{}])[0].get("value", "Unknown")
    
    def _extract_function(self, entry: Dict) -> str:
        """Extract protein function from UniProt entry"""
        comments = entry.get("comments", [])
        for comment in comments:
            if comment.get("commentType") == "FUNCTION":
                return comment.get("texts", [{}])[0].get("value", "")
        return ""
    
    async def validate_record(self, record: Dict[str, Any]) -> tuple:
        """Validate UniProt record"""
        
        if not record.get("uniprot_id"):
            return False, "Missing UniProt ID"
        
        if not record.get("sequence"):
            return False, "Missing protein sequence"
        
        if len(record["sequence"]) < 10:
            return False, "Sequence too short"
        
        return True, "Valid"
    
    async def transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform to database format"""
        
        return {
            "_id": str(ObjectId()),
            "uniprot_id": record["uniprot_id"],
            "protein_name": record.get("protein_name"),
            "gene_name": record.get("gene_name"),
            "organism": record.get("organism"),
            "sequence": record.get("sequence"),
            "sequence_length": len(record.get("sequence", "")),
            "function": record.get("function"),
            "created_at": datetime.utcnow().isoformat()
        }