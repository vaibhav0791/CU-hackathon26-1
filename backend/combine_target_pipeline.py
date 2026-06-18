# CU-hackathon26/backend/combine_target_pipeline.py
import json
import os

def combine_target_discovery_data():
    print("🚀 STEP 4 INITIALIZED: Executing Cross-Join Target Unification Pipeline...\n")
    
    pdb_file = "pdb_step_output.json"
    string_file = "string_step_output.json"
    geo_file = "geo_step_output.json"
    output_file = "target_discovery_master.json"
    
    # Safety Check: Ensure all upstream steps have generated files
    if not (os.path.exists(pdb_file) and os.path.exists(string_file) and os.path.exists(geo_file)):
        print("❌ Error: Missing upstream step files! Please run step 1, 2, and 3 first.")
        return

    # Load data slices
    with open(pdb_file, "r", encoding="utf-8") as f:
        pdb_data = json.load(f)
    with open(string_file, "r", encoding="utf-8") as f:
        string_data = json.load(f)
    with open(geo_file, "r", encoding="utf-8") as f:
        geo_data = json.load(f)

    # Dictionary to hold the cross-joined master map (Gene Symbol as unique Key)
    master_pipeline_map = {}

    # 1. Map GEO Data first (sets up disease profile base)
    for item in geo_data:
        gene = item["gene_symbol"].upper()
        master_pipeline_map[gene] = {
            "target_uid": f"TGT_{gene}_2026",
            "gene_symbol": gene,
            "disease_association_matrix": item["geo_data"],
            "rcsb_pdb_structures": {},
            "string_protein_network": []
        }

    # 2. Cross-join PDB Structural Keys cleanly
    for item in pdb_data:
        gene = item["gene_symbol"].upper()
        if gene in master_pipeline_map:
            master_pipeline_map[gene]["rcsb_pdb_structures"] = {
                "uniprot_id": item.get("uniprot_id", "N/A"),
                "pdb_entry_ids": item.get("pdb_entry_ids", []),
                "status": item.get("status", "N/A")
            }

    # 3. Cross-join STRING DB Network Nodes cleanly
    for item in string_data:
        gene = item["gene_symbol"].upper()
        if gene in master_pipeline_map:
            master_pipeline_map[gene]["string_protein_network"] = item.get("string_network_partners", [])

    # Convert the deduplicated map back to a clean list structure
    unified_dataset = list(master_pipeline_map.values())

    # Write out the final master data asset
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(unified_dataset, f, indent=2)

    print("=" * 70)
    print("🏁 PIPELINE UNIFICATION COMPLETE!")
    print(f"🎯 Successfully cross-joined and deduplicated {len(unified_dataset)} Master Targets.")
    print(f"💾 Tech team master file saved to: {output_file}")
    print("=" * 70)

if __name__ == "__main__":
    combine_target_discovery_data()