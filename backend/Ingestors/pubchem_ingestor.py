import asyncio
import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base_ingestor import BaseIngestor
from bson import ObjectId

logger = logging.getLogger(__name__)

class PubChemIngestor(BaseIngestor):
    """Ingest molecular properties from PubChem API"""
    
    def __init__(self, drug_list: Optional[List[str]] = None):
        super().__init__("pubchem_properties")
        self.drug_list = drug_list or []
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        self.timeout = 15.0
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch properties from PubChem for given compounds"""
        if not self.drug_list:
            logger.warning("⚠️ No drugs provided for PubChem fetch")
            return []
        
        properties = []
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for i, cid in enumerate(self.drug_list):
                try:
                    logger.info(f"[{i+1}/{len(self.drug_list)}] Fetching PubChem CID: {cid}")
                    
                    # Get compound properties
                    url = f"{self.base_url}/compound/cid/{cid}/property/MolecularWeight,LogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,CanonicalSMILES/JSON"
                    
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        props = data["PropertyTable"]["Properties"][0]
                        
                        properties.append({
                            "cid": cid,
                            "smiles": props.get("CanonicalSMILES"),
                            "molecular_weight": props.get("MolecularWeight"),
                            "log_p": props.get("LogP"),
                            "h_bond_donors": props.get("HBondDonorCount"),
                            "h_bond_acceptors": props.get("HBondAcceptorCount"),
                            "rotatable_bonds": props.get("RotatableBondCount"),
                            "topological_psa": props.get("TPSA"),
                            "source": "PubChem"
                        })
                        logger.info(f"✅ Retrieved properties for CID {cid}")
                    
                    elif response.status_code == 404:
                        logger.warning(f"⚠️ CID {cid} not found in PubChem")
                    
                    elif response.status_code == 429:
                        logger.warning(f"⏳ Rate limited. Waiting 5 seconds...")
                        await asyncio.sleep(5)
                        continue
                    
                    # Rate limiting
                    await asyncio.sleep(0.5)
                
                except Exception as e:
                    logger.error(f"❌ Error fetching CID {cid}: {type(e).__name__}: {e}")
                    continue
        
        return properties
    
    async def validate_record(self, record: Dict[str, Any]) -> tuple:
        """Validate PubChem record"""
        
        # Check required fields
        if not record.get("smiles"):
            return False, "Missing SMILES string"
        
        if not record.get("cid"):
            return False, "Missing CID"
        
        # Validate molecular weight
        mw = record.get("molecular_weight")
        if mw and (mw < 10 or mw > 2000):
            return False, f"Invalid molecular weight: {mw}"
        
        return True, "Valid"
    
    async def transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform to database format"""
        
        drug_name = record.get("drug_name", f"PubChem_{record['cid']}")
        
        return {
            "_id": str(ObjectId()),
            "cid": record["cid"],
            "smiles": record["smiles"],
            "drug_name": drug_name,
            "molecular_weight": record.get("molecular_weight"),
            "log_p": record.get("log_p"),
            "h_bond_donors": record.get("h_bond_donors"),
            "h_bond_acceptors": record.get("h_bond_acceptors"),
            "rotatable_bonds": record.get("rotatable_bonds"),
            "topological_psa": record.get("topological_psa"),
            "created_at": datetime.utcnow().isoformat()
        }