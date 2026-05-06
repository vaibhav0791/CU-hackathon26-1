# backend/data_ingestion_engine.py
import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class IngestionStats:
    """Statistics for data ingestion"""
    dataset: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED
    total_records: int = 0
    ingested_records: int = 0
    failed_records: int = 0
    skipped_records: int = 0
    start_time: str = None
    end_time: str = None
    error_message: str = None

class DataIngestionEngine:
    """Main orchestrator for all 19 datasets"""
    
    def __init__(self, db_path: str = "pharma.db", cache_dir: str = "ingestion_cache"):
        self.db_path = db_path
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.stats: Dict[str, IngestionStats] = {}
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite with all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Drug Discovery Tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chembl_bioactivity (
                compound_id TEXT PRIMARY KEY,
                compound_name TEXT,
                smiles TEXT,
                target_name TEXT,
                bioactivity_type TEXT,
                bioactivity_value REAL,
                units TEXT,
                assay_type TEXT,
                ingestion_date TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pubchem_properties (
                cid INTEGER PRIMARY KEY,
                compound_name TEXT,
                smiles TEXT,
                molecular_weight REAL,
                logp REAL,
                h_bond_donors INTEGER,
                h_bond_acceptors INTEGER,
                tpsa REAL,
                rotatable_bonds INTEGER,
                ingestion_date TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zinc15_compounds (
                zinc_id TEXT PRIMARY KEY,
                compound_name TEXT,
                smiles TEXT,
                molecular_weight REAL,
                price_min REAL,
                price_max REAL,
                suppliers INTEGER,
                ingestion_date TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qm9_properties (
                molecule_id TEXT PRIMARY KEY,
                smiles TEXT,
                homo_energy REAL,
                lumo_energy REAL,
                gap_energy REAL,
                dipole_moment REAL,
                polarizability REAL,
                ingestion_date TEXT
            )
        ''')
        
        # Target Discovery Tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS uniprot_sequences (
                uniprot_id TEXT PRIMARY KEY,
                protein_name TEXT,
                gene_name TEXT,
                organism TEXT,
                sequence TEXT,
                sequence_length INTEGER,
                ingestion_date TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pdb_structures (
                pdb_id TEXT PRIMARY KEY,
                title TEXT,
                resolution REAL,
                experiment_type TEXT,
                biological_assembly TEXT,
                binding_sites TEXT,
                ingestion_date TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS geo_expression (
                geo_id TEXT PRIMARY KEY,
                study_title TEXT,
                organism TEXT,
                disease_condition TEXT,
                sample_count INTEGER,
                genes_profiled INTEGER,
                data_url TEXT,
                ingestion_date TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS string_interactions (
                interaction_id TEXT PRIMARY KEY,
                protein_a TEXT,
                protein_b TEXT,
                interaction_type TEXT,
                combined_score REAL,
                neighborhood_score REAL,
                fusion_score REAL,
                cooccurrence_score REAL,
                homology_score REAL,
                coexpression_score REAL,
                experimental_score REAL,
                database_score REAL,
                textmining_score REAL,
                ingestion_date TEXT
            )
        ''')
        
        # Clinical Trial Tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clinical_trials (
                nct_id TEXT PRIMARY KEY,
                trial_title TEXT,
                condition TEXT,
                phase TEXT,
                status TEXT,
                enrollment INTEGER,
                start_date TEXT,
                completion_date TEXT,
                study_type TEXT,
                primary_outcome TEXT,
                ingestion_date TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mimic_patients (
                patient_id TEXT PRIMARY KEY,
                gender TEXT,
                age INTEGER,
                mortality INTEGER,
                admission_count INTEGER,
                hospital_expire_flag INTEGER,
                ingestion_date TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aact_trials (
                nct_id TEXT PRIMARY KEY,
                overall_status TEXT,
                phase TEXT,
                enrollment INTEGER,
                primary_completion_date TEXT,
                results_available BOOLEAN,
                adverse_events_count INTEGER,
                serious_adverse_events_count INTEGER,
                ingestion_date TEXT
            )
        ''')
        
        # Formulation Tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drugbank_formulations (
                drug_id TEXT PRIMARY KEY,
                drug_name TEXT,
                smiles TEXT,
                route_of_administration TEXT,
                dosage_form TEXT,
                excipients TEXT,
                solubility_comment TEXT,
                ingestion_date TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS esol_solubility (
                compound_id TEXT PRIMARY KEY,
                smiles TEXT,
                solubility_value REAL,
                bcs_class TEXT,
                mw REAL,
                logp REAL,
                hbd INTEGER,
                hba INTEGER,
                ingestion_date TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tox21_toxicity (
                compound_id TEXT PRIMARY KEY,
                smiles TEXT,
                nr_ar_lbd INTEGER,
                nr_ar INTEGER,
                nr_ahr INTEGER,
                nr_aromatase INTEGER,
                nr_er INTEGER,
                nr_er_lbd INTEGER,
                nr_pxr INTEGER,
                sr_atad5 INTEGER,
                sr_hse INTEGER,
                sr_mmp INTEGER,
                sr_p53 INTEGER,
                ingestion_date TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gras_excipients (
                excipient_id TEXT PRIMARY KEY,
                excipient_name TEXT,
                usage_type TEXT,
                fda_status TEXT,
                molecular_weight REAL,
                solubility TEXT,
                ph_range TEXT,
                ingestion_date TEXT
            )
        ''')
        
        # Ingestion Status Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingestion_status (
                dataset_name TEXT PRIMARY KEY,
                status TEXT,
                total_records INTEGER,
                ingested_records INTEGER,
                failed_records INTEGER,
                skipped_records INTEGER,
                start_time TEXT,
                end_time TEXT,
                error_message TEXT,
                last_updated TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized successfully")
    
    async def ingest_all_datasets(self):
        """Orchestrate ingestion of all 19 datasets"""
        logger.info("=" * 70)
        logger.info("🚀 STARTING COMPREHENSIVE DATA INGESTION FOR ALL 19 DATASETS")
        logger.info("=" * 70)
        
        # Drug Discovery
        await self.ingest_drug_discovery()
        
        # Target Discovery
        await self.ingest_target_discovery()
        
        # Clinical Trials
        await self.ingest_clinical_trials()
        
        # Formulation
        await self.ingest_formulation()
        
        # Summary
        self.print_summary()
    
    async def ingest_drug_discovery(self):
        """Ingest all Drug Discovery datasets"""
        logger.info("\n" + "="*70)
        logger.info("📊 PHASE 1: DRUG DISCOVERY DATASETS")
        logger.info("="*70)
        
        from fetchers.drug_discovery_fetcher import DrugDiscoveryFetcher
        fetcher = DrugDiscoveryFetcher(self.db_path, self.cache_dir)
        
        # ChEMBL
        logger.info("\n1️⃣ Ingesting ChEMBL Bioactivity...")
        await fetcher.fetch_chembl()
        
        # PubChem
        logger.info("\n2️⃣ Ingesting PubChem Molecular Properties...")
        await fetcher.fetch_pubchem()
        
        # ZINC15
        logger.info("\n3️⃣ Ingesting ZINC15 Compounds...")
        await fetcher.fetch_zinc15()
        
        # QM9
        logger.info("\n4️⃣ Ingesting QM9 Quantum Properties...")
        await fetcher.fetch_qm9()
    
    async def ingest_target_discovery(self):
        """Ingest all Target Discovery datasets"""
        logger.info("\n" + "="*70)
        logger.info("🔬 PHASE 2: TARGET DISCOVERY DATASETS")
        logger.info("="*70)
        
        from fetchers.target_discovery_fetcher import TargetDiscoveryFetcher
        fetcher = TargetDiscoveryFetcher(self.db_path, self.cache_dir)
        
        # UniProt
        logger.info("\n1️⃣ Ingesting UniProt Sequences...")
        await fetcher.fetch_uniprot()
        
        # PDB
        logger.info("\n2️⃣ Ingesting RCSB PDB Structures...")
        await fetcher.fetch_pdb()
        
        # GEO
        logger.info("\n3️⃣ Ingesting GEO Expression Data...")
        await fetcher.fetch_geo()
        
        # STRING DB
        logger.info("\n4️⃣ Ingesting STRING DB Interactions...")
        await fetcher.fetch_string()
    
    async def ingest_clinical_trials(self):
        """Ingest all Clinical Trial datasets"""
        logger.info("\n" + "="*70)
        logger.info("🏥 PHASE 3: CLINICAL TRIAL DATASETS")
        logger.info("="*70)
        
        from fetchers.clinical_trial_fetcher import ClinicalTrialFetcher
        fetcher = ClinicalTrialFetcher(self.db_path, self.cache_dir)
        
        # ClinicalTrials.gov
        logger.info("\n1️⃣ Ingesting ClinicalTrials.gov...")
        await fetcher.fetch_clinicaltrials()
        
        # MIMIC-III
        logger.info("\n2️⃣ Ingesting MIMIC-III Patient Data...")
        await fetcher.fetch_mimic()
        
        # AACT
        logger.info("\n3️⃣ Ingesting AACT Trial Data...")
        await fetcher.fetch_aact()
    
    async def ingest_formulation(self):
        """Ingest all Formulation datasets"""
        logger.info("\n" + "="*70)
        logger.info("⚗️  PHASE 4: FORMULATION DATASETS")
        logger.info("="*70)
        
        from fetchers.formulation_fetcher import FormulationFetcher
        fetcher = FormulationFetcher(self.db_path, self.cache_dir)
        
        # DrugBank
        logger.info("\n1️⃣ Ingesting DrugBank Formulations...")
        await fetcher.fetch_drugbank()
        
        # ESOL
        logger.info("\n2️⃣ Ingesting ESOL Solubility...")
        await fetcher.fetch_esol()
        
        # Tox21
        logger.info("\n3️⃣ Ingesting Tox21 Toxicity...")
        await fetcher.fetch_tox21()
        
        # GRAS
        logger.info("\n4️⃣ Ingesting GRAS Excipients...")
        await fetcher.fetch_gras()
    
    def print_summary(self):
        """Print ingestion summary"""
        logger.info("\n" + "="*70)
        logger.info("📈 INGESTION SUMMARY")
        logger.info("="*70)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tables = [
            'chembl_bioactivity', 'pubchem_properties', 'zinc15_compounds', 'qm9_properties',
            'uniprot_sequences', 'pdb_structures', 'geo_expression', 'string_interactions',
            'clinical_trials', 'mimic_patients', 'aact_trials',
            'drugbank_formulations', 'esol_solubility', 'tox21_toxicity', 'gras_excipients'
        ]
        
        total_records = 0
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            if count > 0:
                logger.info(f"✅ {table}: {count} records")
                total_records += count
            else:
                logger.info(f"⚠️  {table}: 0 records")
        
        logger.info("="*70)
        logger.info(f"🎉 TOTAL RECORDS INGESTED: {total_records}")
        logger.info("="*70)
        
        conn.close()

if __name__ == "__main__":
    engine = DataIngestionEngine()
    asyncio.run(engine.ingest_all_datasets())