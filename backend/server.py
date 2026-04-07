from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
import json
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import hashlib
import asyncio
import time
from bson import ObjectId
from fastapi.responses import StreamingResponse

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    logging.warning("RDKit not available — 3D molecule generation & SMILES validation disabled")
    class _ChemStub:
        @staticmethod
        def MolFromSmiles(smiles):
            return True
        @staticmethod
        def AddHs(mol):
            return mol
        @staticmethod
        def MolToMolBlock(mol):
            return None
    class _AllChemStub:
        @staticmethod
        def EmbedMolecule(mol, params=None):
            pass
        @staticmethod
        def ETKDG():
            return None
        @staticmethod
        def MMFFOptimizeMolecule(mol):
            pass
    Chem = _ChemStub()
    AllChem = _AllChemStub()


from database_schema import AnalysisBlueprint
from analytics_schema import APIAnalytics, AnalyticsSummary, RequestType

from export_service import ExportService
from backup_service import BackupService

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import sqlite3

class PersistentDatabase:
    """SQLite-based persistent database"""
    
    def __init__(self, db_path: str = "pharma.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._init_schema()
    
    def _init_schema(self):
        """Create tables if they don't exist"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_blueprint (
                _id TEXT PRIMARY KEY,
                drug_name TEXT NOT NULL,
                smiles TEXT NOT NULL,
                bcs_class TEXT NOT NULL,
                category TEXT,              -- H-4: Therapeutic category tag
                solubility_score REAL,
                confidence_score REAL,
                molecular_weight REAL,
                dose_mg REAL,
                timestamp TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_analytics (
                _id TEXT PRIMARY KEY,
                request_id TEXT,
                request_type TEXT,
                endpoint TEXT,
                drug_name TEXT,
                smiles TEXT,
                response_time_ms REAL,
                status_code INTEGER,
                is_error BOOLEAN,
                error_message TEXT,
                was_cached BOOLEAN,
                cache_hit BOOLEAN,
                timestamp TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_summary (
                _id TEXT PRIMARY KEY,
                date TEXT UNIQUE,
                total_requests INTEGER,
                total_errors INTEGER,
                total_cache_hits INTEGER,
                avg_response_time_ms REAL,
                min_response_time_ms REAL,
                max_response_time_ms REAL,
                most_analyzed_drugs TEXT,
                cache_hit_rate REAL,
                endpoint_stats TEXT,
                timestamp TEXT
            )
        ''')
        
        self.conn.commit()
    
    async def insert_one(self, collection: str, document: Dict[str, Any]) -> Any:
        """Insert a document into a collection"""
        table = self._get_table_name(collection)
        cols = ", ".join(document.keys())
        placeholders = ", ".join(["?"] * len(document))
        self.cursor.execute(
            f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
            tuple(document.values())
        )
        self.conn.commit()
        return type('InsertResult', (), {'inserted_id': document.get('_id')})()
    
    async def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict]:
        """Find one document"""
        table = self._get_table_name(collection)
        where_clause = " AND ".join([f"{k} = ?" for k in query.keys()])
        values = tuple(query.values())
        
        self.cursor.execute(f"SELECT * FROM {table} WHERE {where_clause}", values)
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    async def find(self, collection: str, query: Dict[str, Any] = None) -> List[Dict]:
        """Find documents"""
        table = self._get_table_name(collection)
        if query:
            where_clause = " AND ".join([f"{k} = ?" for k in query.keys()])
            values = tuple(query.values())
            self.cursor.execute(f"SELECT * FROM {table} WHERE {where_clause}", values)
        else:
            self.cursor.execute(f"SELECT * FROM {table}")
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    async def find_all(self, collection: str) -> List[Dict]:
        """Find all documents in a collection"""
        table = self._get_table_name(collection)
        self.cursor.execute(f"SELECT * FROM {table}")
        return [dict(row) for row in self.cursor.fetchall()]
    
    async def update_one(self, collection: str, query: Dict, update: Dict) -> Any:
        """Update one document"""
        table = self._get_table_name(collection)
        where_clause = " AND ".join([f"{k} = ?" for k in query.keys()])
        
        if "$set" in update:
            set_clause = ", ".join([f"{k} = ?" for k in update["$set"].keys()])
            values = tuple(update["$set"].values()) + tuple(query.values())
            self.cursor.execute(f"UPDATE {table} SET {set_clause} WHERE {where_clause}", values)
        
        self.conn.commit()
        return type('UpdateResult', (), {'modified_count': self.cursor.rowcount})()
    
    async def delete_one(self, collection: str, query: Dict) -> Any:
        """Delete one document"""
        table = self._get_table_name(collection)
        where_clause = " AND ".join([f"{k} = ?" for k in query.keys()])
        values = tuple(query.values())
        
        self.cursor.execute(f"DELETE FROM {table} WHERE {where_clause}", values)
        self.conn.commit()
        return type('DeleteResult', (), {'deleted_count': self.cursor.rowcount})()
    
    def _get_table_name(self, collection: str) -> str:
        """Map collection names to table names"""
        mapping = {
            "AnalysisBlueprint": "analysis_blueprint",
            "APIAnalytics": "api_analytics",
            "AnalyticsSummary": "analytics_summary"
        }
        return mapping.get(collection, collection.lower())
    
    def close(self):
        """Close database connection"""
        self.conn.close()

persistent_db = PersistentDatabase("pharma.db")

class AsyncDatabaseWrapper:
    def __init__(self, db):
        self.db = db
    
    def __getitem__(self, collection_name):
        return AsyncCollectionWrapper(self.db, collection_name)

class AsyncCollectionWrapper:
    def __init__(self, db, collection_name):
        self.db = db
        self.collection_name = collection_name
    
    async def insert_one(self, document):
        return await self.db.insert_one(self.collection_name, document)
    
    async def find_one(self, query):
        return await self.db.find_one(self.collection_name, query)
    
    async def find(self, query=None):
        return await self.db.find(self.collection_name, query)
    
    async def find_all(self):
        return await self.db.find_all(self.collection_name)
    
    async def update_one(self, query, update):
        return await self.db.update_one(self.collection_name, query, update)
    
    async def delete_one(self, query):
        return await self.db.delete_one(self.collection_name, query)

db = AsyncDatabaseWrapper(persistent_db)

backup_service = BackupService(db_path="pharma.db", backup_dir="backups")

class InMemoryCache:
    """In-memory cache with LRU"""

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
            logger.info(f"Cache HIT for SMILES: {smiles[:20]}...")
            return self.cache[key].copy()

        self.miss_count += 1
        logger.info(f"Cache MISS for SMILES: {smiles[:20]}...")
        return None

    def set(self, smiles: str, data: Dict) -> bool:
        """Store in cache"""
        key = self.generate_key(smiles)

        if len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.info(f"Cache full, removed oldest entry")

        self.cache[key] = data.copy()
        logger.info(f"Cached analysis for SMILES: {smiles[:20]}...")
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

class AnalyticsTracker:
    """Track API requests and performance"""

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
            analytics_doc = {
                "_id": str(ObjectId()),
                "request_id": str(uuid.uuid4()),
                "request_type": str(request_type),
                "endpoint": endpoint,
                "drug_name": drug_name,
                "smiles": smiles,
                "response_time_ms": response_time_ms,
                "status_code": status_code,
                "is_error": is_error,
                "error_message": error_message,
                "was_cached": was_cached,
                "cache_hit": was_cached,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await db['api_analytics'].insert_one(analytics_doc)
            logger.info(f"Analytics logged: {request_type} - {response_time_ms:.2f}ms")
        except Exception as e:
            logger.error(f"Analytics logging error: {type(e).__name__}: {e}")

    @staticmethod
    async def generate_daily_summary():
        """Generate daily analytics summary"""
        try:
            today = datetime.now(timezone.utc).date().isoformat()
            start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)

            analytics = await db['api_analytics'].find_all()
            
            today_analytics = [
                a for a in analytics 
                if start_of_day <= datetime.fromisoformat(a.get('timestamp', datetime.now(timezone.utc).isoformat())) < end_of_day
            ]

            if not today_analytics:
                return None

            total_requests = len(today_analytics)
            total_errors = sum(1 for a in today_analytics if a.get('is_error', False))
            total_cache_hits = sum(1 for a in today_analytics if a.get('cache_hit', False))

            response_times = [a.get('response_time_ms', 0) for a in today_analytics]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0    
            min_response_time = min(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0

            drug_counts = {}
            for a in today_analytics:
                drug_name = a.get('drug_name')
                if drug_name:
                    drug_counts[drug_name] = drug_counts.get(drug_name, 0) + 1

            most_analyzed = dict(sorted(drug_counts.items(), key=lambda x: x[1], reverse=True)[:10])

            endpoint_counts = {}
            for a in today_analytics:
                endpoint = a.get('endpoint', 'unknown')
                endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1

            cache_hit_rate = (total_cache_hits / total_requests * 100) if total_requests > 0 else 0

            summary = {
                "_id": str(ObjectId()),
                "date": today,
                "total_requests": total_requests,
                "total_errors": total_errors,
                "total_cache_hits": total_cache_hits,
                "avg_response_time_ms": round(avg_response_time, 2),
                "min_response_time_ms": round(min_response_time, 2),
                "max_response_time_ms": round(max_response_time, 2),
                "most_analyzed_drugs": json.dumps(most_analyzed),
                "cache_hit_rate": round(cache_hit_rate, 2),
                "endpoint_stats": json.dumps(endpoint_counts),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            await db['analytics_summary'].insert_one(summary)
            logger.info(f"Daily summary created for {today}")
            return summary
        except Exception as e:
            logger.error(f"Summary generation error: {type(e).__name__}: {e}")
            return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("FULL SYSTEM ONLINE: AI Brain, Database Heart & In-Memory Cache Connected!")        
        print("Cache Type: In-Memory (Zero Installation, Zero Storage!)")
        print("Analytics: Enabled (V-5)")
        print("Database: SQLite Persistent Storage")
        print("Export API: Enabled (V-6)")
        print("Backup & Recovery: Enabled (V-8)")
    except Exception as e:
        logger.error(f"Startup Error: {type(e).__name__}: {e}")

    yield

    print("Server shutting down...")
    logger.info("Database and cache cleaned up")


app = FastAPI(title="PHARMA-AI Formulation Optimizer", lifespan=lifespan)
api_router = APIRouter(prefix="/api")

# H-4: Drug Database with Therapeutic Category Tags
DRUG_DATABASE = {
    "Aspirin": {"smiles": "CC(=O)Oc1ccccc1C(=O)O", "bcs_class": "I", "molecular_weight": 180.16, "category": "Analgesic"},
    "Atorvastatin": {"smiles": "CC(C)c1c(C(=O)Nc2ccccc2F)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CC[C@@H](O)C[C@@H](O)CC(=O)O", "bcs_class": "II", "molecular_weight": 558.64, "category": "Cardiovascular"},
    "Amlodipine": {"smiles": "CCOC(=O)C1=C(COCCN)NC(C)=C(C(=O)OCC)C1c1ccccc1Cl", "bcs_class": "I", "molecular_weight": 408.88, "category": "Cardiovascular"},
    "Lisinopril": {"smiles": "OC(=O)[C@@H](CCc1ccccc1)N[C@@H](CC(=O)O)C(=O)N1CCC[C@H]1C(=O)O", "bcs_class": "III", "molecular_weight": 405.49, "category": "Cardiovascular"},
    "Metoprolol": {"smiles": "CC(C)NCC(O)COc1ccc(CCOC)cc1", "bcs_class": "I", "molecular_weight": 267.36, "category": "Cardiovascular"},
    "Warfarin": {"smiles": "OC(=O)CCCC1CC(=O)c2ccccc2O1", "bcs_class": "I", "molecular_weight": 308.33, "category": "Anticoagulant"},
    
    # H-1: Week 1 — Cardiovascular drugs (10 new entries)
    "Diltiazem": {"smiles": "COc1ccc2c(c1)SC(c1ccc(F)cc1)C(OC(C)=O)C(=O)N2CCN(C)C", "bcs_class": "I", "molecular_weight": 414.52, "category": "Cardiovascular"},
    "Verapamil": {"smiles": "COc1ccc(CCN(C)CCCC(C#N)(c2ccc(OC)c(OC)c2)C(C)C)cc1OC", "bcs_class": "I", "molecular_weight": 454.60, "category": "Cardiovascular"},
    "Digoxin": {"smiles": "CC1OC(OC2CC(O)C(OC3CC(O)C(OC4CCC5(C)C(CCC5C5CCC6(C)C(=CC(=O)OC6)C5)C4)O3)O2)C(O)CC1O", "bcs_class": "IV", "molecular_weight": 780.94, "category": "Cardiovascular"},
    "Spironolactone": {"smiles": "CC(=O)SC1CC2=CC(=O)CCC2(C)C2CCC3(C)C(CCC34CCC(=O)O4)C12", "bcs_class": "II", "molecular_weight": 416.57, "category": "Cardiovascular"},
    "Propranolol": {"smiles": "CC(C)NCC(O)COc1cccc2ccccc12", "bcs_class": "I", "molecular_weight": 259.34, "category": "Cardiovascular"},
    "Nifedipine": {"smiles": "COC(=O)C1=C(C)NC(C)=C(C(=O)OC)C1c1ccccc1[N+](=O)[O-]", "bcs_class": "II", "molecular_weight": 346.33, "category": "Cardiovascular"},
    "Carvedilol": {"smiles": "COc1ccccc1OCCNCC(O)COc1cccc2[nH]c3ccccc3c12", "bcs_class": "II", "molecular_weight": 406.47, "category": "Cardiovascular"},
    "Ramipril": {"smiles": "CCOC(=O)C(CCc1ccccc1)NC(C)C(=O)N1C2CCCC2CC1C(=O)O", "bcs_class": "I", "molecular_weight": 416.51, "category": "Cardiovascular"},
    "Candesartan": {"smiles": "CCOc1nc2cccc(C(=O)O)c2n1Cc1ccc(-c2ccccc2-c2nnn[nH]2)cc1", "bcs_class": "II", "molecular_weight": 440.45, "category": "Cardiovascular"},
    "Bisoprolol": {"smiles": "CC(C)NCC(O)COc1ccc(COCCOC(C)C)cc1", "bcs_class": "I", "molecular_weight": 325.44, "category": "Cardiovascular"},
    
    # H-2: Week 2 — Anti-infective drugs (10 new entries)
    "Azithromycin": {"smiles": "CCC1C(C(C(N(CC(CC(C(C(C(C(C(=O)O1)C)OC2CC(C(C(O2)C)O)(C)OC)C)OC3C(C(CC(O3)C)N(C)C)O)(C)O)C)C)C)O)(C)O", "bcs_class": "II", "molecular_weight": 748.98, "category": "Anti-infective"},
    "Levofloxacin": {"smiles": "CC1COc2c(N3CCN(C)CC3)c(F)cc3c(=O)c(C(=O)O)cn1c23", "bcs_class": "I", "molecular_weight": 361.37, "category": "Anti-infective"},
    "Fluconazole": {"smiles": "OC(Cn1cncn1)(Cn1cncn1)c1ccc(F)cc1F", "bcs_class": "I", "molecular_weight": 306.27, "category": "Anti-infective"},
    "Acyclovir": {"smiles": "C1=NC2=C(N1COCCO)N=C(NC2=O)N", "bcs_class": "III", "molecular_weight": 225.20, "category": "Anti-infective"},
    "Oseltamivir": {"smiles": "CCOC(=O)C1=CC(OC(CC)CC)C(NC(C)=O)C(N)C1", "bcs_class": "I", "molecular_weight": 312.40, "category": "Anti-infective"},
    "Rifampicin": {"smiles": "CC1C=CC=C(C(=O)NC2=CC(=C3C(=C2O)C(=C(C4=C3C(=O)C(O4)(OC=CC(C(C(C(C(C(C1O)C)OC(=O)C)C)O)C)OC)C)C)O)C=NN5CCN(CC5)C)C", "bcs_class": "II", "molecular_weight": 822.94, "category": "Anti-infective"},
    "Trimethoprim": {"smiles": "COc1cc(Cc2cnc(N)nc2N)cc(OC)c1OC", "bcs_class": "I", "molecular_weight": 290.32, "category": "Anti-infective"},
    "Nitrofurantoin": {"smiles": "O=C1CN(N=Cc2ccc(o2)[N+](=O)[O-])C(=O)N1", "bcs_class": "IV", "molecular_weight": 238.16, "category": "Anti-infective"},
    "Clindamycin": {"smiles": "CCCC1CC(N(C1)C)C(=O)NC(C(C2C(C(C(C(O2)SC)O)O)O)O)C(C)Cl", "bcs_class": "I", "molecular_weight": 424.98, "category": "Anti-infective"},
    # "Vancomycin": SMILES too complex for manual entry — fetched via PubChem CID 14969 during ingestion
    
    # H-5: Week 3 — CNS drugs (10 new entries)
    "Levetiracetam": {"smiles": "CCC(C(=O)NC)CC(=O)N1CCCC1", "bcs_class": "I", "molecular_weight": 170.21, "category": "CNS"},
    "Carbamazepine": {"smiles": "c1ccc2c(c1)C=Cc1ccccc1N2C(=O)N", "bcs_class": "II", "molecular_weight": 236.27, "category": "CNS"},
    "Valproic Acid": {"smiles": "CCCC(CCC)C(=O)O", "bcs_class": "I", "molecular_weight": 144.21, "category": "CNS"},
    "Lithium Carbonate": {"smiles": "[Li+].[Li+].[O-]C([O-])=O", "bcs_class": "I", "molecular_weight": 73.89, "category": "CNS"},
    "Risperidone": {"smiles": "CC1=C(C(=O)N2CCCCC2)C(=O)N(N1)c1ccc(F)cc1", "bcs_class": "II", "molecular_weight": 410.48, "category": "CNS"},
    "Quetiapine": {"smiles": "OCCOCCN1CCN(CC1)c1c2ccccc2Sc2ccccc21", "bcs_class": "II", "molecular_weight": 383.51, "category": "CNS"},
    "Duloxetine": {"smiles": "CNCC(Oc1cccc2ccccc12)c1cccs1", "bcs_class": "II", "molecular_weight": 297.41, "category": "CNS"},
    "Venlafaxine": {"smiles": "COc1ccc(C(CN(C)C)C2(O)CCCCC2)cc1", "bcs_class": "I", "molecular_weight": 277.40, "category": "CNS"},
    "Bupropion": {"smiles": "CC(NC(C)(C)C)C(=O)c1cccc(Cl)c1", "bcs_class": "I", "molecular_weight": 239.74, "category": "CNS"},
    "Escitalopram": {"smiles": "Fc1ccc(C2(OCCN(C)C)CCc3cc(C#N)ccc32)cc1", "bcs_class": "I", "molecular_weight": 324.39, "category": "CNS"},

        # H-6: Week 4 — Oncology drugs (10 new entries)
    "Imatinib": {"smiles": "Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc1nccc(-c2cccnc2)n1", "bcs_class": "II", "molecular_weight": 493.60, "category": "Oncology"},
    "Erlotinib": {"smiles": "COCCOc1cc2ncnc(Nc3cccc(C#C)c3)c2cc1OCCOC", "bcs_class": "II", "molecular_weight": 393.44, "category": "Oncology"},
    "Sorafenib": {"smiles": "CNC(=O)c1cc(Oc2ccc(NC(=O)Nc3ccc(Cl)c(C(F)(F)F)c3)cc2)ccn1", "bcs_class": "II", "molecular_weight": 464.82, "category": "Oncology"},
    "Sunitinib": {"smiles": "CCN(CC)CCNC(=O)c1c(C)[nH]c(C=c2[nH]c(=O)c3ccccc3/2)c1C", "bcs_class": "IV", "molecular_weight": 398.47, "category": "Oncology"},
    "Capecitabine": {"smiles": "CCCCCOC(=O)NC1=NC(=O)N(C=C1F)C1OC(C)C(O)C1O", "bcs_class": "I", "molecular_weight": 359.35, "category": "Oncology"},
    "Cyclophosphamide": {"smiles": "ClCCN(CCCl)P1(=O)NCCCO1", "bcs_class": "I", "molecular_weight": 261.08, "category": "Oncology"},
    "Doxorubicin": {"smiles": "COc1cccc2c1C(=O)c1c(O)c3c(c(O)c1C2=O)CC(O)(C(=O)CO)CC3OC1CC(N)C(O)C(C)O1", "bcs_class": "III", "molecular_weight": 543.52, "category": "Oncology"},
    "Paclitaxel": {"smiles": "CC1=C2C(C(=O)C3(C)CC(OC(=O)C(O)C(NC(=O)c4ccccc4)c4ccccc4)C(OC(C)=O)C(OC(=O)c4ccccc4)C3C2(C)C)OC(=O)CC1O", "bcs_class": "IV", "molecular_weight": 853.91, "category": "Oncology"},
    "Cisplatin": {"smiles": "[NH3][Pt]([NH3])(Cl)Cl", "bcs_class": "III", "molecular_weight": 300.05, "category": "Oncology"},
    # "Rituximab": Monoclonal antibody — no SMILES representation possible

}


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

def generate_3d_from_smiles(smiles: str) -> Optional[str]:
    """Generate 3D SDF structure from SMILES string"""
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
        logger.error(f"Error generating 3D structure: {type(e).__name__}: {e}")
        return None


def compute_confidence_score(smiles: str, bcs_class: str, molecular_weight: Optional[float] = None) -> float:
    """Calculate confidence score"""
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
    except Exception as e:
        logger.error(f"Error in compute_confidence_score: {type(e).__name__}: {e}")
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
    """Auto-assign BCS class"""
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
    """Flag unusual/outlier values"""
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
    """Estimate solubility score"""
    base_solubility = {"I": 75.0, "II": 30.0, "III": 80.0, "IV": 15.0}

    solubility = base_solubility.get(bcs_class, 50.0)

    if molecular_weight:
        if molecular_weight > 500:
            solubility *= 0.8
        elif molecular_weight < 200:
            solubility *= 1.1

    return min(solubility, 100.0)


@api_router.get("/")
async def root():
    return {"message": "PHARMA-AI Formulation Optimizer API", "version": "2.7.0"}


@api_router.get("/drugs")
async def get_drugs():
    """Get all available drugs from SQLite database"""
    start_time = time.time()
    
    try:
        drugs_from_db = await db['AnalysisBlueprint'].find_all()
        
        drugs = [
            {
                "name": drug.get("drug_name"),
                "smiles": drug.get("smiles"),
                "bcs_class": drug.get("bcs_class"),
                "molecular_weight": drug.get("molecular_weight")
            }
            for drug in drugs_from_db
        ]
        
        response_time = (time.time() - start_time) * 1000

        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.FETCH_DRUG,
                endpoint="/api/drugs",
                response_time_ms=response_time,
                status_code=200
            )
        except Exception as e:
            logger.error(f"Failed to log analytics for /drugs: {e}")

        return {"drugs": drugs, "total": len(drugs)}
    
    except Exception as e:
        logger.error(f"Error fetching drugs from database: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch drugs")


@api_router.get("/drugs/{drug_name}")
async def get_drug(drug_name: str):
    """Get specific drug information"""
    start_time = time.time()

    for name, info in DRUG_DATABASE.items():
        if name.lower() == drug_name.lower():
            response_time = (time.time() - start_time) * 1000

            try:
                await AnalyticsTracker.log_request(
                    request_type=RequestType.FETCH_DRUG,
                    endpoint="/api/drugs/{drug_name}",
                    response_time_ms=response_time,
                    status_code=200,
                    drug_name=name
                )
            except Exception as e:
                logger.error(f"Failed to log analytics: {e}")

            return {"name": name, **info}

    response_time = (time.time() - start_time) * 1000
    try:
        await AnalyticsTracker.log_request(
            request_type=RequestType.FETCH_DRUG,
            endpoint="/api/drugs/{drug_name}",
            response_time_ms=response_time,
            status_code=404,
            drug_name=drug_name,
            is_error=True,
            error_message="Drug not found"
        )
    except Exception as e:
        logger.error(f"Failed to log analytics: {e}")

    raise HTTPException(status_code=404, detail="Drug not found")


@api_router.get("/molecule3d")
async def get_molecule_3d(smiles: str = Query(..., description="SMILES string")):
    """Generate 3D molecular structure"""
    start_time = time.time()

    try:
        sdf_data = generate_3d_from_smiles(smiles)
        if not sdf_data:
            response_time = (time.time() - start_time) * 1000
            try:
                await AnalyticsTracker.log_request(
                    request_type=RequestType.GET_MOLECULE_3D,
                    endpoint="/api/molecule3d",
                    response_time_ms=response_time,
                    status_code=400,
                    smiles=smiles,
                    is_error=True,
                    error_message="Could not generate 3D structure"
                )
            except Exception as e:
                logger.error(f"Failed to log analytics: {e}")
            raise HTTPException(status_code=400, detail="Could not generate 3D structure")

        response_time = (time.time() - start_time) * 1000
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.GET_MOLECULE_3D,
                endpoint="/api/molecule3d",
                response_time_ms=response_time,
                status_code=200,
                smiles=smiles
            )
        except Exception as e:
            logger.error(f"Failed to log analytics: {e}")

        return {"sdf": sdf_data, "source": "RDKit (Computed)"}
    except HTTPException:
        raise
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.GET_MOLECULE_3D,
                endpoint="/api/molecule3d",
                response_time_ms=response_time,
                status_code=500,
                smiles=smiles,
                is_error=True,
                error_message=str(e)
            )
        except Exception as log_e:
            logger.error(f"Failed to log analytics: {log_e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/analyze")
async def analyze_drug(request: AnalysisRequest) -> AnalysisResponse:
    """Analyze drug with caching"""
    start_time = time.time()

    try:
        cached_result = await asyncio.to_thread(cache.get, request.smiles)
        if cached_result:
            result_copy = cached_result.copy()
            result_copy["cached"] = True
            response_time = (time.time() - start_time) * 1000

            try:
                await AnalyticsTracker.log_request(
                    request_type=RequestType.ANALYZE,
                    endpoint="/api/analyze",
                    response_time_ms=response_time,
                    status_code=200,
                    drug_name=request.drug_name,
                    smiles=request.smiles,
                    was_cached=True
                )
            except Exception as e:
                logger.error(f"Failed to log analytics: {e}")

            return AnalysisResponse(**result_copy)

        mol = Chem.MolFromSmiles(request.smiles)
        if not mol:
            response_time = (time.time() - start_time) * 1000
            try:
                await AnalyticsTracker.log_request(
                    request_type=RequestType.ANALYZE,
                    endpoint="/api/analyze",
                    response_time_ms=response_time,
                    status_code=400,
                    drug_name=request.drug_name,
                    smiles=request.smiles,
                    is_error=True,
                    error_message="Invalid SMILES string"
                )
            except Exception as e:
                logger.error(f"Failed to log analytics: {e}")
            raise HTTPException(status_code=400, detail="Invalid SMILES string")

        mol_3d = generate_3d_from_smiles(request.smiles)

        auto_bcs = auto_tag_bcs_class(
            molecular_weight=request.molecular_weight,
            solubility=None
        )

        solubility_score = estimate_solubility_score(auto_bcs, request.molecular_weight)

        confidence_score = compute_confidence_score(
            request.smiles,
            auto_bcs,
            request.molecular_weight
        )

        outlier_info = flag_outliers(solubility_score, confidence_score, request.molecular_weight)    

        analysis_doc = {
            "_id": str(ObjectId()),
            "drug_name": request.drug_name or "Unknown",
            "smiles": request.smiles,
            "bcs_class": auto_bcs,
            "solubility_score": solubility_score,
            "confidence_score": confidence_score,
            "molecular_weight": request.molecular_weight,
            "dose_mg": request.dose_mg,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db['AnalysisBlueprint'].insert_one(analysis_doc)

        logger.info(f"Analysis saved: {request.drug_name}")

        response_data = {
            "status": "success",
            "analysis_id": analysis_doc["_id"],
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

        await asyncio.to_thread(cache.set, request.smiles, response_data)

        response_time = (time.time() - start_time) * 1000
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.ANALYZE,
                endpoint="/api/analyze",
                response_time_ms=response_time,
                status_code=200,
                drug_name=request.drug_name,
                smiles=request.smiles,
                was_cached=False
            )
        except Exception as e:
            logger.error(f"Failed to log analytics: {e}")

        return AnalysisResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        try:
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
        except Exception as log_e:
            logger.error(f"Failed to log analytics: {log_e}")
        logger.error(f"Analysis error: {type(e).__name__}: {e}")
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
    """Get today's analytics summary"""
    try:
        today = datetime.now(timezone.utc).date().isoformat()
        summaries = await db['AnalyticsSummary'].find({"date": today})
        
        if not summaries:
            return {
                "message": "No analytics data for today yet",
                "date": today,
                "data": None
            }

        summary = summaries[0]
        return {
            "date": summary.get("date"),
            "total_requests": summary.get("total_requests"),
            "total_errors": summary.get("total_errors"),
            "total_cache_hits": summary.get("total_cache_hits"),
            "avg_response_time_ms": summary.get("avg_response_time_ms"),
            "min_response_time_ms": summary.get("min_response_time_ms"),
            "max_response_time_ms": summary.get("max_response_time_ms"),
            "most_analyzed_drugs": json.loads(summary.get("most_analyzed_drugs", "{}")),
            "cache_hit_rate": summary.get("cache_hit_rate"),
            "endpoint_stats": json.loads(summary.get("endpoint_stats", "{}"))
        }
    except Exception as e:
        logger.error(f"Error in get_daily_analytics: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/analytics/summary")
async def generate_analytics_summary():
    """Generate and return today's analytics summary"""
    try:
        summary = await AnalyticsTracker.generate_daily_summary()

        if not summary:
            return {"message": "No analytics data available"}

        return {
            "status": "success",
            "date": summary.get("date"),
            "total_requests": summary.get("total_requests"),
            "total_errors": summary.get("total_errors"),
            "total_cache_hits": summary.get("total_cache_hits"),
            "avg_response_time_ms": summary.get("avg_response_time_ms"),
            "min_response_time_ms": summary.get("min_response_time_ms"),
            "max_response_time_ms": summary.get("max_response_time_ms"),
            "most_analyzed_drugs": json.loads(summary.get("most_analyzed_drugs", "{}")),
            "cache_hit_rate": summary.get("cache_hit_rate"),
            "endpoint_stats": json.loads(summary.get("endpoint_stats", "{}"))
        }
    except Exception as e:
        logger.error(f"Error in generate_analytics_summary: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/analytics/requests")
async def get_recent_requests(limit: int = Query(50, le=500)):
    """Get recent API requests"""
    try:
        all_requests = await db['api_analytics'].find_all()
        requests_data = sorted(all_requests, key=lambda x: x.get('timestamp', datetime.now(timezone.utc).isoformat()), reverse=True)[:limit]

        requests_list = []
        for r in requests_data:
            requests_list.append({
                "request_id": r.get("request_id"),
                "request_type": r.get("request_type"),
                "endpoint": r.get("endpoint"),
                "drug_name": r.get("drug_name"),
                "response_time_ms": r.get("response_time_ms"),
                "status_code": r.get("status_code"),
                "is_error": r.get("is_error"),
                "was_cached": r.get("was_cached"),
                "timestamp": r.get("timestamp")
            })

        return {
            "total": len(requests_list),
            "requests": requests_list
        }
    except Exception as e:
        logger.error(f"Error in get_recent_requests: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/analyses")
async def get_analyses():
    """Get all stored analyses"""
    try:
        analyses = await db['AnalysisBlueprint'].find_all()
        return {
            "analyses": analyses,
            "total": len(analyses)
        }
    except Exception as e:
        logger.error(f"Error in get_analyses: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/analyses/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get specific analysis by ID"""
    try:
        analyses = await db['AnalysisBlueprint'].find({"_id": analysis_id})
        if not analyses:
            raise HTTPException(status_code=404, detail="Analysis not found")

        return analyses[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_analysis: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/export/analyses")
async def export_analyses(
    format: str = Query("json", pattern="^(json|csv)$", description="Export format: json or csv"),
    drug_name: Optional[str] = Query(None, description="Filter by drug name"),
    bcs_class: Optional[str] = Query(None, description="Filter by BCS class"),
    min_confidence: Optional[float] = Query(None, description="Minimum confidence score"),
    max_solubility: Optional[float] = Query(None, description="Maximum solubility score"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    download: bool = Query(False, description="Download as file")
):
    """Export analyses data"""
    start_time = time.time()
    
    try:
        all_analyses = await db['AnalysisBlueprint'].find_all()
        
        filtered_analyses = await ExportService.filter_analyses(
            all_analyses,
            drug_name=drug_name,
            bcs_class=bcs_class,
            min_confidence=min_confidence,
            max_solubility=max_solubility,
            date_from=date_from,
            date_to=date_to
        )
        
        if format == "json":
            exported_data = await ExportService.export_to_json(filtered_analyses, pretty=True)
            media_type = "application/json"
            filename = ExportService.get_export_filename("json", "analyses")
        else:
            exported_data = await ExportService.export_to_csv(filtered_analyses)
            media_type = "text/csv"
            filename = ExportService.get_export_filename("csv", "analyses")
        
        response_time = (time.time() - start_time) * 1000
        
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/export/analyses",
                response_time_ms=response_time,
                status_code=200
            )
        except Exception as e:
            logger.error(f"Failed to log analytics: {e}")
        
        if download:
            return StreamingResponse(
                iter([exported_data]),
                media_type=media_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:
            return {
                "status": "success",
                "format": format,
                "total_records": len(filtered_analyses),
                "data": json.loads(exported_data) if format == "json" else exported_data
            }
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/export/analyses",
                response_time_ms=response_time,
                status_code=500,
                is_error=True,
                error_message=str(e)
            )
        except Exception as log_e:
            logger.error(f"Failed to log analytics: {log_e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@api_router.get("/export/analytics")
async def export_analytics(
    format: str = Query("json", pattern="^(json|csv)$", description="Export format: json or csv"),
    request_type: Optional[str] = Query(None, description="Filter by request type"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    download: bool = Query(False, description="Download as file")
):
    """Export analytics data"""
    start_time = time.time()
    
    try:
        all_analytics = await db['api_analytics'].find_all()
        
        filtered_analytics = all_analytics.copy()
        
        if request_type:
            filtered_analytics = [a for a in filtered_analytics if a.get('request_type') == request_type]
        
        if endpoint:
            filtered_analytics = [a for a in filtered_analytics if a.get('endpoint') == endpoint]
        
        if format == "json":
            exported_data = await ExportService.export_analytics_json(filtered_analytics, pretty=True)
            media_type = "application/json"
            filename = ExportService.get_export_filename("json", "analytics")
        else:
            exported_data = await ExportService.export_analytics_csv(filtered_analytics)
            media_type = "text/csv"
            filename = ExportService.get_export_filename("csv", "analytics")
        
        response_time = (time.time() - start_time) * 1000
        
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/export/analytics",
                response_time_ms=response_time,
                status_code=200
            )
        except Exception as e:
            logger.error(f"Failed to log analytics: {e}")
        
        if download:
            return StreamingResponse(
                iter([exported_data]),
                media_type=media_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:
            return {
                "status": "success",
                "format": format,
                "total_records": len(filtered_analytics),
                "data": json.loads(exported_data) if format == "json" else exported_data
            }
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/export/analytics",
                response_time_ms=response_time,
                status_code=500,
                is_error=True,
                error_message=str(e)
            )
        except Exception as log_e:
            logger.error(f"Failed to log analytics: {log_e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@api_router.get("/export/summary")
async def export_summary():
    """
    ✅ V-6: 
    
    Returns:
    - Total analyses
    - Total analytics records
    - Cache statistics
    - Daily summary
    
    ✅ V-6: Export comprehensive summary
    
    Returns:
    - Total analyses
    - Total analytics records
    - Cache statistics
    - Daily summary
    """
    start_time = time.time()
    
    try:
        analyses = await db['AnalysisBlueprint'].find_all()
        analytics = await db['api_analytics'].find_all()
        summaries = await db['AnalyticsSummary'].find_all()
        
        summary_data = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "total_analyses": len(analyses),
            "total_analytics_records": len(analytics),
            "cache_stats": cache.get_stats(),
            "daily_summaries": summaries,
            "drugs_analyzed": list(set([a.get('drug_name') for a in analyses if a.get('drug_name')])),
            "analyses_summary": {
                "total": len(analyses),
                "by_bcs_class": {
                    "I": len([a for a in analyses if a.get('bcs_class') == 'I']),
                    "II": len([a for a in analyses if a.get('bcs_class') == 'II']),
                    "III": len([a for a in analyses if a.get('bcs_class') == 'III']),
                    "IV": len([a for a in analyses if a.get('bcs_class') == 'IV']),
                },
                "avg_confidence": round(sum([a.get('confidence_score', 0) for a in analyses]) / len(analyses), 2) if analyses else 0,
                "avg_solubility": round(sum([a.get('solubility_score', 0) for a in analyses]) / len(analyses), 2) if analyses else 0,
            }
        }    
        
        response_time = (time.time() - start_time) * 1000
        
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/export/summary",
                response_time_ms=response_time,
                status_code=200
            )
        except Exception as e:
            logger.error(f"Failed to log analytics: {e}")
        
        return summary_data
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/export/summary",
                response_time_ms=response_time,
                status_code=500,
                is_error=True,
                error_message=str(e)
            )
        except Exception as log_e:
            logger.error(f"Failed to log analytics: {log_e}")
        raise HTTPException(status_code=500, detail=f"Summary export failed: {str(e)}")


@api_router.post("/backup/create")
async def create_backup(
    backup_type: str = Query("full", pattern="^(full|incremental)$", description="Backup type: full or incremental"),
    compress: bool = Query(True, description="Compress backup (for full backups)")
):
    """Create database backup"""
    start_time = time.time()
    
    try:
        if backup_type == "full":
            backup_info = await backup_service.create_full_backup(compress=compress)
        else:
            backup_info = await backup_service.create_incremental_backup()
        
        response_time = (time.time() - start_time) * 1000
        
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/backup/create",
                response_time_ms=response_time,
                status_code=200
            )
        except Exception as e:
            logger.error(f"Failed to log analytics: {e}")
        
        return backup_info
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/backup/create",
                response_time_ms=response_time,
                status_code=500,
                is_error=True,
                error_message=str(e)
            )
        except Exception as log_e:
            logger.error(f"Failed to log analytics: {log_e}")
        raise HTTPException(status_code=500, detail=f"Backup creation failed: {str(e)}")


@api_router.get("/backup/list")
async def list_backups(backup_type: Optional[str] = Query(None, pattern="^(full|incremental)$")):
    """List all available backups"""
    start_time = time.time()
    
    try:
        backups = await backup_service.list_backups(backup_type=backup_type)
        response_time = (time.time() - start_time) * 1000
        
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/backup/list",
                response_time_ms=response_time,
                status_code=200
            )
        except Exception as e:
            logger.error(f"Failed to log analytics: {e}")
        
        return {
            "total_backups": len(backups),
            "backups": backups
        }
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/backup/list",
                response_time_ms=response_time,
                status_code=500,
                is_error=True,
                error_message=str(e)
            )
        except Exception as log_e:
            logger.error(f"Failed to log analytics: {log_e}")
        raise HTTPException(status_code=500, detail=f"List backups failed: {str(e)}")


@api_router.post("/backup/restore")
async def restore_backup(backup_filename: str = Query(..., description="Backup filename to restore")):
    """Restore database from backup"""
    start_time = time.time()
    
    try:
        restore_info = await backup_service.restore_backup(backup_filename)
        response_time = (time.time() - start_time) * 1000
        
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/backup/restore",
                response_time_ms=response_time,
                status_code=200
            )
        except Exception as e:
            logger.error(f"Failed to log analytics: {e}")
        
        return restore_info
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/backup/restore",
                response_time_ms=response_time,
                status_code=500,
                is_error=True,
                error_message=str(e)
            )
        except Exception as log_e:
            logger.error(f"Failed to log analytics: {log_e}")
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")


@api_router.delete("/backup/cleanup")
async def cleanup_old_backups(days: int = Query(30, ge=1, description="Delete backups older than N days")):
    """Delete old backups to save space"""
    start_time = time.time()
    
    try:
        cleanup_info = await backup_service.delete_old_backups(days=days)
        response_time = (time.time() - start_time) * 1000
        
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/backup/cleanup",
                response_time_ms=response_time,
                status_code=200
            )
        except Exception as e:
            logger.error(f"Failed to log analytics: {e}")
        
        return cleanup_info
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/backup/cleanup",
                response_time_ms=response_time,
                status_code=500,
                is_error=True,
                error_message=str(e)
            )
        except Exception as log_e:
            logger.error(f"Failed to log analytics: {log_e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@api_router.get("/backup/validate")
async def validate_backup(backup_filename: str = Query(..., description="Backup filename to validate")):
    """Validate backup integrity"""
    start_time = time.time()
    
    try:
        validate_info = await backup_service.validate_backup(backup_filename)
        response_time = (time.time() - start_time) * 1000
        
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/backup/validate",
                response_time_ms=response_time,
                status_code=200
            )
        except Exception as e:
            logger.error(f"Failed to log analytics: {e}")
        
        return validate_info
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/backup/validate",
                response_time_ms=response_time,
                status_code=500,
                is_error=True,
                error_message=str(e)
            )
        except Exception as log_e:
            logger.error(f"Failed to log analytics: {log_e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@api_router.get("/backup/stats")
async def get_backup_stats():
    """Get backup statistics"""
    start_time = time.time()
    
    try:
        stats = await backup_service.get_backup_stats()
        response_time = (time.time() - start_time) * 1000
        
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/backup/stats",
                response_time_ms=response_time,
                status_code=200
            )
        except Exception as e:
            logger.error(f"Failed to log analytics: {e}")
        
        return stats
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        try:
            await AnalyticsTracker.log_request(
                request_type=RequestType.EXPORT_DATA,
                endpoint="/api/backup/stats",
                response_time_ms=response_time,
                status_code=500,
                is_error=True,
                error_message=str(e)
            )
        except Exception as log_e:
            logger.error(f"Failed to log analytics: {log_e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    server_port = int(os.environ.get('SERVER_PORT', 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=server_port, reload=False)