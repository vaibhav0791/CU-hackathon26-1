"""
Pydantic models for Formulation API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class DrugbankInfo(BaseModel):
    """Drugbank drug information"""
    name: str
    smiles: str
    dosage_forms: List[str]
    routes: List[str]
    molecular_weight: float
    solubility: str
    pka: Optional[float] = None
    logp: Optional[float] = None
    metabolism: str
    half_life: str
    bioavailability: float


class SolubilityData(BaseModel):
    """ESOL solubility prediction"""
    compound: str
    smiles: str
    solubility_g_per_l: float
    solubility_mol_per_l: float
    log_solubility: float
    molecular_weight: float
    logp: float
    prediction_confidence: float
    solubility_classification: str


class ToxAssay(BaseModel):
    """Single Tox21 assay result"""
    active: bool
    score: float


class ToxicityProfile(BaseModel):
    """Tox21 toxicity assay data"""
    compound: str
    smiles: str
    assays: Dict[str, ToxAssay]
    overall_toxicity_risk: str  # LOW, MEDIUM, HIGH
    confidence: float


class Excipient(BaseModel):
    """GRAS-approved excipient"""
    name: str
    status: str
    usage: str
    max_percentage: float
    solubility: str
    compatibility: List[str]
    incompatibility: List[str]
    regulatory_status: str
    safety_data: str


class FormulationSuggestion(BaseModel):
    """Formulation recommendation"""
    drug_name: str
    dosage_form: str
    drugbank_info: Optional[DrugbankInfo] = None
    solubility_profile: Optional[SolubilityData] = None
    toxicity_profile: Optional[ToxicityProfile] = None
    recommended_excipients: List[Excipient]
    formulation_feasibility: str


class FormulationRequest(BaseModel):
    """Request for formulation analysis"""
    drug_name: str = Field(..., description="Drug name")
    smiles: str = Field(..., description="SMILES string")
    dosage_form: str = Field(default="Tablet", description="Target dosage form")