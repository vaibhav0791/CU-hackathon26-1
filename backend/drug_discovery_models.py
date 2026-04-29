"""
Pydantic models for Drug Discovery API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class Bioactivity(BaseModel):
    """ChEMBL Bioactivity record"""
    target: str
    assay_type: str
    ic50_nm: Optional[float] = None
    pchembl_value: float


class ChEMBLCompound(BaseModel):
    """ChEMBL compound data"""
    chembl_id: str
    pref_name: str
    smiles: str
    molecular_weight: float
    logp: float
    bioactivities: List[Bioactivity]
    compound_type: str
    max_phase: int


class MolecularProperties(BaseModel):
    """PubChem molecular properties"""
    cid: int
    iupac_name: str
    smiles: str
    molecular_weight: float
    molecular_formula: str
    logp: float
    hbd: int  # Hydrogen bond donors
    hba: int  # Hydrogen bond acceptors
    rotatable_bonds: int
    topological_psa: float
    heavy_atom_count: int
    complexity: float


class ZINC15Compound(BaseModel):
    """ZINC15 purchasable compound"""
    zinc_id: str
    smiles: str
    name: str
    molecular_weight: float
    logp: float
    purchasable: bool
    supplier_count: int
    price_range: str
    availability: str


class QuantumProperties(BaseModel):
    """QM9 quantum mechanical properties"""
    energy_homo: float
    energy_lumo: float
    energy_gap: float
    total_energy: float
    dipole_moment: float
    polarizability: float
    zero_point_energy: float


class QM9Compound(BaseModel):
    """QM9 compound with quantum properties"""
    smiles: str
    name: str
    molecular_weight: float
    quantum_properties: QuantumProperties
    atoms: int
    bonds: int


class ChEMBLSearchRequest(BaseModel):
    """ChEMBL search request"""
    query: str = Field(..., description="Search query")
    search_type: str = Field(default="name", description="Search type: 'name', 'smiles', 'chembl_id'")


class ZINC15SearchRequest(BaseModel):
    """ZINC15 search request"""
    query: str = Field(..., description="Search query")
    filter_type: str = Field(default="name", description="Filter type: 'name', 'smiles', 'zinc_id'")


class DrugDiscoveryDatasetInfo(BaseModel):
    """Drug discovery dataset information"""
    description: str
    total_records: int
    data_format: str
    url: str
    endpoint: str