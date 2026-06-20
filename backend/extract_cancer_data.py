# backend/extract_pure_cancer_data.py
import asyncio
import json
import httpx
from run_discovery_audit import PharmaAIDiscoveryAudit
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import Crippen

async def fetch_paginated_target_data(client, target_name: str, target_id: str, max_records: int = 650) -> list:
    records = []
    offset = 0
    page_size = 100
    print(f"📡 Ingesting deep profile data for {target_name} ({target_id})...")
    
    while len(records) < max_records:
        url = f"https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id={target_id}&limit={page_size}&offset={offset}&format=json"
        try:
            response = await client.get(url, timeout=30.0)
            if response.status_code != 200:
                break
            data = response.json()
            activities = data.get("activities", []) or data.get("results", [])
            if not activities:
                break
            records.extend(activities)
            offset += page_size
            await asyncio.sleep(0.1)
        except Exception:
            break
    print(f"  📥 Harvested {len(records)} raw rows for {target_name}.")
    return records

async def run_cancer_extraction():
    print("⚡ CDO Data Engine: Initializing PURE HIGH-VOLUME Cancer Ingestion...")
    audit_engine = PharmaAIDiscoveryAudit()
    
    pristine_cancer_records = []
    seen_in_this_batch = set()
    
    async with httpx.AsyncClient() as client:
        raw_assays = await fetch_paginated_target_data(client, "Oncology EGFR Kinase", "CHEMBL203", max_records=650)
        
        for act in raw_assays:
            smiles = act.get("canonical_smiles")
            chembl_id = act.get("molecule_chembl_id")
            target_desc = act.get("assay_description", "").upper()
            
            if smiles and chembl_id:
                if smiles in audit_engine.already_trained_smiles:
                    continue
                
                # 🛡️ THE SECURITY SHIELD: Filter off-target toxicological side-screens
                blacklist_words = ["CARDIAC", "HEART", "CYTOTOXICITY", "HEPATOCYTE"]
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

                    # Strictly isolate small-molecule oncological candidates
                    if 150.0 < mw < 650.0:
                        pristine_cancer_records.append({
                            "pharma_uid": uid,
                            "smiles": smiles,
                            "chembl_id": chembl_id,
                            "pubchem_cid": "Ingested via Oncology EGFR Pathway",
                            "molecular_weight": mw,
                            "log_p": logp,
                            "assay_context": act.get("assay_description", "EGFR Cancer Kinase Inhibition Assay"),
                            "ingestion_timestamp": "2026-06-20T05:00:00Z"
                        })
                        
    output_file = "cancer_data_for_damini_final.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(pristine_cancer_records, f, indent=2)
        
    print("\n" + "="*70)
    print(f"📈 Total Flawless Cancer Records Generated: {len(pristine_cancer_records)}")
    print(f"💾 File Saved To: {output_file}")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(run_cancer_extraction())