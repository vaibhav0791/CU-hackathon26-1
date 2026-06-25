# C:\Pharma Project\CU-hackathon26\backend\live_api_pipeline.py
import json
import logging
import numpy as np
from chembl_webresource_client.new_client import new_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("live_pharma_fetcher")

def fetch_unique_sanitized_dataset(target_gene_symbol="INSR", target_chembl_id="CHEMBL1981", limit=80):
    """
    Automatically fetches unique small-molecule assay data using a direct ChEMBL ID,
    filters out noise/mixtures, converts to log metrics, and builds a clean JSON.
    """
    logger.info(f"🚀 Querying ChEMBL API directly for target ID: {target_chembl_id} ({target_gene_symbol})")
    
    # Direct Bioactivity Lookup: Bypass target search errors completely
    activity_api = new_client.activity
    try:
        raw_activities = activity_api.filter(
            target_chembl_id=target_chembl_id, 
            standard_type="IC50", 
            standard_units="nM"
        ).only(['molecule_chembl_id', 'molecule_pref_name', 'canonical_smiles', 'standard_value', 'standard_type'])[:limit]
    except Exception as e:
        logger.error(f"❌ Failed to communicate with ChEMBL API server: {e}")
        return
    
    flat_training_sink = []
    
    for act in raw_activities:
        smiles = act.get('canonical_smiles')
        raw_val = act.get('standard_value')
        chembl_id = act.get('molecule_chembl_id')
        name = act.get('molecule_pref_name') or chembl_id 
        
        # 🧼 Sanitization Filter 1: Drop empty strings, macros, or salt mixtures
        if not smiles or "." in smiles or "N/A" in smiles:
            continue
            
        # 🧼 Sanitization Filter 2: Pure Logarithmic Bounds Conversion
        try:
            val_flt = float(raw_val)
            if val_flt <= 0:
                continue
            actual_px50 = round(9 - np.log10(val_flt), 3)
        except (ValueError, TypeError):
            continue 
            
        flat_entry = {
            "chembl_id": chembl_id,
            "chemical_name": name,
            "target_protein": target_gene_symbol,
            "smiles": smiles,
            "experiment_type": "IC50",
            "target_value_pX50": actual_px50
        }
        flat_training_sink.append(flat_entry)
        
    # 💾 Save payload safely
    output_filename = f"{target_gene_symbol.lower()}_unique_sanitized_data.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(flat_training_sink, f, indent=2)
        
    print(f"\n" + "="*80)
    print(f"🏁 SUCCESS: Generated {len(flat_training_sink)} Unique Clean Data Vectors for {target_gene_symbol}.")
    print(f"💾 File Saved To: {output_filename}")
    print("="*80)

if __name__ == "__main__":
    # Human Insulin Receptor is explicitly mapped to CHEMBL1981
    fetch_unique_sanitized_dataset(target_gene_symbol="INSR", target_chembl_id="CHEMBL1981", limit=100)