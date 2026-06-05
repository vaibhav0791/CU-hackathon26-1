# backend/run_discovery_audit.py
"""
Pharma AI - Isolated Discovery Dataset Pipeline & Audit Engine
Tests live ChEMBL/PubChem APIs, joins them, and blocks previously trained data.
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
        
        # In-memory structural cache to avoid retraining loops
        self.already_trained_smiles = self._load_trained_smiles_history()

    def _load_trained_smiles_history(self) -> set:
        """Reads previously ingested structures to prevent re-training loops."""
        trained_set = set()
        
        # Seed cache with known baseline control molecules (Aspirin & Ibuprofen structures)
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
            logger.info(f"💾 Loaded {len(trained_set)} historically trained molecules from your database cache.")
        except Exception as e:
            logger.warning(f"⚠️ Starting audit with baseline chemical memory. ({e})")
        return trained_set

    def generate_structural_hash(self, smiles: str) -> str:
        """Generates a permanent unique structure-based ID from SMILES."""
        if not smiles:
            return "UNKNOWN"
        clean_smiles = smiles.strip().replace(" ", "")
        hash_obj = hashlib.sha256(clean_smiles.encode('utf-8'))
        return f"PAI_COMP_{hash_obj.hexdigest()[:16].upper()}"

    async def test_and_fetch_chembl(self, limit: int = 5) -> list:
        """Step 1: Check ChEMBL API and pull active target compound metadata."""
        url = f"{self.chembl_url}?limit={limit}&assay_organism=Homo sapiens&format=json"
        logger.info(f"📡 Testing ChEMBL Connection... URL: {url}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    logger.info("✅ ChEMBL API Status: 200 OK (Pipeline functional)")
                    activities = response.json().get("activities", []) or response.json().get("results", [])
                    
                    extracted_compounds = []
                    for act in activities:
                        smiles = act.get("canonical_smiles")
                        chembl_id = act.get("molecule_chembl_id")
                        target_desc = act.get("assay_description", "Unknown Target")
                        
                        if smiles and chembl_id:
                            extracted_compounds.append({
                                "chembl_id": chembl_id,
                                "smiles": smiles,
                                "target": target_desc,
                                "bioactivity": f"{act.get('standard_value')} {act.get('standard_units', 'nM')}"
                            })
                    return extracted_compounds
                else:
                    logger.error(f"❌ ChEMBL API Connection Failed. Status: {response.status_code}")
                    return []
            except Exception as e:
                logger.error(f"❌ ChEMBL Pipeline Error: {e}")
                return []

    async def test_and_fetch_pubchem_properties(self, cid: int) -> dict:
        """Step 1 Continued: Check PubChem API for a sample profile lookup."""
        url = f"{self.pubchem_base_url}/compound/cid/{cid}/property/MolecularWeight,XLogP,CanonicalSMILES/JSON"
        logger.info(f"📡 Testing PubChem Connection... Fetching CID: {cid}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    logger.info("✅ PubChem API Status: 200 OK (Pipeline functional)")
                    props = response.json()["PropertyTable"]["Properties"][0]
                    return {
                        "pubchem_cid": cid,
                        "smiles": props.get("CanonicalSMILES"),
                        "molecular_weight": props.get("MolecularWeight"),
                        "log_p": props.get("XLogP")
                    }
                else:
                    logger.error(f"❌ PubChem API Connection Failed. Status: {response.status_code}")
                    return None
            except Exception as e:
                logger.error(f"❌ PubChem Pipeline Error: {e}")
                return None

    def join_and_deduplicate(self, chembl_list: list, pubchem_profile: dict) -> list:
        """Step 2 & 3: Joint datasets and filter out previously trained entries or pathways."""
        logger.info("\n🛡️ Running Joint Processing & Deep Deduplication Ingestion...")
        
        master_stream = []
        if chembl_list:
            master_stream.extend(chembl_list)
        if pubchem_profile and pubchem_profile.get("smiles"):
            master_stream.append(pubchem_profile)
            
        pristine_new_dataset = []
        skipped_old_training_count = 0
        seen_in_this_batch = set()

        for item in master_stream:
            smiles = item.get("smiles")
            target_info = item.get("target", "").upper()
            if not smiles:
                continue
                
            # A) BLOCK BASED ON TARGET GENE BLACKLIST
            # If descriptor text matches a trained target pathway from your screenshots, discard it
            is_blacklisted_target = any(trained_target in target_info for trained_target in self.already_trained_targets)
            
            # B) BLOCK BASED ON MOLECULAR STRUCTURE MEMORY
            is_blacklisted_structure = smiles in self.already_trained_smiles
            
            if is_blacklisted_target or is_blacklisted_structure:
                logger.warning(f"⏭️ [BLOCKED TRAINED DATA] Detected structural or target marker redundancy. Skipping record.")
                skipped_old_training_count += 1
                continue
                
            structure_uid = self.generate_structural_hash(smiles)
            
            if structure_uid not in seen_in_this_batch:
                seen_in_this_batch.add(structure_uid)
                
                joined_record = {
                    "pharma_uid": structure_uid,
                    "smiles": smiles,
                    "chembl_id": item.get("chembl_id", "N/A"),
                    "pubchem_cid": item.get("pubchem_cid", "N/A"),
                    "molecular_weight": item.get("molecular_weight", "Fetched on Demand"),
                    "log_p": item.get("log_p", "Fetched on Demand"),
                    "ingestion_timestamp": datetime.now(timezone.utc).isoformat()
                }
                pristine_new_dataset.append(joined_record)

        print("\n" + "="*80)
        print("🎯 PRISTINE DISCOVERY SNAPSHOT GENERATED (CHEMBL + PUBCHEM ONLY)")
        print("="*80)
        print(f"📈 Total New Pristine Entries for Tech Team: {len(pristine_new_dataset)}")
        print(f"🛑 Total Old Training Rows Blocked:         {skipped_old_training_count}")
        print("="*80)
        
        return pristine_new_dataset

async def main():
    logger.info("🚀 Starting Isolated Chief Data Officer Audit Pipeline...")
    audit_engine = PharmaAIDiscoveryAudit()
    
    # Run fetch commands
    chembl_data = await audit_engine.test_and_fetch_chembl(limit=5)
    pubchem_data = await audit_engine.test_and_fetch_pubchem_properties(cid=2244)
    
    # 🧪 CDO COLLISION INJECTION TEST: Simulating a dangerous redundant asset coming down the pipeline
    logger.info("\n🧪 Injecting old trained targets to verify boundary defenses...")
    old_trained_data_simulation = {
        "chembl_id": "CHEMBL_COLLISION_TEST",
        "smiles": "CC(=O)Oc1ccccc1C(=O)O",                      # Aspirin structure (blocked by chemical memory)
        "target": "Human Prostaglandin G/H synthase 2 (PTGS2) Assay" # Blocked by target protein name rule
    }
    chembl_data.append(old_trained_data_simulation)
    
    # Intercept data redundancy and format snapshot
    pristine_data = audit_engine.join_and_deduplicate(chembl_list=chembl_data, pubchem_profile=pubchem_data)
    
    if pristine_data:
        filename = "pharma_ai_discovery_v1.json"
        with open(filename, "w") as f:
            json.dump(pristine_data, f, indent=2)
        logger.info(f"💾 PRISTINE SNAPSHOT IMMUTABLY FROZEN TO: {filename}")

if __name__ == "__main__":
    asyncio.run(main())