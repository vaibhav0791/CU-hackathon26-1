import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from dataset_manager import dataset_manager

logger = logging.getLogger(__name__)

class DatasetService:
    """High-level API for querying datasets"""
    
    @staticmethod
    async def get_compound_profile(smiles: str) -> Dict[str, Any]:
        """
        Get comprehensive compound profile from all datasets
        
        Returns:
        - PubChem properties (MW, LogP, H-bonds, TPSA)
        - ChEMBL bioactivity (IC50, EC50, Ki)
        - Tox21 toxicity assays
        - ESOL solubility prediction
        """
        
        profile = {
            "smiles": smiles,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {}
        }
        
        try:
            # Get all data for this SMILES
            all_data = await dataset_manager.query_by_smiles(smiles)
            profile["data"] = all_data.get("data", {})
            
            # Get solubility prediction
            solubility = await dataset_manager.get_solubility_prediction(smiles)
            if solubility:
                profile["data"]["solubility_prediction"] = solubility
            
            # Get toxicity profile
            toxicity = await dataset_manager.get_toxicity_profile(smiles)
            if toxicity:
                profile["data"]["toxicity_profile"] = toxicity
            
        except Exception as e:
            logger.error(f"Error building compound profile: {e}")
            profile["error"] = str(e)
        
        return profile
    
    @staticmethod
    async def get_drug_bioactivity(drug_name: str) -> Dict[str, Any]:
        """Get ChEMBL bioactivity data for a drug"""
        
        try:
            bioactivity_data = await dataset_manager.get_bioactivity_data(drug_name)
            
            return {
                "drug_name": drug_name,
                "total_assays": len(bioactivity_data),
                "bioactivity_data": bioactivity_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error fetching bioactivity: {e}")
            return {
                "drug_name": drug_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    async def get_target_info(uniprot_id: str) -> Dict[str, Any]:
        """Get UniProt protein information"""
        
        try:
            protein_info = await dataset_manager.get_protein_info(uniprot_id)
            
            if protein_info:
                return {
                    "status": "success",
                    "data": protein_info
                }
            else:
                return {
                    "status": "not_found",
                    "message": f"Protein {uniprot_id} not found"
                }
        
        except Exception as e:
            logger.error(f"Error fetching protein info: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @staticmethod
    async def validate_formulation(excipient_list: List[str]) -> Dict[str, Any]:
        """Validate formulation with GRAS excipients"""
        
        try:
            return await dataset_manager.validate_formulation(excipient_list)
        except Exception as e:
            logger.error(f"Error validating formulation: {e}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    @staticmethod
    async def search_trials(
        condition: Optional[str] = None,
        status: Optional[str] = None,
        phase: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search clinical trials"""
        
        try:
            trials = await dataset_manager.search_clinical_trials(
                condition=condition,
                status=status,
                phase=phase
            )
            
            return {
                "status": "success",
                "total_trials": len(trials),
                "trials": trials,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error searching trials: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @staticmethod
    async def get_all_stats() -> Dict[str, Any]:
        """Get statistics for all datasets"""
        
        try:
            return await dataset_manager.get_dataset_stats()
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }