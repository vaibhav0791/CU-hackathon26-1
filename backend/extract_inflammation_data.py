# backend/extract_inflammation_data.py
import asyncio
import json
import httpx
from run_discovery_audit import PharmaAIDiscoveryAudit
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import Crippen

async def run_inflammation_extraction():
    print("⚡ CDO Data Engine: Initializing TARGETED PTGS2 Inflammation Pathway Extraction...")
    audit_engine = PharmaAIDiscoveryAudit()
    
    # Target CHEMBL230 (Human COX-2 / PTGS2), the master driver for anti-inflammatory assays
    url = "https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id=CHEMBL230&limit=100&format=json"
    
    print("📡 Requesting direct bioactivities for inflammation target COX-2 (CHEMBL230)...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url)
            if response.status_code != 200:
                print(f"❌ Failed to reach ChEMBL API. Status: {response.status_code}")
                return
                
            activities = response.json().get("activities", []) or response.json().get("results", [])
            print(f"📥 Successfully received {len(activities)} raw inflammation assays from ChEMBL.")
            
            pristine_inflammation_records = []
            seen_in_this_batch = set()
            
            # Process and calculate real RDKit numbers on-the-fly!
            for act in activities:
                smiles = act.get("canonical_smiles")
                chembl_id = act.get("molecule_chembl_id")
                
                if smiles and chembl_id:
                    # Filter against historical database duplicates
                    if smiles in audit_engine.already_trained_smiles:
                        continue
                        
                    uid = audit_engine.generate_structural_hash(smiles)
                    if uid not in seen_in_this_batch:
                        seen_in_this_batch.add(uid)
                        
                        # Calculate exact Molecular Weight and LogP numbers natively
                        try:
                            mol = Chem.MolFromSmiles(smiles)
                            mw = round(Descriptors.MolWt(mol), 2) if mol else 0.0
                            logp = round(Crippen.MolLogP(mol), 2) if mol else 0.0
                        except:
                            mw, logp = 0.0, 0.0

                        pristine_inflammation_records.append({
                            "pharma_uid": uid,
                            "smiles": smiles,
                            "chembl_id": chembl_id,
                            "pubchem_cid": "Ingested via Inflammation Target Gateway",
                            "molecular_weight": mw,
                            "log_p": logp,
                            "assay_context": act.get("assay_description", "PTGS2/COX-2 Inflammation Assay"),
                            "ingestion_timestamp": "2026-06-07T01:15:00Z"
                        })
            
            # Save the clean final file for Damini
            output_file = "inflammation_data_for_damini_final.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(pristine_inflammation_records, f, indent=2)
                
            print("\n" + "="*60)
            print("🏁 INFLAMMATION TARGETED EXTRACTION COMPLETE!")
            print(f"📈 Total Clean Inflammation Records Found: {len(pristine_inflammation_records)}")
            print(f"💾 File Saved To: {output_file}")
            print("="*60)
            print("👉 Ready for your final bulk GitHub push or to send via WhatsApp!")
            
        except Exception as e:
            print(f"❌ Extraction error: {e}")

if __name__ == "__main__":
    asyncio.run(run_inflammation_extraction())