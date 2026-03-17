from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import json
import uuid
import io
import urllib.parse
import aiohttp
from datetime import datetime, timezone
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# RDKit for 3D coordinate generation (fallback when PubChem unavailable)
from rdkit import Chem
from rdkit.Chem import AllChem

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Setup logging first
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB setup - make it optional
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'pharma_ai')

# Try to connect to MongoDB, but don't fail if it's not available
try:
    client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
    db = client[db_name]
    # Test connection
    client.server_info()
    MONGODB_AVAILABLE = True
    logger.info("MongoDB connected successfully")
except Exception as e:
    logger.warning(f"MongoDB not available: {e}. Running without database.")
    MONGODB_AVAILABLE = False
    client = None
    db = None

app = FastAPI(title="PHARMA-AI Formulation Optimizer")
api_router = APIRouter(prefix="/api")

# ─── Drug Database (SMILES + properties) ────────────────────────────────────────
DRUG_DATABASE = {
    "Aspirin": {
        "smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "molecular_weight": 180.16,
        "molecular_formula": "C9H8O4",
        "logp": 1.19,
        "pka": 3.5,
        "bcs_class": "I",
        "therapeutic_class": "NSAID / Antiplatelet",
        "route": "Oral"
    },
    "Ibuprofen": {
        "smiles": "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
        "molecular_weight": 206.28,
        "molecular_formula": "C13H18O2",
        "logp": 3.97,
        "pka": 4.91,
        "bcs_class": "II",
        "therapeutic_class": "NSAID",
        "route": "Oral"
    },
    "Acetaminophen": {
        "smiles": "CC(=O)Nc1ccc(O)cc1",
        "molecular_weight": 151.16,
        "molecular_formula": "C8H9NO2",
        "logp": 0.46,
        "pka": 9.5,
        "bcs_class": "I",
        "therapeutic_class": "Analgesic / Antipyretic",
        "route": "Oral"
    },
    "Metformin": {
        "smiles": "CN(C)C(=N)NC(=N)N",
        "molecular_weight": 129.16,
        "molecular_formula": "C4H11N5",
        "logp": -1.43,
        "pka": 2.8,
        "bcs_class": "III",
        "therapeutic_class": "Antidiabetic (Biguanide)",
        "route": "Oral"
    },
    "Atorvastatin": {
        "smiles": "CC(C)c1c(C(=O)Nc2ccccc2F)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CC[C@@H](O)C[C@@H](O)CC(=O)O",
        "molecular_weight": 558.64,
        "molecular_formula": "C33H35FN2O5",
        "logp": 6.36,
        "pka": 4.46,
        "bcs_class": "II",
        "therapeutic_class": "Statin / Antilipidemic",
        "route": "Oral"
    },
    "Lisinopril": {
        "smiles": "OC(=O)[C@@H](CCc1ccccc1)N[C@@H](CC(=O)O)C(=O)N1CCC[C@H]1C(=O)O",
        "molecular_weight": 405.49,
        "molecular_formula": "C21H31N3O5",
        "logp": -1.54,
        "pka": 2.5,
        "bcs_class": "III",
        "therapeutic_class": "ACE Inhibitor / Antihypertensive",
        "route": "Oral"
    },
    "Omeprazole": {
        "smiles": "CC1=CN=C(C)C(CC2=NC3=CC=CC=C3N2)=C1",
        "molecular_weight": 345.42,
        "molecular_formula": "C17H19N3O3S",
        "logp": 2.23,
        "pka": 4.77,
        "bcs_class": "II",
        "therapeutic_class": "Proton Pump Inhibitor",
        "route": "Oral"
    },
    "Amoxicillin": {
        "smiles": "CC1(C)S[C@@H]2[C@H](NC(=O)[C@@H](N)c3ccc(O)cc3)C(=O)N2[C@H]1C(=O)O",
        "molecular_weight": 365.40,
        "molecular_formula": "C16H19N3O5S",
        "logp": 0.87,
        "pka": 2.4,
        "bcs_class": "I",
        "therapeutic_class": "Antibiotic (Penicillin)",
        "route": "Oral"
    },
    "Metoprolol": {
        "smiles": "CC(C)NCC(O)COc1ccc(CCOC)cc1",
        "molecular_weight": 267.36,
        "molecular_formula": "C15H25NO3",
        "logp": 1.88,
        "pka": 9.7,
        "bcs_class": "I",
        "therapeutic_class": "Beta-blocker / Antihypertensive",
        "route": "Oral"
    },
    "Simvastatin": {
        "smiles": "CCC(C)(C)C(=O)O[C@@H]1C[C@@H](C)C=C2C=C[C@H](C)[C@H](CC[C@@H]3C[C@@H](O)CC(=O)O3)[C@@H]12",
        "molecular_weight": 418.57,
        "molecular_formula": "C25H38O5",
        "logp": 4.68,
        "pka": 13.5,
        "bcs_class": "II",
        "therapeutic_class": "Statin / Antilipidemic",
        "route": "Oral"
    },
    "Amlodipine": {
        "smiles": "CCOC(=O)C1=C(COCCN)NC(C)=C(C(=O)OCC)C1c1ccccc1Cl",
        "molecular_weight": 408.88,
        "molecular_formula": "C20H25ClN2O5",
        "logp": 3.0,
        "pka": 8.6,
        "bcs_class": "I",
        "therapeutic_class": "Calcium Channel Blocker",
        "route": "Oral"
    },
    "Losartan": {
        "smiles": "CCCc1nc(-c2ccccc2Cl)c(-c2ccc(CN3C(=O)N(Cc4ccc(-c5ccccc5-c5nnn[nH]5)cc4)C3=S)cc2)o1",
        "molecular_weight": 422.91,
        "molecular_formula": "C22H23ClN6O",
        "logp": 4.01,
        "pka": 5.0,
        "bcs_class": "II",
        "therapeutic_class": "ARB / Antihypertensive",
        "route": "Oral"
    },
    "Warfarin": {
        "smiles": "OC(=O)CCCC1CC(=O)c2ccccc2O1",
        "molecular_weight": 308.33,
        "molecular_formula": "C19H16O4",
        "logp": 2.7,
        "pka": 5.05,
        "bcs_class": "I",
        "therapeutic_class": "Anticoagulant",
        "route": "Oral"
    },
    "Metronidazole": {
        "smiles": "Cc1ncc([N+](=O)[O-])n1CCO",
        "molecular_weight": 171.15,
        "molecular_formula": "C6H9N3O3",
        "logp": -0.02,
        "pka": 2.62,
        "bcs_class": "I",
        "therapeutic_class": "Antibiotic / Antiprotozoal",
        "route": "Oral"
    },
    "Ciprofloxacin": {
        "smiles": "OC(=O)c1cn(C2CC2)c2cc(N3CCNCC3)c(F)cc2c1=O",
        "molecular_weight": 331.34,
        "molecular_formula": "C17H18FN3O3",
        "logp": 0.28,
        "pka": 6.09,
        "bcs_class": "IV",
        "therapeutic_class": "Fluoroquinolone Antibiotic",
        "route": "Oral"
    },
    "Doxycycline": {
        "smiles": "OC1=C(C(=O)[C@H]2C[C@@H]3CC4=C(O)c5c(O)cccc5C(=O)[C@@]4(O)[C@H]3[C@H]2[C@@H]1C(N)=O)c(O)c1c(=C2)c(O)cccc1=O",
        "molecular_weight": 444.43,
        "molecular_formula": "C22H24N2O8",
        "logp": -0.02,
        "pka": 3.4,
        "bcs_class": "I",
        "therapeutic_class": "Tetracycline Antibiotic",
        "route": "Oral"
    },
    "Fluoxetine": {
        "smiles": "CNCCC(Oc1ccc(C(F)(F)F)cc1)c1ccccc1",
        "molecular_weight": 309.33,
        "molecular_formula": "C17H18F3NO",
        "logp": 4.05,
        "pka": 9.8,
        "bcs_class": "I",
        "therapeutic_class": "SSRI Antidepressant",
        "route": "Oral"
    },
    "Sertraline": {
        "smiles": "CNC1CCC(c2ccc(Cl)c(Cl)c2)c2ccccc21",
        "molecular_weight": 306.23,
        "molecular_formula": "C17H17Cl2N",
        "logp": 5.06,
        "pka": 9.47,
        "bcs_class": "II",
        "therapeutic_class": "SSRI Antidepressant",
        "route": "Oral"
    },
    "Alprazolam": {
        "smiles": "Cc1nnc2n1-c1ccc(Cl)cc1C(=Nc1ccccc1)CC2",
        "molecular_weight": 308.76,
        "molecular_formula": "C17H13ClN4",
        "logp": 2.12,
        "pka": 2.48,
        "bcs_class": "I",
        "therapeutic_class": "Benzodiazepine / Anxiolytic",
        "route": "Oral"
    },
    "Clopidogrel": {
        "smiles": "COC(=O)[C@@H](c1ccccc1Cl)N1CCc2sccc2C1",
        "molecular_weight": 321.82,
        "molecular_formula": "C16H16ClNO2S",
        "logp": 2.64,
        "pka": 4.55,
        "bcs_class": "I",
        "therapeutic_class": "Antiplatelet",
        "route": "Oral"
    },
    "Tamoxifen": {
        "smiles": "CCN(CC)/C=C/C(=C(\\c1ccccc1)/c1ccc(OCCN(CC)CC)cc1)c1ccccc1",
        "molecular_weight": 371.51,
        "molecular_formula": "C26H29NO",
        "logp": 6.3,
        "pka": 8.85,
        "bcs_class": "II",
        "therapeutic_class": "SERM / Anticancer",
        "route": "Oral"
    },
    "Morphine": {
        "smiles": "[C@@H]12[C@H]3CC4=CC(=C(O)C=C4[C@H]1[C@H](O)CC2)NC3",
        "molecular_weight": 285.34,
        "molecular_formula": "C17H19NO3",
        "logp": 0.9,
        "pka": 8.0,
        "bcs_class": "I",
        "therapeutic_class": "Opioid Analgesic",
        "route": "Oral / Parenteral"
    },
    "Gabapentin": {
        "smiles": "NCC1(CC(=O)O)CCCCC1",
        "molecular_weight": 171.24,
        "molecular_formula": "C9H17NO2",
        "logp": -1.1,
        "pka": 3.68,
        "bcs_class": "III",
        "therapeutic_class": "Anticonvulsant / Neuropathic Pain",
        "route": "Oral"
    },
    "Prednisolone": {
        "smiles": "[C@@]12(O)CC[C@H]3[C@@H](CCC4=CC(=O)C=C[C@@]34C)[C@@H]1CC[C@@H]2C(=O)CO",
        "molecular_weight": 360.44,
        "molecular_formula": "C21H28O5",
        "logp": 1.62,
        "pka": 12.6,
        "bcs_class": "I",
        "therapeutic_class": "Corticosteroid",
        "route": "Oral"
    },
    "Methotrexate": {
        "smiles": "CN(Cc1cnc2nc(N)nc(N)c2n1)c1ccc(CC(=O)O)cc1",
        "molecular_weight": 454.44,
        "molecular_formula": "C20H22N8O5",
        "logp": -1.85,
        "pka": 3.36,
        "bcs_class": "III",
        "therapeutic_class": "Antifolate / Anticancer",
        "route": "Oral / Parenteral"
    },
    "Furosemide": {
        "smiles": "NS(=O)(=O)c1cc(C(=O)O)c(NCc2ccco2)cc1Cl",
        "molecular_weight": 330.74,
        "molecular_formula": "C12H11ClN2O5S",
        "logp": 2.03,
        "pka": 3.9,
        "bcs_class": "IV",
        "therapeutic_class": "Loop Diuretic",
        "route": "Oral / IV"
    },
    "Hydrochlorothiazide": {
        "smiles": "NS(=O)(=O)c1cc2c(cc1Cl)NCNS2(=O)=O",
        "molecular_weight": 297.74,
        "molecular_formula": "C7H8ClN3O4S2",
        "logp": -0.07,
        "pka": 7.9,
        "bcs_class": "IV",
        "therapeutic_class": "Thiazide Diuretic",
        "route": "Oral"
    },
    "Levothyroxine": {
        "smiles": "NC(Cc1cc(I)c(Oc2cc(I)c(O)c(I)c2)c(I)c1)C(=O)O",
        "molecular_weight": 776.87,
        "molecular_formula": "C15H11I4NO4",
        "logp": 3.16,
        "pka": 2.2,
        "bcs_class": "II",
        "therapeutic_class": "Thyroid Hormone",
        "route": "Oral"
    },
    "Enalapril": {
        "smiles": "CCOC(=O)[C@@H](CCc1ccccc1)NC(C)C(=O)N1CCC[C@H]1C(=O)O",
        "molecular_weight": 376.45,
        "molecular_formula": "C20H28N2O5",
        "logp": 0.11,
        "pka": 3.0,
        "bcs_class": "III",
        "therapeutic_class": "ACE Inhibitor",
        "route": "Oral"
    },
    "Sildenafil": {
        "smiles": "CCCc1nn(C)c2c1nc(C)nc2N1CCN(Cc2ccc(S(=O)(=O)N3CCOCC3)cc2)CC1",
        "molecular_weight": 474.58,
        "molecular_formula": "C22H30N6O4S",
        "logp": 1.9,
        "pka": 5.97,
        "bcs_class": "II",
        "therapeutic_class": "PDE5 Inhibitor / Vasodilator",
        "route": "Oral"
    }
}

# ─── Pydantic Models ─────────────────────────────────────────────────────────────
class AnalysisRequest(BaseModel):
    smiles: str                              # SMILES is now the PRIMARY required field
    drug_name: Optional[str] = None         # Name is optional (for experimental drugs)
    molecular_weight: Optional[float] = None
    dose_mg: Optional[float] = None

class AnalysisResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    drug_name: str
    smiles: str
    molecular_weight: float
    dose_mg: float
    timestamp: str
    solubility: Dict[str, Any]
    excipients: Dict[str, Any]
    stability: Dict[str, Any]
    pk_compatibility: Dict[str, Any]
    drug_info: Dict[str, Any]

# ─── Routes ──────────────────────────────────────────────────────────────────────

@api_router.get("/")
async def root():
    return {"message": "PHARMA-AI Formulation Optimizer API", "version": "1.0.0"}

@api_router.get("/drugs")
async def get_drugs():
    drugs = []
    for name, info in DRUG_DATABASE.items():
        drugs.append({"name": name, **info})
    return {"drugs": drugs, "total": len(drugs)}

@api_router.get("/drugs/{drug_name}")
async def get_drug(drug_name: str):
    # Case-insensitive search
    for name, info in DRUG_DATABASE.items():
        if name.lower() == drug_name.lower():
            return {"name": name, **info}
    raise HTTPException(status_code=404, detail=f"Drug '{drug_name}' not found in database")


def generate_3d_from_smiles(smiles: str) -> str:
    """Generate 3D SDF from SMILES using RDKit."""
    # Try to parse the SMILES
    mol = Chem.MolFromSmiles(smiles, sanitize=False)
    if mol is None:
        raise ValueError("Invalid SMILES string")
    
    # Try to sanitize, but continue if it fails
    try:
        Chem.SanitizeMol(mol)
    except:
        # Try kekulization fix
        try:
            Chem.Kekulize(mol, clearAromaticFlags=True)
        except:
            pass
    
    # Add hydrogens for better 3D structure
    try:
        mol = Chem.AddHs(mol)
    except:
        pass
    
    # Generate 3D coordinates using ETKDG (better conformer generation)
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    params.maxAttempts = 50
    
    result = AllChem.EmbedMolecule(mol, params)
    if result == -1:
        # Fallback to basic embedding
        result = AllChem.EmbedMolecule(mol, randomSeed=42, useRandomCoords=True)
        if result == -1:
            # Last resort: use 2D coordinates as pseudo-3D
            AllChem.Compute2DCoords(mol)
    
    # Optimize geometry if we have 3D coords
    if result != -1:
        try:
            AllChem.MMFFOptimizeMolecule(mol, maxIters=200)
        except:
            try:
                AllChem.UFFOptimizeMolecule(mol, maxIters=200)
            except:
                pass
    
    # Convert to SDF format
    sdf = Chem.MolToMolBlock(mol)
    if not sdf:
        raise ValueError("Could not generate 3D structure")
    
    return sdf


def normalize_analysis_data(data):
    """Normalize AI response to match frontend expectations - convert all field names and ensure numeric values"""
    
    # Map AI response fields to frontend expected fields
    normalized = {}
    
    # Solubility mapping
    solubility_raw = data.get("solubility_analysis", data.get("solubility", {}))
    enhancement = solubility_raw.get("enhancement_strategy", solubility_raw.get("enhancement_strategies", []))
    if isinstance(enhancement, str):
        enhancement = [enhancement]
    elif not isinstance(enhancement, list):
        enhancement = ["Salt formation", "Nanosuspension"]
    
    normalized["solubility"] = {
        "prediction": int(solubility_raw.get("score", solubility_raw.get("prediction", 65))),
        "accuracy": float(solubility_raw.get("accuracy", 95.0)),
        "classification": solubility_raw.get("classification", "Moderately Soluble"),
        "aqueous_solubility_mg_ml": float(solubility_raw.get("aqueous_solubility_mg_ml", 6.5)),
        "ph_optimal": solubility_raw.get("ph_optimal", "6.5-7.5"),
        "mechanisms": solubility_raw.get("mechanisms", ["Hydrogen bonding", "Ionization"]),
        "enhancement_strategies": enhancement,
        "natural_language_summary": solubility_raw.get("natural_language_summary", "Moderate solubility suitable for oral formulation.")
    }
    
    # Formulation mapping
    formulation_raw = data.get("formulation_plan", data.get("excipients", {}))
    normalized["excipients"] = {
        "binders": formulation_raw.get("excipients", [{"name": "PVP K30", "grade": "USP", "recommended_conc": "3-5%", "rationale": "Binding"}]) if isinstance(formulation_raw.get("excipients"), list) else [{"name": "PVP K30", "grade": "USP", "recommended_conc": "3-5%", "rationale": "Binding"}],
        "fillers": [{"name": "Microcrystalline Cellulose", "grade": "Avicel PH-102", "recommended_conc": "40-60%", "rationale": "Compressibility"}],
        "disintegrants": [{"name": "Croscarmellose Sodium", "grade": "USP", "recommended_conc": "2-4%", "rationale": "Rapid disintegration"}],
        "lubricants": [{"name": "Magnesium Stearate", "grade": "USP", "recommended_conc": "0.5-1%", "rationale": "Lubrication"}],
        "coating": formulation_raw.get("coating", {"recommended": True, "type": "Film coating", "rationale": "Protection"}),
        "incompatibilities": formulation_raw.get("incompatibilities", ["Avoid strong oxidizers"]),
        "optimal_dosage_form": formulation_raw.get("optimal_dosage_form", "Tablet"),
        "natural_language_summary": formulation_raw.get("natural_language_summary", "Standard tablet formulation with pharmaceutical-grade excipients.")
    }
    
    # Stability mapping
    stability_raw = data.get("stability_report", data.get("stability", {}))
    normalized["stability"] = {
        "shelf_life_years": int(float(stability_raw.get("shelf_life_estimate_years", stability_raw.get("shelf_life_years", 3)))),
        "shelf_life_score": int(stability_raw.get("shelf_life_score", 85)),
        "primary_degradation": stability_raw.get("degradation_risk", stability_raw.get("primary_degradation", "Oxidation")),
        "degradation_mechanisms": stability_raw.get("degradation_mechanisms", ["Oxidation", "Hydrolysis"]),
        "storage_conditions": stability_raw.get("storage_conditions", {
            "temperature": "15-30°C",
            "humidity": "≤60% RH",
            "light": "Protected",
            "container": "HDPE bottle"
        }),
        "accelerated_data": stability_raw.get("accelerated_stability_data", stability_raw.get("accelerated_data", [
            {"condition": "25C/60%RH", "months": 0, "potency": 100},
            {"condition": "25C/60%RH", "months": 6, "potency": 97},
            {"condition": "25C/60%RH", "months": 12, "potency": 95}
        ])),
        "packaging_recommendation": stability_raw.get("packaging_recommendation", "HDPE bottle with desiccant"),
        "natural_language_summary": stability_raw.get("natural_language_summary", "Stable formulation with 3-year shelf life at room temperature.")
    }
    
    # PK/PD mapping
    pkpd_raw = data.get("pk_pd_simulation", data.get("pk_compatibility", {}))
    bioavail = pkpd_raw.get("bioavailability_percent", pkpd_raw.get("bioavailability_score", 70))
    if isinstance(bioavail, str):
        bioavail = int(float(bioavail.replace("%", "")))
    
    normalized["pk_compatibility"] = {
        "bioavailability_percent": int(bioavail),
        "bioavailability_score": int(bioavail),
        "tmax_hours": float(pkpd_raw.get("t_max_hours", pkpd_raw.get("tmax_hours", 2.0))),
        "t_half_hours": float(pkpd_raw.get("half_life_hours", pkpd_raw.get("t_half_hours", 4.5))),
        "absorption_rate": pkpd_raw.get("absorption_rate", "Moderate"),
        "absorption_mechanism": pkpd_raw.get("absorption_mechanism", "Passive diffusion"),
        "distribution_vd": float(pkpd_raw.get("distribution_vd_l_kg", pkpd_raw.get("distribution_vd", 1.2))),
        "protein_binding_percent": int(pkpd_raw.get("protein_binding_percent", 85)),
        "metabolism": pkpd_raw.get("metabolism", {
            "primary_enzyme": "CYP3A4",
            "metabolites": ["Hydroxylated metabolite"],
            "first_pass": 30
        }),
        "excretion": pkpd_raw.get("excretion", {
            "route": "Renal and Hepatic",
            "percent_unchanged": 25
        }),
        "bioavailability_curve": pkpd_raw.get("pk_curve_data", pkpd_raw.get("bioavailability_curve", [
            {"time": 0, "concentration": 0},
            {"time": 1, "concentration": 50},
            {"time": 2, "concentration": int(bioavail)},
            {"time": 4, "concentration": int(bioavail * 0.75)},
            {"time": 8, "concentration": int(bioavail * 0.4)},
            {"time": 12, "concentration": int(bioavail * 0.2)},
            {"time": 24, "concentration": int(bioavail * 0.05)}
        ])),
        "recommended_dosage_form": pkpd_raw.get("recommended_dosage_form", "Tablet"),
        "dosing_frequency": pkpd_raw.get("dosing_frequency", "Twice daily"),
        "natural_language_summary": pkpd_raw.get("natural_language_summary", f"Achieves {bioavail}% bioavailability with moderate absorption.")
    }
    
    # Molecule overview
    normalized["molecule_overview"] = data.get("physicochemical_properties", data.get("molecule_overview", {
        "inferred_class": "Small Molecule Drug",
        "key_features": ["Drug-like properties"],
        "drug_likeness": "Pass"
    }))
    
    return normalized


def generate_mock_analysis(drug_name, smiles, mw, bcs_class, logp, pka):
    """Generate mock pharmaceutical analysis data for demo purposes"""
    
    # Determine properties based on BCS class and LogP
    if bcs_class == "I":
        solubility_score = 85
        bioavailability = 90
    elif bcs_class == "II":
        solubility_score = 45
        bioavailability = 70
    elif bcs_class == "III":
        solubility_score = 80
        bioavailability = 50
    else:
        solubility_score = 35
        bioavailability = 40
    
    return {
        "molecule_overview": {
            "inferred_class": "Small Molecule Drug",
            "key_features": ["Aromatic rings present", "H-bond donors/acceptors", "Moderate molecular weight", "Drug-like properties"],
            "drug_likeness": "Pass - Complies with Lipinski's Rule of 5"
        },
        "solubility": {
            "prediction": solubility_score,
            "accuracy": 95.0,
            "classification": "Highly Soluble" if solubility_score > 70 else "Moderately Soluble" if solubility_score > 40 else "Poorly Soluble",
            "aqueous_solubility_mg_ml": round(solubility_score/10, 2),
            "ph_optimal": "6.5-7.5",
            "mechanisms": [
                "Hydrogen bonding with water molecules",
                "Ionization at physiological pH",
                "Hydrophilic functional groups present"
            ],
            "enhancement_strategies": ["Salt formation with HCl", "Nanosuspension technology", "Cyclodextrin complexation"],
            "natural_language_summary": f"This compound shows {solubility_score}% solubility score, making it suitable for oral formulation. The molecule dissolves readily in aqueous media at physiological pH."
        },
        "excipients": {
            "binders": [{"name": "Polyvinylpyrrolidone (PVP K30)", "grade": "USP", "recommended_conc": "3-5% w/w", "rationale": "Provides cohesive strength"}],
            "fillers": [{"name": "Microcrystalline Cellulose", "grade": "Avicel PH-102", "recommended_conc": "40-60% w/w", "rationale": "Excellent compressibility"}],
            "disintegrants": [{"name": "Croscarmellose Sodium", "grade": "USP", "recommended_conc": "2-4% w/w", "rationale": "Rapid disintegration"}],
            "lubricants": [{"name": "Magnesium Stearate", "grade": "USP", "recommended_conc": "0.5-1% w/w", "rationale": "Reduces friction"}],
            "coating": {"recommended": True, "type": "Film coating", "rationale": "Moisture protection"},
            "incompatibilities": ["Avoid lactose if moisture-sensitive", "Incompatible with strong oxidizing agents"],
            "optimal_dosage_form": "Immediate-Release Tablet" if bcs_class in ["I", "III"] else "Modified-Release Capsule",
            "natural_language_summary": "The formulation uses pharmaceutical-grade excipients selected based on the drug's physicochemical properties for optimal tablet formation and drug release."
        },
        "stability": {
            "shelf_life_years": 3,
            "shelf_life_score": 85,
            "primary_degradation": "Oxidation (minor hydrolysis)",
            "degradation_mechanisms": [
                "Oxidative degradation of aromatic rings",
                "Hydrolysis of ester bonds in humid conditions",
                "Photodegradation under UV exposure"
            ],
            "storage_conditions": {
                "temperature": "15-30°C",
                "humidity": "≤60% RH",
                "light": "Protected from light",
                "container": "HDPE bottle with desiccant"
            },
            "accelerated_data": [
                {"condition": "25C/60%RH", "months": 0, "potency": 100},
                {"condition": "25C/60%RH", "months": 3, "potency": 98.5},
                {"condition": "25C/60%RH", "months": 6, "potency": 97.2},
                {"condition": "25C/60%RH", "months": 12, "potency": 95.8},
                {"condition": "40C/75%RH", "months": 0, "potency": 100},
                {"condition": "40C/75%RH", "months": 1, "potency": 96.5},
                {"condition": "40C/75%RH", "months": 3, "potency": 92.3},
                {"condition": "40C/75%RH", "months": 6, "potency": 88.7}
            ],
            "packaging_recommendation": "Alu-Alu blister pack with desiccant",
            "natural_language_summary": "The formulation demonstrates excellent stability with a projected 3-year shelf life at room temperature. Packaging in moisture-barrier containers ensures product integrity."
        },
        "pk_compatibility": {
            "bioavailability_percent": bioavailability,
            "bioavailability_score": bioavailability,
            "tmax_hours": 2.0,
            "t_half_hours": 4.5,
            "absorption_rate": "Moderate",
            "absorption_mechanism": "Passive diffusion through intestinal epithelium",
            "distribution_vd": 1.2,
            "protein_binding_percent": 85,
            "metabolism": {
                "primary_enzyme": "CYP3A4",
                "metabolites": ["Hydroxylated metabolite", "Glucuronide conjugate"],
                "first_pass": 30
            },
            "excretion": {
                "route": "Renal (60%) and Hepatic (40%)",
                "percent_unchanged": 25
            },
            "bioavailability_curve": [
                {"time": 0, "concentration": 0},
                {"time": 0.5, "concentration": 20},
                {"time": 1, "concentration": 50},
                {"time": 2, "concentration": bioavailability},
                {"time": 4, "concentration": bioavailability * 0.75},
                {"time": 6, "concentration": bioavailability * 0.55},
                {"time": 8, "concentration": bioavailability * 0.40},
                {"time": 12, "concentration": bioavailability * 0.20},
                {"time": 24, "concentration": bioavailability * 0.05}
            ],
            "recommended_dosage_form": "Immediate-Release Tablet",
            "dosing_frequency": "Twice daily (BID)",
            "natural_language_summary": f"The drug achieves peak plasma concentration in 2 hours with {bioavailability}% bioavailability. The moderate half-life of 4.5 hours supports twice-daily dosing."
        }
    }


@api_router.get("/molecule3d")
async def get_molecule_3d(smiles: str = Query(..., description="SMILES string")):
    """Fetch 3D SDF from PubChem, fallback to RDKit for novel compounds."""
    headers = {
        "User-Agent": "PHARMA-AI/1.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # First, try PubChem
    try:
        async with aiohttp.ClientSession() as session:
            # Step 1: POST smiles to PubChem
            cid_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/cids/TXT"
            post_data = f"smiles={urllib.parse.quote(smiles, safe='')}"
            async with session.post(
                cid_url,
                data=post_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                resp_text = (await resp.text()).strip()
                if resp.status == 200 and resp_text.isdigit() and resp_text != '0':
                    cid = resp_text.split("\n")[0].strip()
                    
                    # Step 2: Fetch 3D SDF by CID
                    sdf_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/record/SDF?record_type=3d"
                    async with session.get(
                        sdf_url,
                        headers={"User-Agent": "PHARMA-AI/1.0"},
                        timeout=aiohttp.ClientTimeout(total=15)
                    ) as sdf_resp:
                        if sdf_resp.status == 200:
                            sdf_data = await sdf_resp.text()
                            if "V2000" in sdf_data or "V3000" in sdf_data:
                                return {"sdf": sdf_data, "cid": cid, "source": "PubChem"}
    except Exception as e:
        logger.info(f"PubChem lookup failed, falling back to RDKit: {e}")

    # Fallback: Generate 3D using RDKit
    try:
        logger.info(f"Generating 3D structure with RDKit for: {smiles[:50]}...")
        sdf_data = generate_3d_from_smiles(smiles)
        return {"sdf": sdf_data, "cid": None, "source": "RDKit (computed)"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Cannot generate 3D structure: {str(e)}")
    except Exception as e:
        logger.error(f"RDKit 3D generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate 3D structure")


@api_router.post("/analyze")
async def analyze_drug(request: AnalysisRequest):
    smiles = request.smiles.strip()
    if not smiles:
        raise HTTPException(status_code=400, detail="SMILES string is required.")

    # Try to match with database by name (optional) or by SMILES
    drug_info = None
    drug_name = request.drug_name or "Experimental Compound"

    if request.drug_name:
        for name, info in DRUG_DATABASE.items():
            if name.lower() == request.drug_name.lower():
                drug_info = info
                drug_name = name
                # If no custom SMILES override, use DB smiles
                if not request.smiles or request.smiles == info["smiles"]:
                    smiles = info["smiles"]
                break

    # If SMILES matches a known drug, auto-detect info
    if not drug_info:
        for name, info in DRUG_DATABASE.items():
            if info["smiles"].strip() == smiles.strip():
                drug_info = info
                if drug_name == "Experimental Compound":
                    drug_name = name
                break

    # is_experimental only when no DB entry was matched AND no name was provided by user
    is_experimental = (drug_info is None) and not bool(request.drug_name)

    mw = request.molecular_weight or (drug_info["molecular_weight"] if drug_info else 300.0)
    dose = request.dose_mg or 100.0
    bcs_class = drug_info.get("bcs_class", "Unknown") if drug_info else "Unknown"
    logp = drug_info.get("logp", "Unknown") if drug_info else "Unknown"
    pka = drug_info.get("pka", "Unknown") if drug_info else "Unknown"
    therapeutic_class = drug_info.get("therapeutic_class", "Unknown") if drug_info else "Unknown"
    route = drug_info.get("route", "Oral") if drug_info else "Oral"

    # AI Analysis using Hugging Face Llama-3.3-70B-Instruct
    hf_api_key = os.environ.get("HF_API_KEY")
    hf_model = os.environ.get("HF_MODEL", "meta-llama/Llama-3.3-70B-Instruct")
    
    if not hf_api_key:
        raise HTTPException(status_code=500, detail="Hugging Face API key not configured")

    system_message = """You are a Senior Pharmaceutical Scientist and Cheminformatics Expert specializing in drug formulation, PK/PD modeling, and ICH Q8 guidelines.
You provide scientifically accurate analysis using Lipinski's Rule of 5, Veber's Rules, and functional group analysis.
For unknown drugs, derive ALL properties from SMILES structure (functional groups, H-bond donors/acceptors, rotatable bonds, LogP estimation).
Output MUST be valid JSON only. No markdown, no prose, no code blocks."""

    experimental_note = "CRITICAL: This is an experimental compound. Derive ALL properties from SMILES using cheminformatics (functional groups = degradation pathways, esters = hydrolysis risk, aromatic rings = stability, etc.)." if is_experimental else ""

    prompt = f"""Act as a Senior Pharmaceutical Scientist. Generate comprehensive formulation and PK/PD analysis.

Input Data:
- Compound: {drug_name}
- SMILES: {smiles}
- MW: {mw} g/mol
{'- BCS Class: ' + str(bcs_class) if bcs_class != 'Unknown' else '- BCS Class: Derive from SMILES'}
{'- LogP: ' + str(logp) if logp != 'Unknown' else '- LogP: Estimate from SMILES'}
{'- pKa: ' + str(pka) if pka != 'Unknown' else '- pKa: Estimate from SMILES'}
- Therapeutic Class: {therapeutic_class}
- Target Dose: {dose} mg
{experimental_note}

Scientific Constraints:
1. Use Lipinski's Rule of 5 (MW<500, LogP<5, HBD≤5, HBA≤10)
2. Apply Veber's Rules (Rotatable bonds ≤10, TPSA ≤140)
3. Follow ICH Q8 guidelines for formulation
4. Functional group analysis: Esters→Hydrolysis, Phenols→Oxidation, Amines→Salt formation

Return ONLY valid JSON (no markdown blocks) with this EXACT structure:
{{
  "molecule_name": "{drug_name}",
  "smiles": "{smiles}",
  "physicochemical_properties": {{
    "mw": {mw},
    "logp": "Estimated LogP value",
    "hbd": "H-Bond Donors count",
    "hba": "H-Bond Acceptors count",
    "rotatable_bonds": "Count",
    "tpsa": "Topological Polar Surface Area",
    "bcs_class": "I, II, III, or IV",
    "lipinski_violations": 0,
    "drug_likeness": "Pass/Fail with explanation"
  }},
  "solubility_analysis": {{
    "score": 0-100,
    "classification": "Highly Soluble / Moderately Soluble / Poorly Soluble",
    "aqueous_solubility_mg_ml": "numeric value",
    "ph_optimal": "optimal pH range",
    "mechanisms": ["3 solubility mechanisms from functional groups"],
    "enhancement_strategy": "e.g., Nanosuspension, Salt formation, Cyclodextrin complexation",
    "natural_language_summary": "2-3 sentences for non-experts"
  }},
  "formulation_plan": {{
    "optimal_dosage_form": "Tablet / Capsule / Suspension based on BCS class",
    "excipients": [
      {{"type": "Binder", "name": "e.g., PVP K30", "concentration": "% w/w", "rationale": "Based on SMILES functional groups"}},
      {{"type": "Filler", "name": "e.g., Lactose Monohydrate", "concentration": "% w/w", "rationale": "Reason"}},
      {{"type": "Disintegrant", "name": "e.g., Croscarmellose Sodium", "concentration": "% w/w", "rationale": "Reason"}},
      {{"type": "Lubricant", "name": "e.g., Magnesium Stearate", "concentration": "% w/w", "rationale": "Reason"}}
    ],
    "coating": {{"recommended": true/false, "type": "Enteric/Film", "rationale": "pH stability"}},
    "incompatibilities": ["2-3 excipient incompatibilities to avoid"],
    "natural_language_summary": "2-3 sentences explaining excipient choices"
  }},
  "pk_pd_simulation": {{
    "bioavailability_percent": 0-100,
    "bioavailability_score": 0-100,
    "t_max_hours": "Time to peak concentration",
    "c_max_ug_ml": "Peak plasma concentration",
    "half_life_hours": "Elimination half-life",
    "absorption_rate": "Fast / Moderate / Slow",
    "absorption_mechanism": "Passive diffusion / Active transport",
    "distribution_vd_l_kg": "Volume of distribution",
    "protein_binding_percent": "% plasma protein binding",
    "metabolism": {{
      "primary_enzyme": "CYP450 enzyme",
      "metabolites": ["Major metabolites"],
      "first_pass_percent": "% first-pass effect"
    }},
    "excretion": {{
      "route": "Renal / Hepatic / Both",
      "percent_unchanged": "% excreted unchanged"
    }},
    "pk_curve_data": [
      {{"time": 0, "conc": 0}},
      {{"time": 0.5, "conc": 25}},
      {{"time": 1, "conc": 55}},
      {{"time": 2, "conc": 100}},
      {{"time": 4, "conc": 85}},
      {{"time": 6, "conc": 65}},
      {{"time": 8, "conc": 45}},
      {{"time": 12, "conc": 25}},
      {{"time": 18, "conc": 10}},
      {{"time": 24, "conc": 3}}
    ],
    "dosing_frequency": "Once/Twice/Three times daily",
    "natural_language_summary": "2-3 sentences about absorption and duration"
  }},
  "stability_report": {{
    "shelf_life_estimate_years": "2-5 years",
    "shelf_life_score": 0-100,
    "degradation_risk": "Primary pathway: Oxidation / Hydrolysis / Photolysis",
    "degradation_mechanisms": ["3 mechanisms based on functional groups"],
    "storage_conditions": {{
      "temperature": "15-30°C",
      "humidity": "% RH",
      "light_protection": "Required / Not Required",
      "container": "HDPE / Glass / Alu-Alu"
    }},
    "accelerated_stability_data": [
      {{"condition": "25°C/60%RH", "months": 0, "potency_percent": 100}},
      {{"condition": "25°C/60%RH", "months": 3, "potency_percent": 98}},
      {{"condition": "25°C/60%RH", "months": 6, "potency_percent": 97}},
      {{"condition": "25°C/60%RH", "months": 12, "potency_percent": 95}},
      {{"condition": "40°C/75%RH", "months": 0, "potency_percent": 100}},
      {{"condition": "40°C/75%RH", "months": 1, "potency_percent": 96}},
      {{"condition": "40°C/75%RH", "months": 3, "potency_percent": 92}},
      {{"condition": "40°C/75%RH", "months": 6, "potency_percent": 88}}
    ],
    "packaging_recommendation": "Alu-Alu blister / HDPE bottle with desiccant",
    "natural_language_summary": "2-3 sentences about shelf life and storage"
  }},
  "executive_summary": "A 2-sentence technical summary highlighting key formulation challenges and PK advantages for judges and investors."
}}"""

    try:
        # Check if API key is valid
        if not hf_api_key or hf_api_key == "your_huggingface_api_key_here":
            raise HTTPException(status_code=500, detail="Hugging Face API key not configured. Please set HF_API_KEY in backend/.env")
        
        logger.info(f"Using Hugging Face API with model: {hf_model}")
        logger.info(f"API Key present: {hf_api_key[:10]}...")
        
        # Hugging Face Inference API via novita router
        hf_url = "https://router.huggingface.co/novita/v3/openai/chat/completions"
        headers = {
            "Authorization": f"Bearer {hf_api_key}",
            "Content-Type": "application/json"
        }
        
        # Use lowercase model name for novita
        model_name = hf_model.lower()
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.95
        }
        
        logger.info(f"Calling Hugging Face API for drug: {drug_name}")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                hf_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(f"Hugging Face API error: {resp.status} - {error_text}")
                    raise HTTPException(status_code=502, detail=f"Hugging Face API failed: {resp.status} - {error_text[:200]}")
                
                logger.info("API call successful! Parsing response...")
                result_json = await resp.json() 
                response = result_json["choices"][0]["message"]["content"]
                
                # Clean and parse JSON response (handle markdown code blocks)
                clean_response = response.strip()
                if clean_response.startswith('```json'):
                    clean_response = clean_response[7:]  # Remove ```json
                if clean_response.startswith('```'):
                    clean_response = clean_response[3:]   # Remove ```
                if clean_response.endswith('```'):
                    clean_response = clean_response[:-3]  # Remove ending ```
                clean_response = clean_response.strip()
                
                analysis_data = json.loads(clean_response)
                logger.info("Successfully parsed AI response!")
                
                # Normalize the data structure to match frontend expectations
                normalized_data = normalize_analysis_data(analysis_data)
        
        result = {
            "id": str(uuid.uuid4()),
            "drug_name": drug_name,
            "smiles": smiles,
            "molecular_weight": mw,
            "dose_mg": dose,
            "is_experimental": is_experimental,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "drug_info": drug_info or {"smiles": smiles, "molecular_weight": mw, "therapeutic_class": "Experimental Compound"},
            **normalized_data
        }
        
        # Save to MongoDB if available
        if MONGODB_AVAILABLE and db is not None:
            try:
                doc = result.copy()
                await db.analyses.insert_one(doc)
                doc.pop("_id", None)
                logger.info(f"Analysis saved to MongoDB: {result['id']}")
            except Exception as e:
                logger.warning(f"Failed to save to MongoDB: {e}")
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}, response: {response[:500] if 'response' in locals() else 'N/A'}")
        raise HTTPException(status_code=500, detail="AI returned invalid JSON. Please retry.")
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analyses")
async def get_analyses():
    if not MONGODB_AVAILABLE or db is None:
        return {"analyses": [], "total": 0, "message": "MongoDB not available - history disabled"}
    
    try:
        analyses = await db.analyses.find({}, {"_id": 0}).sort("timestamp", -1).to_list(50)
        return {"analyses": analyses, "total": len(analyses)}
    except Exception as e:
        logger.error(f"Error fetching analyses: {e}")
        return {"analyses": [], "total": 0, "error": str(e)}

@api_router.get("/analyses/{analysis_id}")
async def get_analysis(analysis_id: str):
    if not MONGODB_AVAILABLE or db is None:
        raise HTTPException(status_code=503, detail="MongoDB not available")
    
    try:
        analysis = await db.analyses.find_one({"id": analysis_id}, {"_id": 0})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return analysis
    except Exception as e:
        logger.error(f"Error fetching analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/compare")
async def compare_drugs(request: dict):
    """Compare two drugs side-by-side"""
    drug1_smiles = request.get("drug1_smiles")
    drug2_smiles = request.get("drug2_smiles")
    drug1_name = request.get("drug1_name", "Drug A")
    drug2_name = request.get("drug2_name", "Drug B")
    
    if not drug1_smiles or not drug2_smiles:
        raise HTTPException(status_code=400, detail="Both SMILES strings required")
    
    # Get analyses for both drugs
    try:
        # Analyze drug 1
        req1 = AnalysisRequest(smiles=drug1_smiles, drug_name=drug1_name)
        result1 = await analyze_drug(req1)
        
        # Analyze drug 2
        req2 = AnalysisRequest(smiles=drug2_smiles, drug_name=drug2_name)
        result2 = await analyze_drug(req2)
        
        # Create comparison
        comparison = {
            "drug1": result1,
            "drug2": result2,
            "comparison_summary": {
                "solubility_winner": drug1_name if float(result1.get("solubility", {}).get("prediction", 0)) > float(result2.get("solubility", {}).get("prediction", 0)) else drug2_name,
                "bioavailability_winner": drug1_name if float(result1.get("pk_compatibility", {}).get("bioavailability_percent", 0)) > float(result2.get("pk_compatibility", {}).get("bioavailability_percent", 0)) else drug2_name,
                "stability_winner": drug1_name if float(result1.get("stability", {}).get("shelf_life_years", 0)) > float(result2.get("stability", {}).get("shelf_life_years", 0)) else drug2_name,
            }
        }
        
        return comparison
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/what-if")
async def what_if_scenario(request: dict):
    """Analyze what-if scenarios for drug modifications"""
    base_smiles = request.get("smiles")
    scenario_type = request.get("scenario_type")  # "increase_dose", "change_formulation", "storage_conditions"
    parameters = request.get("parameters", {})
    
    if not base_smiles or not scenario_type:
        raise HTTPException(status_code=400, detail="SMILES and scenario_type required")
    
    try:
        # Get base analysis
        base_req = AnalysisRequest(smiles=base_smiles, drug_name=parameters.get("drug_name", "Base Drug"))
        base_result = await analyze_drug(base_req)
        
        # Generate scenario analysis based on type
        scenario_result = {}
        
        if scenario_type == "increase_dose":
            new_dose = parameters.get("new_dose", 500)
            scenario_req = AnalysisRequest(smiles=base_smiles, drug_name=f"{base_result['drug_name']} ({new_dose}mg)", dose_mg=new_dose)
            scenario_result = await analyze_drug(scenario_req)
            scenario_result["scenario_description"] = f"Increased dose from {base_result.get('dose_mg', 100)}mg to {new_dose}mg"
            
        elif scenario_type == "storage_temperature":
            temp = parameters.get("temperature", "30C")
            scenario_result = base_result.copy()
            scenario_result["scenario_description"] = f"Storage at {temp} instead of recommended temperature"
            scenario_result["stability"]["predicted_impact"] = "Shelf life may be reduced by 20-30% at higher temperatures"
            
        elif scenario_type == "formulation_change":
            new_form = parameters.get("new_formulation", "Capsule")
            scenario_result = base_result.copy()
            scenario_result["excipients"]["optimal_dosage_form"] = new_form
            scenario_result["scenario_description"] = f"Changed formulation to {new_form}"
            
        return {
            "base_analysis": base_result,
            "scenario_analysis": scenario_result,
            "scenario_type": scenario_type,
            "parameters": parameters
        }
    except Exception as e:
        logger.error(f"What-if scenario error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    if client is not None:
        client.close()
        logger.info("MongoDB connection closed")
