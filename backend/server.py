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
from datetime import datetime, timezone, timedelta
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import hashlib
from functools import lru_cache
import asyncio
import time

# RDKit for 3D coordinate generation
from rdkit import Chem
from rdkit.Chem import AllChem

# Import schemas
from database_schema import AnalysisBlueprint
from analytics_schema import APIAnalytics, AnalyticsSummary, RequestType

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- DATABASE SETUP ---
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'pharma_db')

client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# ─── IN-MEMORY CACHE ──────────────────────────────────────────────────────────
class InMemoryCache:
    """✅ V-7: Simple in-memory cache with LRU"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.hit_count = 0
        self.miss_count = 0
    
    def generate_key(self, smiles: str) -> str:
        """Generate cache key from SMILES"""
        return f"analysis:{hashlib.md5(smiles.encode()).hexdigest()}"
    
    def get(self, smiles: str) -> Optional[Dict]:
        """Retrieve from cache"""
        key = self.generate_key(smiles)
        
        if key in self.cache:
            self.hit_count += 1
            logger.info(f"💾 Cache HIT for SMILES: {smiles[:20]}...")
            return self.cache[key]
        
        self.miss_count += 1
        logger.info(f"🔍 Cache MISS for SMILES: {smiles[:20]}...")
        return None
    
    def set(self, smiles: str, data: Dict) -> bool:
        """Store in cache"""
        key = self.generate_key(smiles)
        
        if len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.info(f"Cache full, removed oldest entry. Current size: {len(self.cache)}/{self.max_size}")
        
        self.cache[key] = data
        logger.info(f"💾 Cached analysis for SMILES: {smiles[:20]}...")
        return True
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            "cache_enabled": True,
            "cache_type": "In-Memory (Zero Installation, Zero Storage!)",
            "total_cached": len(self.cache),
            "max_size": self.max_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": round(hit_rate, 2)
        }

cache = InMemoryCache(max_size=1000)

# ─── ANALYTICS HELPER ──────────────────────────────────────────────────────────
class AnalyticsTracker:
    """✅ V-5: Track API requests and performance"""
    
    @staticmethod
    async def log_request(
        request_type: RequestType,
        endpoint: str,
        response_time_ms: float,
        status_code: int,
        drug_name: Optional[str] = None,
        smiles: Optional[str] = None,
        was_cached: bool = False,
        is_error: bool = False,
        error_message: Optional[str] = None
    ):
        """Log API request to analytics"""
        try:
            analytics = APIAnalytics(
                request_id=str(uuid.uuid4()),
                request_type=request_type,
                endpoint=endpoint,
                drug_name=drug_name,
                smiles=smiles,
                response_time_ms=response_time_ms,
                status_code=status_code,
                is_error=is_error,
                error_message=error_message,
                was_cached=was_cached,
                cache_hit=was_cached
            )
            await analytics.insert()
            logger.info(f"📊 Analytics logged: {request_type} - {response_time_ms:.2f}ms")
        except Exception as e:
            logger.warning(f"Analytics logging error: {e}")
    
    @staticmethod
    async def generate_daily_summary():
        """✅ V-5: Generate daily analytics summary"""
        try:
            today = datetime.now(timezone.utc).date().isoformat()
            
            # Get all requests from today
            start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            analytics = await APIAnalytics.find({
                "timestamp": {
                    "$gte": start_of_day,
                    "$lt": end_of_day
                }
            }).to_list()
            
            if not analytics:
                return None
            
            # Calculate metrics
            total_requests = len(analytics)
            total_errors = sum(1 for a in analytics if a.is_error)
            total_cache_hits = sum(1 for a in analytics if a.cache_hit)
            
            response_times = [a.response_time_ms for a in analytics]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            
            # Most analyzed drugs
            drug_counts = {}
            for a in analytics:
                if a.drug_name:
                    drug_counts[a.drug_name] = drug_counts.get(a.drug_name, 0) + 1
            
            most_analyzed = dict(sorted(drug_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            
            # Endpoint stats
            endpoint_counts = {}
            for a in analytics:
                endpoint_counts[a.endpoint] = endpoint_counts.get(a.endpoint, 0) + 1
            
            # Cache hit rate
            cache_hit_rate = (total_cache_hits / total_requests * 100) if total_requests > 0 else 0
            
            # Create summary
            summary = AnalyticsSummary(
                date=today,
                total_requests=total_requests,
                total_errors=total_errors,
                total_cache_hits=total_cache_hits,
                avg_response_time_ms=round(avg_response_time, 2),
                min_response_time_ms=round(min_response_time, 2),
                max_response_time_ms=round(max_response_time, 2),
                most_analyzed_drugs=most_analyzed,
                cache_hit_rate=round(cache_hit_rate, 2),
                endpoint_stats=endpoint_counts
            )
            
            await summary.insert()
            logger.info(f"📊 Daily summary created for {today}")
            return summary
        except Exception as e:
            logger.warning(f"Summary generation error: {e}")
            return None

# ─── LIFESPAN HANDLER ──────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    try:
        await init_beanie(
            database=db,
            document_models=[AnalysisBlueprint, APIAnalytics, AnalyticsSummary]
        )
        print("✅ FULL SYSTEM ONLINE: AI Brain, Database Heart & In-Memory Cache Connected!")
        print("📦 Cache Type: In-Memory (Zero Installation, Zero Storage!)")
        print("📊 Analytics: Enabled (V-5)")
    except Exception as e:
        print(f"❌ Startup Error: {e}")
    
    yield  # Application runs here
    
    # SHUTDOWN
    print("🛑 Server shutting down...")
    await client.close()


app = FastAPI(
    title="PHARMA-AI Formulation Optimizer",
    lifespan=lifespan
)
api_router = APIRouter(prefix="/api")

# ─── Drug Database ────────────────────────────────────────────────────────────────
DRUG_DATABASE = {
    "Aspirin": {"smiles": "CC(=O)Oc1ccccc1C(=O)O", "bcs_class": "I", "molecular_weight": 180.16},
    "Atorvastatin": {"smiles": "CC(C)c1c(C(=O)Nc2ccccc2F)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CC[C@@H](O)C[C@@H](O)CC(=O)O", "bcs_class": "II", "molecular_weight": 558.64},
    "Amlodipine": {"smiles": "CCOC(=O)C1=C(COCCN)NC(C)=C(C(=O)OCC)C1c1ccccc1Cl", "bcs_class": "I", "molecular_weight": 408.88},
    "Lisinopril": {"smiles": "OC(=O)[C@@H](CCc1ccccc1)N[C@@H](CC(=O)O)C(=O)N1CCC[C@H]1C(=O)O", "bcs_class": "III", "molecular_weight": 405.49},
    "Metoprolol": {"smiles": "CC(C)NCC(O)COc1ccc(CCOC)cc1", "bcs_class": "I", "molecular_weight": 267.36},
    "Warfarin": {"smiles": "OC(=O)CCCC1CC(=O)c2ccccc2O1", "bcs_class": "I", "molecular_weight": 308.33},
}

# ─── Pydantic Models ──────────────────────────────────────────────────────────────
class AnalysisRequest(BaseModel):
    smiles: str
    drug_name: Optional[str] = None
    molecular_weight: Optional[float] = None
    dose_mg: Optional[float] = None

class OutlierInfo(BaseModel):
    is_outlier: bool
    flag_reason: str
    severity: str

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
    cached: bool = False
    timestamp: str

class CacheStats(BaseModel):
    cache_enabled: bool
    cache_type: str
    total_cached: int
    max_size: int
    hit_count: int
    miss_count: int
    hit_rate: float

# ─── V-2: ANALYSIS PIPELINE FUNCTIONS ──────────────────────────────────────────

def generate_3d_from_smiles(smiles: str) -> Optional[str]:
    """✅ V-2: Generate 3D SDF structure from SMILES string"""
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
    """✅ V-2: Calculate confidence score"""
    confidence = 0.0
    
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            confidence += 50
            num_atoms = mol.GetNumAtoms()
            if num_atoms > 20:
                confidence += 5
        else:
            return 0.0
    except Exception:
        return 0.0
    
    bcs_confidence_map = {"I": 30, "II": 20, "III": 15, "IV": 10}
    confidence += bcs_confidence_map.get(bcs_class, 0)
    
    if molecular_weight:
        if 100 <= molecular_weight <= 1000:
            confidence += 20
        elif 50 <= molecular_weight <= 1200:
            confidence += 10
    else:
        confidence += 15
    
    return min(confidence, 100.0)


def auto_tag_bcs_class(molecular_weight: Optional[float], solubility: Optional[float]) -> str:
    """✅ V-2: Auto-assign BCS class"""
    if solubility is None:
        solubility = 50.0
    if molecular_weight is None:
        molecular_weight = 300.0
    
    is_high_solubility = solubility > 50
    is_high_permeability = molecular_weight < 400
    
    if is_high_solubility and is_high_permeability:
        return "I"
    elif not is_high_solubility and is_high_permeability:
        return "II"
    elif is_high_solubility and not is_high_permeability:
        return "III"
    else:
        return "IV"


def flag_outliers(solubility: float, confidence: float, molecular_weight: Optional[float] = None) -> OutlierInfo:
    """✅ V-2: Flag unusual/outlier values"""
    flags = []
    severity = "low"
    
    if solubility < 5:
        flags.append("Extremely low solubility (< 5%)")
        severity = "high"
    elif solubility > 95:
        flags.append("Extremely high solubility (> 95%)")
        severity = "medium"
    
    if confidence < 20:
        flags.append("Very low confidence score")
        severity = "high" if severity != "high" else "high"
    
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
    """✅ V-2: Estimate solubility score"""
    base_solubility = {"I": 75.0, "II": 30.0, "III": 80.0, "IV": 15.0}
    
    solubility = base_solubility.get(bcs_class, 50.0)
    
    if molecular_weight:
        if molecular_weight > 500:
            solubility *= 0.8
        elif molecular_weight < 200:
            solubility *= 1.1
    
    return min(solubility, 100.0)


# ─── Routes ──────────────────────────────────────────────────────────────────────

@api_router.get("/")
async def root():
    return {"message": "PHARMA-AI Formulation Optimizer API", "version": "2.5.0"}


@api_router.get("/drugs")
async def get_drugs():
    """Get all available drugs"""
    start_time = time.time()
    drugs = [{"name": name, **info} for name, info in DRUG_DATABASE.items()]
    response_time = (time.time() - start_time) * 1000
    
    await AnalyticsTracker.log_request(
        request_type=RequestType.FETCH_DRUG,
        endpoint="/api/drugs",
        response_time_ms=response_time,
        status_code=200
    )
    
    return {"drugs": drugs, "total": len(drugs)}


@api_router.get("/drugs/{drug_name}")
async def get_drug(drug_name: str):
    """Get specific drug information"""
    start_time = time.time()
    
    for name, info in DRUG_DATABASE.items():
        if name.lower() == drug_name.lower():
            response_time = (time.time() - start_time) * 1000
            
            await AnalyticsTracker.log_request(
                request_type=RequestType.FETCH_DRUG,
                endpoint="/api/drugs/{drug_name}",
                response_time_ms=response_time,
                status_code=200,
                drug_name=name
            )
            
            return {"name": name, **info}
    
    response_time = (time.time() - start_time) * 1000
    await AnalyticsTracker.log_request(
        request_type=RequestType.FETCH_DRUG,
        endpoint="/api/drugs/{drug_name}",
        response_time_ms=response_time,
        status_code=404,
        drug_name=drug_name,
        is_error=True,
        error_message="Drug not found"
    )
    
    raise HTTPException(status_code=404, detail="Drug not found")


@api_router.get("/molecule3d")
async def get_molecule_3d(smiles: str = Query(..., description="SMILES string")):
    """Generate 3D molecular structure"""
    start_time = time.time()
    
    try:
        sdf_data = generate_3d_from_smiles(smiles)
        if not sdf_data:
            raise HTTPException(status_code=400, detail="Could not generate 3D structure")
        
        response_time = (time.time() - start_time) * 1000
        await AnalyticsTracker.log_request(
            request_type=RequestType.GET_MOLECULE_3D,
            endpoint="/api/molecule3d",
            response_time_ms=response_time,
            status_code=200,
            smiles=smiles
        )
        
        return {"sdf": sdf_data, "source": "RDKit (Computed)"}
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        await AnalyticsTracker.log_request(
            request_type=RequestType.GET_MOLECULE_3D,
            endpoint="/api/molecule3d",
            response_time_ms=response_time,
            status_code=400,
            smiles=smiles,
            is_error=True,
            error_message=str(e)
        )
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/analyze")
async def analyze_drug(request: AnalysisRequest) -> AnalysisResponse:
    """
    ✅ V-7: Analyze drug with caching
    ✅ V-5: Track analytics
    """
    start_time = time.time()
    was_cached = False
    
    try:
        # 1. Check cache first
        cached_result = await asyncio.to_thread(cache.get, request.smiles)
        if cached_result:
            cached_result["cached"] = True
            response_time = (time.time() - start_time) * 1000
            was_cached = True
            
            await AnalyticsTracker.log_request(
                request_type=RequestType.ANALYZE,
                endpoint="/api/analyze",
                response_time_ms=response_time,
                status_code=200,
                drug_name=request.drug_name,
                smiles=request.smiles,
                was_cached=True
            )
            
            return AnalysisResponse(**cached_result)
        
        # 2. Validate SMILES
        mol = Chem.MolFromSmiles(request.smiles)
        if not mol:
            raise HTTPException(status_code=400, detail="Invalid SMILES string")
        
        # 3. Generate 3D molecule structure
        mol_3d = generate_3d_from_smiles(request.smiles)
        
        # 4. Auto-compute BCS class
        auto_bcs = auto_tag_bcs_class(
            molecular_weight=request.molecular_weight,
            solubility=None
        )
        
        # 5. Estimate solubility
        solubility_score = estimate_solubility_score(auto_bcs, request.molecular_weight)
        
        # 6. Compute confidence score
        confidence_score = compute_confidence_score(
            request.smiles,
            auto_bcs,
            request.molecular_weight
        )
        
        # 7. Flag outliers
        outlier_info = flag_outliers(solubility_score, confidence_score, request.molecular_weight)
        
        # 8. Save to database
        analysis = AnalysisBlueprint(
            drug_name=request.drug_name or "Unknown",
            smiles=request.smiles,
            bcs_class=auto_bcs,
            solubility_score=solubility_score,
            confidence_score=confidence_score
        )
        await analysis.insert()
        
        logger.info(f"✅ Analysis saved: {request.drug_name}")
        
        # 9. Prepare response
        response_data = {
            "status": "success",
            "analysis_id": str(analysis.id),
            "drug_name": request.drug_name or "Unknown",
            "smiles": request.smiles,
            "bcs_class": auto_bcs,
            "solubility_score": round(solubility_score, 2),
            "confidence_score": round(confidence_score, 2),
            "mol_3d": mol_3d,
            "outlier_flagged": outlier_info.is_outlier,
            "outlier_info": outlier_info,
            "cached": False,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # 10. Cache the result
        await asyncio.to_thread(cache.set, request.smiles, response_data)
        
        # 11. Log analytics
        response_time = (time.time() - start_time) * 1000
        await AnalyticsTracker.log_request(
            request_type=RequestType.ANALYZE,
            endpoint="/api/analyze",
            response_time_ms=response_time,
            status_code=200,
            drug_name=request.drug_name,
            smiles=request.smiles,
            was_cached=False
        )
        
        return AnalysisResponse(**response_data)
        
    except HTTPException:
        response_time = (time.time() - start_time) * 1000
        await AnalyticsTracker.log_request(
            request_type=RequestType.ANALYZE,
            endpoint="/api/analyze",
            response_time_ms=response_time,
            status_code=400,
            drug_name=request.drug_name,
            smiles=request.smiles,
            is_error=True,
            error_message="Invalid SMILES"
        )
        raise
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        await AnalyticsTracker.log_request(
            request_type=RequestType.ANALYZE,
            endpoint="/api/analyze",
            response_time_ms=response_time,
            status_code=500,
            drug_name=request.drug_name,
            smiles=request.smiles,
            is_error=True,
            error_message=str(e)
        )
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@api_router.get("/cache/stats")
async def get_cache_stats() -> CacheStats:
    """Get cache statistics"""
    stats = cache.get_stats()
    return CacheStats(**stats)


@api_router.delete("/cache/clear")
async def clear_cache():
    """Clear cache"""
    cache.clear()
    return {"message": "Cache cleared successfully"}


@api_router.get("/analytics/daily")
async def get_daily_analytics():
    """
    ✅ V-5: Get today's analytics summary
    """
    try:
        today = datetime.now(timezone.utc).date().isoformat()
        summary = await AnalyticsSummary.find_one({"date": today})
        
        if not summary:
            return {
                "message": "No analytics data for today yet",
                "date": today,
                "data": None
            }
        
        return {
            "date": summary.date,
            "total_requests": summary.total_requests,
            "total_errors": summary.total_errors,
            "total_cache_hits": summary.total_cache_hits,
            "avg_response_time_ms": summary.avg_response_time_ms,
            "min_response_time_ms": summary.min_response_time_ms,
            "max_response_time_ms": summary.max_response_time_ms,
            "most_analyzed_drugs": summary.most_analyzed_drugs,
            "cache_hit_rate": summary.cache_hit_rate,
            "endpoint_stats": summary.endpoint_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/analytics/summary")
async def generate_analytics_summary():
    """
    ✅ V-5: Generate and return today's analytics summary
    """
    try:
        summary = await AnalyticsTracker.generate_daily_summary()
        
        if not summary:
            return {"message": "No analytics data available"}
        
        return {
            "status": "success",
            "date": summary.date,
            "total_requests": summary.total_requests,
            "total_errors": summary.total_errors,
            "total_cache_hits": summary.total_cache_hits,
            "avg_response_time_ms": summary.avg_response_time_ms,
            "min_response_time_ms": summary.min_response_time_ms,
            "max_response_time_ms": summary.max_response_time_ms,
            "most_analyzed_drugs": summary.most_analyzed_drugs,
            "cache_hit_rate": summary.cache_hit_rate,
            "endpoint_stats": summary.endpoint_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/analytics/requests")
async def get_recent_requests(limit: int = Query(50, le=500)):
    """
    ✅ V-5: Get recent API requests
    """
    try:
        requests = await APIAnalytics.find_all().sort("timestamp", -1).limit(limit).to_list()
        
        return {
            "total": len(requests),
            "requests": [
                {
                    "request_id": r.request_id,
                    "request_type": r.request_type,
                    "endpoint": r.endpoint,
                    "drug_name": r.drug_name,
                    "response_time_ms": r.response_time_ms,
                    "status_code": r.status_code,
                    "is_error": r.is_error,
                    "was_cached": r.was_cached,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in requests
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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