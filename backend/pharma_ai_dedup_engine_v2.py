# pharma_ai_target_discovery_v2/pharma_ai_dedup_engine_v2.py
import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

try:
    from rdkit import Chem
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    logging.warning("⚠️ RDKit not found locally. Falling back to standard string hashing.")

logger = logging.getLogger("pharma_ai_dedup_v2")

class PharmaAIDedupEngineV2:
    @staticmethod
    def generate_canonical_chemical_hash(raw_smiles: str) -> str:
        if not raw_smiles:
            return "UNKNOWN_STRUCTURE"
        clean_smiles = raw_smiles.strip().replace(" ", "")
        if RDKIT_AVAILABLE:
            try:
                mol = Chem.MolFromSmiles(clean_smiles)
                if mol:
                    canonical_smiles = Chem.MolToSmiles(mol, canonical=True)
                    hash_obj = hashlib.sha256(canonical_smiles.encode('utf-8'))
                    return f"PAI_COMP_{hash_obj.hexdigest()[:16].upper()}"
            except Exception as e:
                logger.debug(f"RDKit standardization bypass for structure {clean_smiles}: {e}")
        hash_obj = hashlib.sha256(clean_smiles.encode('utf-8'))
        return f"PAI_COMP_{hash_obj.hexdigest()[:16].upper()}"

    @classmethod
    def consolidate_target_attributes(cls, raw_target_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        target_registry = {}
        for record in raw_target_records:
            uniprot_id = record.get("uniprot_id") or record.get("uniprot_accession")
            if not uniprot_id:
                gene_symbol = record.get("gene_symbol") or record.get("gene_name")
                uniprot_id = f"ORPHAN_{gene_symbol.upper()}" if gene_symbol else "UNKNOWN_TARGET_NODE"
            
            uniprot_id = uniprot_id.strip().upper()
            if uniprot_id not in target_registry:
                target_registry[uniprot_id] = {
                    "master_uniprot_id": uniprot_id,
                    "gene_symbol": record.get("gene_name") or record.get("gene_symbol") or "Unknown",
                    "amino_acid_sequence": None,
                    "structural_pdb_resolutions": [],
                    "expression_matrices": [],
                    "validated_interaction_partners": [],
                    "last_pushed_to_warehouse": datetime.now(timezone.utc).isoformat()
                }
            
            if "sequence" in record:
                target_registry[uniprot_id]["amino_acid_sequence"] = record["sequence"]
            if "pdb_entry_ids" in record:
                for pdb in record["pdb_entry_ids"]:
                    if pdb and pdb not in target_registry[uniprot_id]["structural_pdb_resolutions"]:
                        target_registry[uniprot_id]["structural_pdb_resolutions"].append(pdb)
            if "log2_fold_change" in record or "geo_dataset_gse" in record:
                target_registry[uniprot_id]["expression_matrices"].append({
                    "geo_id": record.get("geo_dataset_gse"),
                    "disease": record.get("associated_disease"),
                    "log2_fc": record.get("log2_fold_change"),
                    "p_value": record.get("p_value")
                })
            if "string_network_partners" in record:
                for partner in record["string_network_partners"]:
                    if partner and partner not in target_registry[uniprot_id]["validated_interaction_partners"]:
                        target_registry[uniprot_id]["validated_interaction_partners"].append(partner)
                        
        return list(target_registry.values())