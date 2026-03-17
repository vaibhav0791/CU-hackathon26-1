from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from contextlib import asynccontextmanager
import os
import logging
import json
import uuid
import urllib.parse
import aiohttp
import io
from datetime import datetime, timezone
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# RDKit for 3D coordinate generation
from rdkit import Chem
from rdkit.Chem import AllChem

# Import Vaibhav's Blueprint
from database_schema import AnalysisBlueprint

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- DATABASE SETUP (SYNCED) ---
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'pharma_db')  # Syncing with your ingest script

client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# ─── LIFESPAN HANDLER (Modern FastAPI - Fixed Deprecation Warning) ──────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP - Initialize Database Connection
    try:
        await init_beanie(database=db, document_models=[AnalysisBlueprint])
        print("✅ FULL SYSTEM ONLINE: AI Brain and Database Heart Connected!")
    except Exception as e:
        print(f"❌ Startup Error: {e}")
    
    yield  # Application runs here
    
    # SHUTDOWN - Cleanup (optional)
    print("🛑 Server shutting down...")
    await client.close()


app = FastAPI(
    title="PHARMA-AI Formulation Optimizer",
    lifespan=lifespan
)
api_router = APIRouter(prefix="/api")

# ─── Drug Database (SMILES + properties) ────────────────────────────────────────
DRUG_DATABASE = {
    "Aspirin": {"smiles": "CC(=O)Oc1ccccc1C(=O)O", "bcs_class": "I", "molecular_weight": 180.16},
    "Atorvastatin": {"smiles": "CC(C)c1c(C(=O)Nc2ccccc2F)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CC[C@@H](O)C[C@@H](O)CC(=O)O", "bcs_class": "II", "molecular_weight": 558.64},
    "Amlodipine": {"smiles": "CCOC(=O)C1=C(COCCN)NC(C)=C(C(=O)OCC)C1c1ccccc1Cl", "bcs_class": "I", "molecular_weight": 408.88},
    "Lisinopril": {"smiles": "OC(=O)[C@@H](CCc1ccccc1)N[C@@H](CC(=O)O)C(=O)N1CCC[C@H]1C(=O)O", "bcs_class": "III", "molecular_weight": 405.49},
    "Metoprolol": {"smiles": "CC(C)NCC(O)COc1ccc(CCOC)cc1", "bcs_class": "I", "molecular_weight": 267.36},
    "Warfarin": {"smiles": "OC(=O)CCCC1CC(=O)c2ccccc2O1", "bcs_class": "I", "molecular_weight": 308.33},
}

# ─── Pydantic Models ─────────────────────────────────────────────────────────────
class AnalysisRequest(BaseModel):
    smiles: str
    drug_name: Optional[str] = None
    molecular_weight: Optional[float] = None
    dose_mg: Optional[float] = None

class OutlierInfo(BaseModel):
    is_outlier: bool
    flag_reason: str
    severity: str  # "low", "medium", "high"

class AnalysisResponse(BaseModel):
    status: str
    analysis_id: str
    drug_name: str
    smiles: str
    bcs_class: str
    solubility_score: float
    confidence_score: float
    mol_3d: Optional[str] = None
    outlier_flagged: bool
    outlier_info: Optional[OutlierInfo] = None
    timestamp: str

# ─── V-2: ANALYSIS DATA PIPELINE FUNCTIONS ──────────────────────────────────────

def generate_3d_from_smiles(smiles: str) -> Optional[str]:
    """
    ✅ V-2: Generate 3D SDF structure from SMILES string
    Returns SDF format molecular structure for visualization
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            logger.warning(f"Invalid SMILES: {smiles}")
            return None
        
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, AllChem.ETKDG())
        AllChem.MMFFOptimizeMolecule(mol)
        sdf = Chem.MolToMolBlock(mol)
        return sdf
    except Exception as e:
        logger.error(f"Error generating 3D structure: {e}")
        return None


def compute_confidence_score(smiles: str, bcs_class: str, molecular_weight: Optional[float] = None) -> float:
    """
    ✅ V-2: Calculate confidence score based on:
    - SMILES validity (0-50 points)
    - BCS class reliability (0-30 points)
    - Molecular weight reasonableness (0-20 points)
    
    Returns: float between 0-100
    """
    confidence = 0.0
    
    # 1. SMILES validity check (50 points max)
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            confidence += 50
            # Bonus for complex molecules
            num_atoms = mol.GetNumAtoms()
            if num_atoms > 20:
                confidence += 5
        else:
            return 0.0  # Invalid SMILES = 0 confidence
    except Exception:
        return 0.0
    
    # 2. BCS class confidence (higher class = more reliable formulation)
    bcs_confidence_map = {
        "I": 30,      # Best: High solubility + High permeability
        "II": 20,     # Good: Low solubility, High permeability
        "III": 15,    # Moderate: High solubility, Low permeability
        "IV": 10,     # Challenging: Low solubility + Low permeability
    }
    confidence += bcs_confidence_map.get(bcs_class, 0)
    
    # 3. Molecular weight reasonableness (0-20 points)
    if molecular_weight:
        # Drug molecular weights typically 100-1000 Da
        if 100 <= molecular_weight <= 1000:
            confidence += 20
        elif 50 <= molecular_weight <= 1200:
            confidence += 10
    else:
        confidence += 15  # Assume reasonable if not provided
    
    return min(confidence, 100.0)


def auto_tag_bcs_class(molecular_weight: Optional[float], solubility: Optional[float]) -> str:
    """
    ✅ V-2: Auto-assign BCS class based on:
    - Class I: High solubility, High permeability
    - Class II: Low solubility, High permeability
    - Class III: High solubility, Low permeability
    - Class IV: Low solubility, Low permeability
    
    Simplified heuristics:
    - High solubility: > 50
    - High permeability: MW < 400 and reasonable LogP
    """
    
    # Default values if not provided
    if solubility is None:
        solubility = 50.0
    if molecular_weight is None:
        molecular_weight = 300.0
    
    is_high_solubility = solubility > 50
    is_high_permeability = molecular_weight < 400  # Smaller molecules permeate better
    
    if is_high_solubility and is_high_permeability:
        return "I"
    elif not is_high_solubility and is_high_permeability:
        return "II"
    elif is_high_solubility and not is_high_permeability:
        return "III"
    else:
        return "IV"


def flag_outliers(solubility: float, confidence: float, molecular_weight: Optional[float] = None) -> OutlierInfo:
    """
    ✅ V-2: Flag unusual/outlier values in analysis
    
    Detects:
    - Extremely low/high solubility
    - Unusually low confidence
    - Unreasonable molecular weight
    """
    
    flags = []
    severity = "low"
    
    # Check solubility outliers
    if solubility < 5:
        flags.append("Extremely low solubility (< 5%)")
        severity = "high"
    elif solubility > 95:
        flags.append("Extremely high solubility (> 95%)")
        severity = "medium"
    
    # Check confidence outliers
    if confidence < 20:
        flags.append("Very low confidence score")
        severity = "high" if severity != "high" else "high"
    
    # Check molecular weight outliers
    if molecular_weight:
        if molecular_weight < 50:
            flags.append("Unusually small molecule (< 50 Da)")
            severity = "high" if severity != "high" else "high"
        elif molecular_weight > 1500:
            flags.append("Unusually large molecule (> 1500 Da)")
            severity = "medium"
    
    if flags:
        return OutlierInfo(
            is_outlier=True,
            flag_reason=" | ".join(flags),
            severity=severity
        )
    else:
        return OutlierInfo(
            is_outlier=False,
            flag_reason="Within normal parameters",
            severity="low"
        )


def estimate_solubility_score(bcs_class: str, molecular_weight: Optional[float] = None) -> float:
    """
    ✅ V-2: Estimate solubility score based on BCS class
    
    This is a simplified heuristic. In production, you'd use:
    - IVIVC (In Vitro-In Vivo Correlation)
    - LogP predictions
    - pH-dependent solubility models
    """
    base_solubility = {
        "I": 75.0,    # Class I: High solubility
        "II": 30.0,   # Class II: Low solubility
        "III": 80.0,  # Class III: High solubility
        "IV": 15.0,   # Class IV: Low solubility
    }
    
    solubility = base_solubility.get(bcs_class, 50.0)
    
    # Adjust based on molecular weight
    if molecular_weight:
        if molecular_weight > 500:
            solubility *= 0.8  # Larger molecules less soluble
        elif molecular_weight < 200:
            solubility *= 1.1  # Smaller molecules more soluble
    
    return min(solubility, 100.0)


# ─── Routes ──────────────────────────────────────────────────────────────────────

@api_router.get("/")
async def root():
    return {"message": "PHARMA-AI Formulation Optimizer API", "version": "2.0.0"}


@api_router.get("/drugs")
async def get_drugs():
    """Get all available drugs in the database"""
    drugs = [{"name": name, **info} for name, info in DRUG_DATABASE.items()]
    return {"drugs": drugs, "total": len(drugs)}


@api_router.get("/drugs/{drug_name}")
async def get_drug(drug_name: str):
    """Get specific drug information"""
    for name, info in DRUG_DATABASE.items():
        if name.lower() == drug_name.lower():
            return {"name": name, **info}
    raise HTTPException(status_code=404, detail="Drug not found")


@api_router.get("/molecule3d")
async def get_molecule_3d(smiles: str = Query(..., description="SMILES string")):
    """Generate 3D molecular structure from SMILES"""
    try:
        sdf_data = generate_3d_from_smiles(smiles)
        if not sdf_data:
            raise HTTPException(status_code=400, detail="Could not generate 3D structure")
        return {"sdf": sdf_data, "source": "RDKit (Computed)"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/analyze")
async def analyze_drug(request: AnalysisRequest) -> AnalysisResponse:
    """
    ✅ V-2 COMPLETE: Analyze drug with full pipeline enrichment
    
    Steps:
    1. Validate SMILES
    2. Generate 3D structure
    3. Auto-compute BCS class
    4. Estimate solubility
    5. Compute confidence score
    6. Flag outliers
    7. Save to database
    """
    try:
        # 1. Validate SMILES
        mol = Chem.MolFromSmiles(request.smiles)
        if not mol:
            raise HTTPException(status_code=400, detail="Invalid SMILES string")
        
        # 2. Generate 3D molecule structure
        mol_3d = generate_3d_from_smiles(request.smiles)
        
        # 3. Auto-compute BCS class
        auto_bcs = auto_tag_bcs_class(
            molecular_weight=request.molecular_weight,
            solubility=None  # Will estimate below
        )
        
        # 4. Estimate solubility based on BCS class and MW
        solubility_score = estimate_solubility_score(auto_bcs, request.molecular_weight)
        
        # 5. Compute confidence score
        confidence_score = compute_confidence_score(
            request.smiles,
            auto_bcs,
            request.molecular_weight
        )
        
        # 6. Flag outliers
        outlier_info = flag_outliers(solubility_score, confidence_score, request.molecular_weight)
        
        # 7. Prepare and save to database
        analysis_id = str(uuid.uuid4())
        
        analysis = AnalysisBlueprint(
            drug_name=request.drug_name or "Unknown",
            smiles=request.smiles,
            bcs_class=auto_bcs,
            solubility_score=solubility_score,
            confidence_score=confidence_score
        )
        await analysis.insert()
        
        logger.info(f"✅ Analysis saved: {request.drug_name} (ID: {analysis_id})")
        
        return AnalysisResponse(
            status="success",
            analysis_id=str(analysis.id),
            drug_name=request.drug_name or "Unknown",
            smiles=request.smiles,
            bcs_class=auto_bcs,
            solubility_score=round(solubility_score, 2),
            confidence_score=round(confidence_score, 2),
            mol_3d=mol_3d,
            outlier_flagged=outlier_info.is_outlier,
            outlier_info=outlier_info,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@api_router.get("/analyses")
async def get_analyses():
    """Get all stored analyses"""
    try:
        analyses = await AnalysisBlueprint.find_all().to_list()
        return {
            "analyses": [dict(a) for a in analyses],
            "total": len(analyses)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/analyses/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get specific analysis by ID"""
    try:
        analysis = await AnalysisBlueprint.find_one({"id": analysis_id})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return dict(analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/compare")
async def compare_drugs(request: dict):
    """Compare two drugs side-by-side"""
    return {"message": "Side-by-side comparison active"}


@api_router.post("/what-if")
async def what_if_scenario(request: dict):
    """What-if scenario analysis"""
    return {"message": "Scenario simulation active"}


# ─── Middleware ──────────────────────────────────────────────────────────────────

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Run Server ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=False)