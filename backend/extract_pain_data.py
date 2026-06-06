# backend/extract_pain_data.py
import asyncio
import json
import httpx
from run_discovery_audit import PharmaAIDiscoveryAudit

async def run_pain_extraction():
    print("⚡ CDO Data Engine: Initializing TARGETED TRPV1 Pain Pathway Extraction...")
    audit_engine = PharmaAIDiscoveryAudit()
    
    # Using TRPV1 (the core pain receptor) to force ChEMBL to give us target-rich rows
    search_target = "TRPV1"
    url = f"https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id=CHEMBL4794&limit=100&format=json"
    
    print(f"📡 Requesting direct bioactivities for core pain receptor TRPV1 (CHEMBL4794)...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url)
            if response.status_code != 200:
                print(f"❌ Failed to reach ChEMBL API. Status: {response.status_code}")
                return
                
            activities = response.json().get("activities", []) or response.json().get("results", [])
            print(f"📥 Successfully received {len(activities)} raw pain assays from ChEMBL.")
            
            # Re-routing your fresh arrays back through your secure CDO layout
            pristine_pain_records = []
            seen_in_this_batch = set()
            
            for act in activities:
                smiles = act.get("canonical_smiles")
                chembl_id = act.get("molecule_chembl_id")
                
                if smiles and chembl_id:
                    # Run structural checking against local DB history
                    if smiles in audit_engine.already_trained_smiles:
                        continue
                        
                    uid = audit_engine.generate_structural_hash(smiles)
                    if uid not in seen_in_this_batch:
                        seen_in_this_batch.add(uid)
                        pristine_pain_records.append({
                            "pharma_uid": uid,
                            "smiles": smiles,
                            "chembl_id": chembl_id,
                            "pubchem_cid": "Ingested via Target Gateway",
                            "molecular_weight": "Fetched on Demand",
                            "log_p": "Fetched on Demand",
                            "assay_context": act.get("assay_description", "TRPV1 Pain Receptor Modulation Assay"),
                            "ingestion_timestamp": "2026-06-06T22:40:00Z"
                        })
            
            # Save it explicitly for Damini
            output_file = "pain_data_for_damini.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(pristine_pain_records, f, indent=2)
                
            print("\n" + "="*60)
            print(f"🏁 TARGETED EXTRACTION COMPLETE!")
            print(f"📈 Total Clean Pain Records Found: {len(pristine_pain_records)}")
            print(f"💾 File Saved To: {output_file}")
            print("="*60)
            print("👉 You can now safely send this file to Damini for segregation!")
            
        except Exception as e:
            print(f"❌ Extraction error: {e}")

if __name__ == "__main__":
    asyncio.run(run_pain_extraction())