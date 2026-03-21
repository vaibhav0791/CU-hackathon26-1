from pydantic import Field, ConfigDict
from beanie import Document
from pymongo import ASCENDING
from datetime import datetime
from typing import Optional

class AnalysisBlueprint(Document):
    """✅ Drug Analysis Data Model - MongoDB Document"""
    
    # Core drug data
    drug_name: str = Field(..., description="Name of the medicine", min_length=1)
    smiles: str = Field(..., description="Universal chemical language string", min_length=1)
    
    # Validation scores (V-4: The Gatekeeper)
    solubility_score: float = Field(0.0, ge=0.0, le=100.0, description="Solubility percentage score")
    confidence_score: float = Field(0.0, ge=0.0, le=100.0, description="AI prediction confidence")
    bcs_class: str = Field(..., description="BCS Classification (I, II, III, or IV)")
    
    # Timestamps for audit trail
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When analysis was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="When analysis was last updated")
    
    # Optional metadata
    molecular_weight: Optional[float] = Field(None, ge=0, description="Molecular weight in g/mol")
    dose_mg: Optional[float] = Field(None, ge=0, description="Recommended dose in mg")
    notes: Optional[str] = Field(None, description="Additional notes about the analysis")
    
    # ✅ FIXED: Pydantic V2 ConfigDict instead of class Config
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "drug_name": "Aspirin",
                "smiles": "CC(=O)Oc1ccccc1C(=O)O",
                "solubility_score": 75.5,
                "confidence_score": 85.0,
                "bcs_class": "I",
                "molecular_weight": 180.16
            }
        }
    )
    
    class Settings:
        """✅ MongoDB Collection Configuration"""
        name = "analyses"
        
        # ✅ V-1 COMPLETE: MongoDB Indexes for Fast Queries
        indexes = [
            # Single-field indexes (most common queries)
            ("smiles",),              # For V-7: Cache lookup by SMILES
            ("drug_name",),           # For user searches by drug name
            ("bcs_class",),           # For filtering drugs by BCS class
            ("created_at",),          # For time-based queries
            
            # Compound indexes (combined field queries)
            [("smiles", ASCENDING), ("bcs_class", ASCENDING)],  # Find drug + verify class
            [("drug_name", ASCENDING), ("created_at", ASCENDING)],  # Drug history
        ]
    
    def __str__(self) -> str:
        return f"Analysis({self.drug_name}, BCS: {self.bcs_class})"