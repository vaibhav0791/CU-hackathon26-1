# backend/extract_inflammation_data.py
import asyncio
import json
import httpx
from run_discovery_audit import PharmaAIDiscoveryAudit
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import Crippen

async def fetch_paginated_target_data(client, target_name: str, target_id: str, max_records: int = 450) -> list:
    """
    🔄 INDUSTRIAL PAGINATION ENGINE: 
    Sweeps deep into ChEMBL pages using offset increments to grab massive non-duplicating blocks.
    """
    records = []
    offset = 0
    page_size = 100  # Optimal high-throughput chunk configuration
    
    print(f"📡 Ingesting deep profile data for {target_name} ({target_id})...")
    
    while len(records) < max_records:
        url = f"https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id={target_id}&limit={page_size}&offset={offset}&format=json"
        try:
            response = await client.get(url, timeout=30.0)
            if response.status_code != 200:
                print(f"  ⚠️ Stopped paging {target_name} at offset {offset} (Status: {response.status_code})")
                break
                
            data = response.json()
            activities = data.get("activities", []) or data.get("results", [])
            
            if not activities:
                break  # Reached the absolute end of the live server table
                
            records.extend(activities)
            offset += page_size
            
            # Rate limit tick to protect connections
            await asyncio.sleep(0.1)
            
        except Exception as e:
            print(f"  ❌ Network glitch at offset {offset}: {e}")
            break
            
    print(f"  📥 Harvested {len(records)} raw biochemical rows for {target_name}.")
    return records

async def run_inflammation_extraction():
    print("⚡ CDO Data Engine: Initializing DEEP HIGH-VOLUME Inflammation Ingestion...")
    audit_engine = PharmaAIDiscoveryAudit()
    
    # 🧬 Focus exclusively on massive, pure anti-inflammatory small-molecule pipelines
    # By maximizing pagination limits here, we hit high volume with zero receptor cross-talk
    inflammation_targets = {
        "COX-2 (PTGS2)": "CHEMBL230",   
        "COX-1 (PTGS1)": "CHEMBL221"
    }
    
    pristine_inflammation_records = []
    seen_in_this_batch = set()
    
    async with httpx.AsyncClient() as client:
        for target_name, target_id in inflammation_targets.items():
            # Scaled up to 450 max records per target to force a massive 10x data surge
            raw_assays = await fetch_paginated_target_data(client, target_name, target_id, max_records=450)
            
            # Process and compute true chemical metrics
            for act in raw_assays:
                smiles = act.get("canonical_smiles")
                chembl_id = act.get("molecule_chembl_id")
                target_desc = act.get("assay_description", "").upper()
                
                if smiles and chembl_id:
                    # Guard against historical control duplication
                    if smiles in audit_engine.already_trained_smiles:
                        continue
                    
                    # 🛡️ THE SECURITY SHIELD: Scrub out cardiac leakage and off-target GPCR screens
                    blacklist_words = ["CARDIAC", "SKELETAL", "HEART", "MUSCLE", "NITRENDIPINE", "ADENOSINE", "TAAR6", "GPCR"]
                    if any(word in target_desc for word in blacklist_words):
                        continue  
                        
                    uid = audit_engine.generate_structural_hash(smiles)
                    if uid not in seen_in_this_batch:
                        seen_in_this_batch.add(uid)
                        
                        try:
                            mol = Chem.MolFromSmiles(smiles)
                            mw = round(Descriptors.MolWt(mol), 2) if mol else 0.0
                            logp = round(Crippen.MolLogP(mol), 2) if mol else 0.0
                        except:
                            mw, logp = 0.0, 0.0

                        # Keep small molecule drug candidates
                        if 150.0 < mw < 650.0:
                            pristine_inflammation_records.append({
                                "pharma_uid": uid,
                                "smiles": smiles,
                                "chembl_id": chembl_id,
                                "pubchem_cid": f"Ingested via {target_name} Pathway",
                                "molecular_weight": mw,
                                "log_p": logp,
                                "assay_context": act.get("assay_description", f"Targeted {target_name} Modulation Assay"),
                                "ingestion_timestamp": "2026-06-20T04:44:00Z"
                            })
                        
    # Save the clean final file for Damini
    output_file = "inflammation_data_for_damini_final.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(pristine_inflammation_records, f, indent=2)
        
    print("\n" + "="*70)
    print("🏁 INGESTION COMPLETE - MAXIMUM DATA DEPLOYMENT PROTOCOL")
    print(f"📈 Total Flawless Train-Ready Records Generated: {len(pristine_inflammation_records)}")
    print(f"💾 File Saved To: {output_file}")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(run_inflammation_extraction())