from pydantic import Field
from beanie import Document
from pymongo import ASCENDING

class AnalysisBlueprint(Document):
    # Core drug data
    drug_name: str = Field(..., description="Name of the medicine")
    smiles: str = Field(..., description="Universal chemical language string")
    
    # Task V-4: Validation (The Gatekeeper)
    # This ensures the AI doesn't save "garbage" data
    solubility_score: float = Field(0.0, ge=0, le=100)
    bcs_class: str = Field(..., pattern="^(I|II|III|IV)$") 
    
    # Task V-2: Data Pipeline Enrichment
    confidence_score: float = Field(0.0, description="AI prediction confidence")

    # Tell Beanie which collection to use in the database
    class Settings:
        name = "analyses"
        
        # ✅ V-1 COMPLETE: MongoDB Indexes for Fast Queries
        indexes = [
            # Single-field indexes (most common queries)
            "smiles",              # For V-7: Redis cache lookup by SMILES
            "drug_name",           # For user searches by drug name
            "bcs_class",           # For filtering drugs by BCS class
            
            # Compound indexes (combined field queries)
            [("smiles", ASCENDING), ("bcs_class", ASCENDING)],  # Find drug + verify its class
        ]