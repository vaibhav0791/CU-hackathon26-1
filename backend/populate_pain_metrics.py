# backend/populate_pain_metrics.py
import json
import os
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import Crippen  # ✅ FIXED: Import the correct sub-module for logP

def process_and_populate_file():
    input_filename = "pain_data_for_damini.json"
    output_filename = "pain_data_for_damini_final.json"
    
    if not os.path.exists(input_filename):
        print(f"❌ Error: Cannot find {input_filename}. Did you run the extraction script first?")
        return

    print(f"🧬 Loading {input_filename} into RDKit Property Calculator Engine...")
    with open(input_filename, "r", encoding="utf-8") as f:
        compounds = json.load(f)

    updated_count = 0
    for comp in compounds:
        smiles = comp.get("smiles")
        if smiles:
            try:
                # Parse the SMILES string into an RDKit molecule object
                mol = Chem.MolFromSmiles(smiles)
                if mol:
                    # Calculate exact molecular properties locally
                    comp["molecular_weight"] = round(Descriptors.MolWt(mol), 2)
                    comp["log_p"] = round(Crippen.MolLogP(mol), 2)  # ✅ FIXED: Using native sub-module
                    updated_count += 1
            except Exception as e:
                print(f"⚠️ Could not compute properties for molecule {comp.get('chembl_id')}: {e}")
                comp["molecular_weight"] = 0.0
                comp["log_p"] = 0.0

    # Save the polished data package
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(compounds, f, indent=2)

    print("\n" + "="*65)
    print("🎯 METRICS POPULATION METRICS COMPLETE!")
    print(f"📈 Successfully calculated and populated numbers for {updated_count} compounds.")
    print(f"💾 File Saved To: {output_filename} -> Ready for Damini!")
    print("="*65)

if __name__ == "__main__":
    process_and_populate_file()