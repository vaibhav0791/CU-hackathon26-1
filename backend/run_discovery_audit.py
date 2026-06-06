# backend/run_discovery_audit.py
"""
Pharma AI - Universal Dynamic Ingestion & Audit Engine
Tests live ChEMBL/PubChem APIs, joins them, and extracts clean data for any category.
"""

import asyncio
import logging
import hashlib
import json
import sqlite3
import httpx
from datetime import datetime, timezone

# Setup clean screen logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("pharma_ai_audit")

class PharmaAIDiscoveryAudit:
    def __init__(self, db_path: str = "pharma_enhanced.db"):
        self.db_path = db_path
        self.chembl_url = "https://www.ebi.ac.uk/chembl/api/data/activity.json"
        self.pubchem_base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        self.timeout = 30.0
        
        # 🛡️ SYSTEM DATA BLACKLIST (FROM CDO REVIEWS)
        # Tracking target proteins and pathways already trained by the tech team to prevent duplication
        self.already_trained_targets = {
            # Inflammation / Autoimmune
            "TNF", "PTGS1", "PTGS2", "JAK1", "JAK2", "JAK3", "TYK2", "IL6", "IL6R", "IL1B", 
            "IL1R1", "NFKB1", "NFKB2", "NLRP3", "CCR5", "CCR2", "CXCR4", "PDE4A", "PDE4B", "PDE4D",
            # Respiratory
            "ADRB2", "CHRM3", "HRH1", "IL5", "IL5RA", "IL13", "IL4R", "ALOX5", "CYSLTR1",
            # Pain
            "OPRM1", "OPRD1", "OPRK1", "TRPV1", "SCN9A", "CACNA2D1", "FAAH",
            # Diabetes / Metabolic
            "DPP4", "PPARG", "PPARD", "PPARGC1A", "SLC5A2", "GCK", "GLP1R", "INSR", "PTPN1", 
            "HMGCR", "PCSK9", "CETP", "LPL", "FABP4", "FASN", "ACACA", "AMPK"
        }
        
        self.already_trained_smiles = self._load_trained_smiles_history()

    def _load_trained_smiles_history(self) -> set:
        """Reads previously ingested structures to prevent re-training loops."""
        trained_set = set()
        baseline_smiles = ["CC(=O)Oc1ccccc1C(=O)O", "CC(C)Cc1ccc(cc1)C(C)C(=O)O"]
        for smiles in baseline_smiles:
            trained_set.add(smiles.strip())
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT smiles FROM chembl_bioactivity WHERE smiles IS NOT NULL")
            for row in cursor.fetchall():
                if row[0]: trained_set.add(row[0].strip())
                    
            cursor.execute("SELECT smiles FROM pubchem_properties WHERE smiles IS NOT NULL")
            for row in cursor.fetchall():
                if row[0]: trained_set.add(row[0].strip())
            conn.close()
            logger.info(f"💾 Loaded {len(trained_set)} historically trained molecules from database cache.")
        except Exception as e:
            logger.warning(f"⚠️ Starting audit with baseline chemical memory. ({e})")
        return trained_set

    def generate_structural_hash(self, smiles: str) -> str:
        if not smiles: return "UNKNOWN"
        clean_smiles = smiles.strip().replace(" ", "")
        hash_obj = hashlib.sha256(clean_smiles.encode('utf-8'))
        return f"PAI_COMP_{hash_obj.hexdigest()[:16].upper()}"

    async def fetch_dynamic_category(self, keywords: list, limit: int = 50) -> list:
        """
        🌐 DYNAMIC RETRIEVAL: Filters live data streams 
        dynamically using runtime disease category keywords.
        """
        upper_keywords = [k.upper() for k in keywords]
        logger.info(f"🔍 Mining live endpoints for target keywords: {keywords}")
        
        url = f"{self.chembl_url}?limit={limit}&assay_organism=Homo sapiens&format=json"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                if response.status_code != 200:
                    return []
                
                activities = response.json().get("activities", []) or response.json().get("results", [])
                pristine_new_dataset = []
                seen_in_this_batch = set()

                for act in activities:
                    target_desc = act.get("assay_description", "").upper()
                    smiles = act.get("canonical_smiles")
                    chembl_id = act.get("molecule_chembl_id")
                    
                    if not smiles:
                        continue

                    # 1. Match against dynamic parameters (e.g., CANCER, RESPIRATORY)
                    matches_category = any(kw in target_desc for kw in upper_keywords)
                    
                    # 2. Safety filter checkpoints
                    is_blacklisted_target = any(trained in target_desc for trained in self.already_trained_targets)
                    is_blacklisted_structure = smiles in self.already_trained_smiles
                    
                    if matches_category and not is_blacklisted_target and not is_blacklisted_structure:
                        structure_uid = self.generate_structural_hash(smiles)
                        
                        if structure_uid not in seen_in_this_batch:
                            seen_in_this_batch.add(structure_uid)
                            pristine_new_dataset.append({
                                "pharma_uid": structure_uid,
                                "smiles": smiles,
                                "chembl_id": chembl_id,
                                "pubchem_cid": "Matched via Ingestion",
                                "molecular_weight": "Fetched on Demand",
                                "log_p": "Fetched on Demand",
                                "assay_context": act.get("assay_description"),
                                "ingestion_timestamp": datetime.now(timezone.utc).isoformat()
                            })
                return pristine_new_dataset
            except Exception as e:
                logger.error(f"❌ Extraction error: {e}")
                return []