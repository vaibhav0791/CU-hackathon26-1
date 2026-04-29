from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# ✅ Dataset Types
class DatasetType(str, Enum):
    CHEMBL_BIOACTIVITY = "chembl_bioactivity"
    PUBCHEM_PROPERTIES = "pubchem_properties"
    UNIPROT_SEQUENCES = "uniprot_sequences"
    PDB_STRUCTURES = "pdb_structures"
    CLINICAL_TRIALS = "clinical_trials"
    TOX21_TOXICITY = "tox21_toxicity"
    ESOL_SOLUBILITY = "esol_solubility"
    GRAS_EXCIPIENTS = "gras_excipients"

# ✅ ChEMBL Bioactivity Model
class ChEMBLBioactivity(BaseModel):
    """ChEMBL drug-target bioactivity data"""
    chembl_id: str = Field(..., description="ChEMBL compound ID")
    smiles: str = Field(..., description="SMILES string")
    drug_name: str = Field(..., description="Drug/compound name")
    target_name: str = Field(..., description="Protein target name")
    bioactivity_type: str = Field(..., description="IC50, EC50, Ki, etc.")
    bioactivity_value: float = Field(..., description="Bioactivity value (nM)")
    standard_units: str = Field(default="nM", description="Unit of measurement")
    assay_id: str = Field(..., description="Assay ID")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ✅ PubChem Molecular Properties Model
class PubChemProperty(BaseModel):
    """PubChem molecular properties"""
    cid: int = Field(..., description="PubChem Compound ID")
    smiles: str = Field(..., description="Canonical SMILES")
    drug_name: str = Field(..., description="Compound name")
    molecular_weight: float = Field(..., description="MW in g/mol")
    log_p: Optional[float] = Field(None, description="Partition coefficient")
    h_bond_donors: Optional[int] = Field(None, description="Hydrogen bond donors")
    h_bond_acceptors: Optional[int] = Field(None, description="Hydrogen bond acceptors")
    rotatable_bonds: Optional[int] = Field(None, description="Rotatable bonds")
    topological_psa: Optional[float] = Field(None, description="Topological polar surface area")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ✅ UniProt Protein Sequence Model
class UniProtSequence(BaseModel):
    """UniProt protein sequence data"""
    uniprot_id: str = Field(..., description="UniProt ID (e.g., P12345)")
    protein_name: str = Field(..., description="Protein name")
    gene_name: str = Field(..., description="Gene name")
    organism: str = Field(..., description="Organism (e.g., Homo sapiens)")
    sequence: str = Field(..., description="Amino acid sequence (FASTA)")
    sequence_length: int = Field(..., description="Length of sequence")
    function: Optional[str] = Field(None, description="Protein function")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ✅ PDB Structure Model
class PDBStructure(BaseModel):
    """RCSB PDB 3D structure data"""
    pdb_id: str = Field(..., description="PDB ID (e.g., 1A1B)")
    title: str = Field(..., description="Structure title")
    protein_name: str = Field(..., description="Protein name")
    resolution: Optional[float] = Field(None, description="Resolution in Angstroms")
    release_date: str = Field(..., description="Release date")
    ligands: Optional[List[str]] = Field(None, description="Bound ligands")
    pdb_file_url: str = Field(..., description="URL to download PDB file")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ✅ Clinical Trial Model
class ClinicalTrial(BaseModel):
    """ClinicalTrials.gov trial metadata"""
    nct_id: str = Field(..., description="NCT ID (e.g., NCT04123456)")
    title: str = Field(..., description="Trial title")
    drug_name: str = Field(..., description="Drug being tested")
    condition: str = Field(..., description="Medical condition")
    phase: str = Field(..., description="Trial phase (1, 2, 3, 4)")
    status: str = Field(..., description="Trial status (recruiting, active, completed, etc.)")
    enrollment: Optional[int] = Field(None, description="Number of participants")
    start_date: Optional[str] = Field(None, description="Start date")
    primary_outcome: Optional[str] = Field(None, description="Primary outcome measure")
    adverse_events: Optional[List[str]] = Field(None, description="Reported adverse events")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ✅ Tox21 Toxicity Model
class Tox21Toxicity(BaseModel):
    """Tox21 toxicity assay data"""
    smiles: str = Field(..., description="SMILES string")
    drug_name: str = Field(..., description="Compound name")
    assay_name: str = Field(..., description="Toxicity assay name")
    result: str = Field(..., description="Active/Inactive/Inconclusive")
    activity_score: float = Field(..., description="Activity score (0-1)")
    assay_description: Optional[str] = Field(None, description="Assay description")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ✅ ESOL Solubility Model
class ESOLSolubility(BaseModel):
    """ESOL water solubility prediction data"""
    smiles: str = Field(..., description="SMILES string")
    drug_name: str = Field(..., description="Compound name")
    solubility_score: float = Field(..., ge=0, le=100, description="Solubility percentage (0-100)")
    bcs_class: str = Field(..., description="BCS class (I, II, III, IV)")
    molecular_weight: float = Field(..., description="MW in g/mol")
    log_p: Optional[float] = Field(None, description="LogP value")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ✅ GRAS Excipient Model
class GRASExcipient(BaseModel):
    """FDA GRAS (Generally Recognized As Safe) excipients"""
    name: str = Field(..., description="Excipient name")
    fda_registry_number: Optional[str] = Field(None, description="FDA registry number")
    cas_number: Optional[str] = Field(None, description="CAS number")
    category: str = Field(..., description="Category (e.g., stabilizer, emulsifier, etc.)")
    max_usage: Optional[str] = Field(None, description="Maximum recommended usage")
    compatible_with: Optional[List[str]] = Field(None, description="Compatible with drug types")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ✅ Dataset Ingestion Status Model
class DatasetIngestionStatus(BaseModel):
    """Track ingestion progress"""
    dataset_type: DatasetType
    status: str = Field(..., description="pending/in_progress/completed/failed")
    total_records: int = Field(default=0)
    processed_records: int = Field(default=0)
    failed_records: int = Field(default=0)
    error_message: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
class DatasetMetadata(BaseModel):
    """Metadata for stored datasets"""
    dataset_type: DatasetType
    total_records: int
    last_updated: datetime
    source_url: str
    description: str
    version: str = "1.0"