import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import json

from dataset_db import dataset_db
from dataset_models import DatasetType, DatasetIngestionStatus, DatasetMetadata
from Ingestors.pubchem_ingestor import PubChemIngestor
from Ingestors.chembl_ingestor import ChEMBLIngestor
from Ingestors.uniprot_ingestor import UniProtIngestor
from Ingestors.clinical_trials_ingestor import ClinicalTrialsIngestor
from Ingestors.tox21_ingestor import Tox21Ingestor
from Ingestors.esol_ingestor import ESOLIngestor
from Ingestors.gras_ingestor import GRASIngestor

logger = logging.getLogger(__name__)

class DatasetManager:
    """Central orchestration service for all datasets"""
    
    def __init__(self):
        self.db = dataset_db
        self.ingestors = {}
        self.ingestion_status: Dict[str, DatasetIngestionStatus] = {}
        self._register_ingestors()
    
    def _register_ingestors(self):
        """Register all available ingestors"""
        logger.info("📋 Registering dataset ingestors...")
        
        self.ingestors = {
            "pubchem_properties": PubChemIngestor,
            "chembl_bioactivity": ChEMBLIngestor,
            "uniprot_sequences": UniProtIngestor,
            "clinical_trials": ClinicalTrialsIngestor,
            "tox21_toxicity": Tox21Ingestor,
            "esol_solubility": ESOLIngestor,
            "gras_excipients": GRASIngestor,
        }
        
        logger.info(f"✅ Registered {len(self.ingestors)} ingestors")
    
    async def ingest_dataset(
        self,
        dataset_type: str,
        dry_run: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Trigger ingestion for a specific dataset
        
        Args:
            dataset_type: Type of dataset to ingest
            dry_run: If True, validate only without saving
            **kwargs: Additional arguments for specific ingestors
        
        Returns:
            Ingestion result with status and statistics
        """
        
        if dataset_type not in self.ingestors:
            return {
                "status": "error",
                "error": f"Unknown dataset type: {dataset_type}",
                "available_types": list(self.ingestors.keys())
            }
        
        try:
            logger.info(f"🚀 Starting ingestion for {dataset_type}...")
            
            # Create ingestor instance
            ingestor_class = self.ingestors[dataset_type]
            ingestor = ingestor_class(**kwargs)
            
            # Run ingestion
            result = await ingestor.ingest(dry_run=dry_run)
            
            # Save records if not dry run
            if not dry_run and result["status"] == "success":
                saved_count = await self._save_records(dataset_type, ingestor)
                result["saved_records"] = saved_count
                
                # Update metadata
                await self._update_metadata(dataset_type, ingestor, result)
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Ingestion failed: {type(e).__name__}: {e}")
            return {
                "status": "error",
                "dataset_type": dataset_type,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _save_records(self, dataset_type: str, ingestor) -> int:
        """Save processed records to database"""
        
        # Map dataset type to table name
        table_mapping = {
            "pubchem_properties": "pubchem_properties",
            "chembl_bioactivity": "chembl_bioactivity",
            "uniprot_sequences": "uniprot_sequences",
            "clinical_trials": "clinical_trials",
            "tox21_toxicity": "tox21_toxicity",
            "esol_solubility": "esol_solubility",
            "gras_excipients": "gras_excipients",
        }
        
        table_name = table_mapping.get(dataset_type)
        if not table_name:
            logger.error(f"❌ No table mapping for {dataset_type}")
            return 0
        
        # Save records (this is simplified - you'd need to extract from ingestor)
        saved_count = 0
        logger.info(f"💾 Saving records to {table_name}...")
        
        return saved_count
    
    async def _update_metadata(self, dataset_type: str, ingestor, result: Dict) -> None:
        """Update dataset metadata"""
        
        try:
            metadata = {
                "_id": f"metadata_{dataset_type}",
                "dataset_type": dataset_type,
                "total_records": result.get("processed_records", 0),
                "last_updated": datetime.utcnow().isoformat(),
                "source_url": self._get_source_url(dataset_type),
                "description": self._get_description(dataset_type),
                "version": "1.0"
            }
            
            self.db.insert_record("dataset_metadata", metadata)
            logger.info(f"✅ Updated metadata for {dataset_type}")
        
        except Exception as e:
            logger.error(f"❌ Error updating metadata: {e}")
    
    def _get_source_url(self, dataset_type: str) -> str:
        """Get source URL for dataset type"""
        sources = {
            "pubchem_properties": "https://pubchem.ncbi.nlm.nih.gov/",
            "chembl_bioactivity": "https://www.ebi.ac.uk/chembl/",
            "uniprot_sequences": "https://www.uniprot.org/",
            "clinical_trials": "https://clinicaltrials.gov/",
            "tox21_toxicity": "https://tripod.nih.gov/tox21/",
            "esol_solubility": "https://huggingface.co/datasets/deepchem/ESOL",
            "gras_excipients": "https://www.fda.gov/food/generally-recognized-safe-gras",
        }
        return sources.get(dataset_type, "")
    
    def _get_description(self, dataset_type: str) -> str:
        """Get description for dataset type"""
        descriptions = {
            "pubchem_properties": "Molecular properties (MW, LogP, H-bonds, TPSA) from PubChem API",
            "chembl_bioactivity": "Drug-target bioactivity data (IC50, EC50, Ki) from ChEMBL",
            "uniprot_sequences": "Protein amino acid sequences from UniProt",
            "clinical_trials": "Clinical trial metadata from ClinicalTrials.gov API",
            "tox21_toxicity": "Toxicity assay results across 12 assays for 12,000+ compounds",
            "esol_solubility": "Water solubility predictions for 1,128 compounds with BCS classification",
            "gras_excipients": "FDA GRAS (Generally Recognized As Safe) excipients for formulations",
        }
        return descriptions.get(dataset_type, "")
    
    async def get_ingestion_status(self, dataset_type: Optional[str] = None) -> Dict[str, Any]:
        """Get ingestion status for one or all datasets"""
        
        if dataset_type:
            status = self.ingestion_status.get(dataset_type)
            if status:
                return status.dict()
            else:
                return {
                    "dataset_type": dataset_type,
                    "status": "not_started",
                    "message": f"No ingestion started for {dataset_type}"
                }
        
        # Return status for all datasets
        return {
            dataset: status.dict() 
            for dataset, status in self.ingestion_status.items()
        }
    
    async def get_dataset_count(self, dataset_type: str) -> int:
        """Get total records in a dataset"""
        
        table_mapping = {
            "pubchem_properties": "pubchem_properties",
            "chembl_bioactivity": "chembl_bioactivity",
            "uniprot_sequences": "uniprot_sequences",
            "clinical_trials": "clinical_trials",
            "tox21_toxicity": "tox21_toxicity",
            "esol_solubility": "esol_solubility",
            "gras_excipients": "gras_excipients",
        }
        
        table_name = table_mapping.get(dataset_type)
        if table_name:
            return self.db.get_table_count(table_name)
        
        return 0
    
    async def query_by_smiles(self, smiles: str) -> Dict[str, Any]:
        """
        Query all datasets for a given SMILES string
        Returns: ChEMBL bioactivity, PubChem properties, Tox21 toxicity, ESOL solubility
        """
        
        results = {
            "smiles": smiles,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {}
        }
        
        # Query each dataset
        if chembl_result := self.db.query_by_smiles("chembl_bioactivity", smiles):
            results["data"]["chembl_bioactivity"] = chembl_result
        
        if pubchem_result := self.db.query_by_smiles("pubchem_properties", smiles):
            results["data"]["pubchem_properties"] = pubchem_result
        
        if tox21_result := self.db.query_by_smiles("tox21_toxicity", smiles):
            results["data"]["tox21_toxicity"] = tox21_result
        
        if esol_result := self.db.query_by_smiles("esol_solubility", smiles):
            results["data"]["esol_solubility"] = esol_result
        
        return results
    
    async def validate_formulation(self, excipient_list: List[str]) -> Dict[str, Any]:
        """
        Validate a formulation based on GRAS excipients
        
        Args:
            excipient_list: List of excipient names
        
        Returns:
            Validation result with compatibility info
        """
        
        validation = {
            "excipients": excipient_list,
            "valid": True,
            "warnings": [],
            "metadata": {}
        }
        
        for excipient in excipient_list:
            # Query GRAS database
            self.db.cursor.execute("SELECT * FROM gras_excipients WHERE name = ?", (excipient,))
            row = self.db.cursor.fetchone()
            
            if not row:
                validation["warnings"].append(f"Excipient '{excipient}' not found in GRAS list")
                validation["valid"] = False
            else:
                gras_data = dict(row)
                validation["metadata"][excipient] = {
                    "category": gras_data.get("category"),
                    "max_usage": gras_data.get("max_usage"),
                    "compatible_with": json.loads(gras_data.get("compatible_with", "[]"))
                }
        
        return validation
    
    async def get_solubility_prediction(self, smiles: str) -> Optional[Dict[str, Any]]:
        """Get solubility prediction from ESOL dataset"""
        
        result = self.db.query_by_smiles("esol_solubility", smiles)
        
        if result:
            return {
                "smiles": smiles,
                "solubility_score": result.get("solubility_score"),
                "bcs_class": result.get("bcs_class"),
                "molecular_weight": result.get("molecular_weight"),
                "log_p": result.get("log_p"),
                "source": "ESOL Dataset"
            }
        
        return None
    
    async def get_toxicity_profile(self, smiles: str) -> Optional[Dict[str, Any]]:
        """Get toxicity assay results from Tox21 dataset"""
        
        self.db.cursor.execute("SELECT * FROM tox21_toxicity WHERE smiles = ?", (smiles,))
        rows = self.db.cursor.fetchall()
        
        if rows:
            assays = [
                {
                    "assay_name": dict(row).get("assay_name"),
                    "result": dict(row).get("result"),
                    "activity_score": dict(row).get("activity_score")
                }
                for row in rows
            ]
            
            return {
                "smiles": smiles,
                "total_assays": len(assays),
                "assay_results": assays,
                "source": "Tox21"
            }
        
        return None
    
    async def get_bioactivity_data(self, drug_name: str) -> List[Dict[str, Any]]:
        """Get ChEMBL bioactivity data for a drug"""
        
        self.db.cursor.execute(
            "SELECT * FROM chembl_bioactivity WHERE drug_name LIKE ?",
            (f"%{drug_name}%",)
        )
        
        rows = self.db.cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def get_protein_info(self, uniprot_id: str) -> Optional[Dict[str, Any]]:
        """Get protein information from UniProt dataset"""
        
        result = self.db.query_by_smiles("uniprot_sequences", uniprot_id)
        # Note: This searches by ID, not SMILES - should use direct query instead
        
        self.db.cursor.execute(
            "SELECT * FROM uniprot_sequences WHERE uniprot_id = ?",
            (uniprot_id,)
        )
        row = self.db.cursor.fetchone()
        
        if row:
            data = dict(row)
            return {
                "uniprot_id": data.get("uniprot_id"),
                "protein_name": data.get("protein_name"),
                "gene_name": data.get("gene_name"),
                "organism": data.get("organism"),
                "sequence_length": data.get("sequence_length"),
                "function": data.get("function"),
                "source": "UniProt"
            }
        
        return None
    
    async def search_clinical_trials(
        self,
        condition: Optional[str] = None,
        status: Optional[str] = None,
        phase: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search clinical trials by criteria"""
        
        query = "SELECT * FROM clinical_trials WHERE 1=1"
        params = []
        
        if condition:
            query += " AND condition LIKE ?"
            params.append(f"%{condition}%")
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if phase:
            query += " AND phase = ?"
            params.append(phase)
        
        self.db.cursor.execute(query, params)
        rows = self.db.cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    async def get_dataset_stats(self) -> Dict[str, Any]:
        """Get statistics for all datasets"""
        
        stats = {
            "timestamp": datetime.utcnow().isoformat(),
            "datasets": {}
        }
        
        table_mapping = {
            "pubchem_properties": "pubchem_properties",
            "chembl_bioactivity": "chembl_bioactivity",
            "uniprot_sequences": "uniprot_sequences",
            "clinical_trials": "clinical_trials",
            "tox21_toxicity": "tox21_toxicity",
            "esol_solubility": "esol_solubility",
            "gras_excipients": "gras_excipients",
        }
        
        for dataset_type, table_name in table_mapping.items():
            count = self.db.get_table_count(table_name)
            stats["datasets"][dataset_type] = {
                "total_records": count,
                "table_name": table_name
            }
        
        total = sum(d["total_records"] for d in stats["datasets"].values())
        stats["total_records"] = total
        
        return stats

# Create global instance
dataset_manager = DatasetManager()