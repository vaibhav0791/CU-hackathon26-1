"""
Pydantic models for Target Discovery API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class UniProtSequence(BaseModel):
    """UniProt protein sequence data"""
    uniprot_id: str
    gene_name: str
    protein_name: str
    organism: str
    length: int
    molecular_weight: float
    fasta: str
    function: str
    disease_association: List[str]
    subcellular_location: str
    post_translational_modifications: List[str]


class BindingSite(BaseModel):
    """PDB binding site information"""
    ligand: str
    chain: str
    residues: List[str]


class PDBStructure(BaseModel):
    """RCSB PDB protein structure"""
    pdb_id: str
    title: str
    organism: str
    method: str
    resolution: float
    chains: List[str]
    protein_name: str
    uniprot_id: str
    biological_process: str
    binding_sites: List[BindingSite]
    pdb_file_url: str
    structure_quality: str


class SignificantGene(BaseModel):
    """Gene expression data"""
    gene_symbol: str
    fold_change: float
    p_value: float
    expression_level: str


class GEOExpression(BaseModel):
    """GEO gene expression dataset"""
    geo_id: str
    title: str
    organism: str
    disease: str
    tissue: str
    samples: int
    platform: str
    genes_analyzed: int
    significant_genes: List[SignificantGene]
    url: str


class ProteinInteraction(BaseModel):
    """STRING DB protein-protein interaction"""
    interacting_protein: str
    uniprot_id: str
    confidence_score: float
    interaction_type: str


class StringInteractions(BaseModel):
    """STRING DB protein interaction network"""
    protein_name: str
    uniprot_id: str
    string_id: str
    interactions: List[ProteinInteraction]
    network_nodes: int
    interaction_count: int


class TargetDiscoveryDatasetInfo(BaseModel):
    """Target discovery dataset information"""
    description: str
    total_records: int
    data_format: str
    url: str
    endpoint: str