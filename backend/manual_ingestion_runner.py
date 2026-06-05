# backend/manual_ingestion_runner.py
"""
Main Data Ingestion Pipeline Orchestrator
Coordinates fetching and ingestion of pharmaceutical data from multiple sources
"""

import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from ingestors.enhanced_db_handler import EnhancedDatabaseHandler
from fetchers.drug_discovery_fetcher import DrugDiscoveryFetcher
from fetchers.target_discovery_fetcher import TargetDiscoveryFetcher
from fetchers.clinical_trial_fetcher import ClinicalTrialFetcher
from fetchers.formulation_fetcher import FormulationFetcher

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ManualDataIngestionEngine:
    """
    Main ingestion orchestrator that:
    1. Fetches data from multiple sources
    2. Validates data quality
    3. Deduplicates records
    4. Stores in database
    5. Generates quality reports
    """
    
    def __init__(self, db_path: str = "pharma_enhanced.db", cache_dir: str = "ingestion_cache"):
        """Initialize all components"""
        self.db_path = db_path
        self.cache_dir = cache_dir
        
        # Initialize database with validation & dedup support
        self.db = EnhancedDatabaseHandler(self.db_path)
        
        # Initialize fetchers
        self._initialize_fetchers()
        
        self.total_records = 0
        self.start_time = None
        self.ingestion_summary = {}
    
    def _initialize_fetchers(self):
        """Initialize all data fetchers"""
        try:
            self.drug_fetcher = DrugDiscoveryFetcher(self.db_path, self.cache_dir)
            self.target_fetcher = TargetDiscoveryFetcher(self.db_path, self.cache_dir)
            self.trial_fetcher = ClinicalTrialFetcher(self.db_path, self.cache_dir)
            self.formulation_fetcher = FormulationFetcher(self.db_path, self.cache_dir)
            
            logger.info("✅ All fetchers initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing fetchers: {e}")
            raise
    
    async def run_all_ingestions(self):
        """Main execution flow - run all ingestions"""
        self.start_time = datetime.now()
        logger.info("🚀 Starting comprehensive data ingestion pipeline")
        logger.info(f"⏰ Start time: {self.start_time}\n")
        
        try:
            # Fetch data from all sources
            data_collections = await self._fetch_all_data()
            
            # Ingest all data with validation & deduplication
            await self._ingest_all_data(data_collections)
            
            # Generate quality report
            self._generate_ingestion_report()
            
        except Exception as e:
            logger.error(f"❌ Fatal error during ingestion: {e}")
            self.db.log_ingestion(
                dataset_name="comprehensive_pipeline",
                total_records=self.total_records,
                status="FAILED",
                errors=str(e)
            )
            raise
    
    async def _fetch_all_data(self) -> Dict[str, List]:
        """Fetch data from all sources in parallel"""
        logger.info("📡 FETCHING DATA FROM ALL SOURCES...\n")
        
        # Fetch in parallel for speed
        drug_data, target_data, trial_data, formulation_data = await asyncio.gather(
            self._fetch_step("drug_discovery", self.drug_fetcher.fetch, 1),
            self._fetch_step("target_discovery", self.target_fetcher.fetch, 2),
            self._fetch_step("clinical_trials", self.trial_fetcher.fetch, 3),
            self._fetch_step("formulations", self.formulation_fetcher.fetch, 4),
        )
        
        return {
            "drug": drug_data,
            "target": target_data,
            "trial": trial_data,
            "formulation": formulation_data
        }
    
    async def _fetch_step(self, name: str, fetcher_func, step_num: int) -> List:
        """Execute a single fetch step with logging"""
        logger.info(f"📦 STEP {step_num}/4: Fetching {name} data...")
        try:
            data = await fetcher_func()
            logger.info(f"✅ Fetched {len(data)} {name} records\n")
            return data
        except Exception as e:
            logger.error(f"❌ Error fetching {name}: {e}\n")
            return []
    
    async def _ingest_all_data(self, data_collections: Dict[str, List]):
        """Ingest all fetched data with validation"""
        logger.info("\n✅ STEP 5/5: Ingesting data with validation...\n")
        
        ingestion_config = [
            {
                "name": "Drug Discovery",
                "emoji": "💊",
                "data_key": "drug",
                "table": "chembl_bioactivity",
                "unique_field": "compound_id"
            },
            {
                "name": "Target Discovery",
                "emoji": "🎯",
                "data_key": "target",
                "table": "string_interactions",
                "unique_field": "interaction_id"
            },
            {
                "name": "Clinical Trials",
                "emoji": "🏥",
                "data_key": "trial",
                "table": "clinical_trials",
                "unique_field": "nct_id"
            },
            {
                "name": "Formulations",
                "emoji": "⚗️",
                "data_key": "formulation",
                "table": "drugbank_formulations",
                "unique_field": "drug_id"
            }
        ]
        
        for config in ingestion_config:
            data = data_collections.get(config["data_key"], [])
            
            if data:
                logger.info(f"{config['emoji']} Ingesting {len(data)} {config['name'].lower()} records...")
                
                stats = self.db.batch_insert_with_validation(
                    table=config["table"],
                    records=data,
                    unique_field=config["unique_field"]
                )
                
                self.total_records += stats["inserted"]
                
                logger.info(
                    f"✅ {config['name']}: "
                    f"Inserted={stats['inserted']}, "
                    f"Duplicates={stats['duplicates']}, "
                    f"Errors={stats['errors']}\n"
                )
                
                self.ingestion_summary[config["name"]] = stats
                
                # Log to database
                self.db.log_ingestion(
                    dataset_name=config["data_key"],
                    total_records=len(data),
                    status="SUCCESS"
                )
    
    def _generate_ingestion_report(self):
        """Generate comprehensive ingestion report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        logger.info("\n" + "="*80)
        logger.info("📊 INGESTION COMPLETE - QUALITY REPORT")
        logger.info("="*80)
        logger.info(f"⏱️ Duration: {duration:.2f} seconds")
        logger.info(f"📈 Total Records Inserted: {self.total_records}")
        
        # Print database stats
        stats = self.db.get_stats()
        logger.info("\n📦 DATABASE STATISTICS:")
        for table, count in sorted(stats.items()):
            if count > 0:
                logger.info(f"  ✅ {table:40s}: {count:7,d} records")
            else:
                logger.info(f"  ⚪ {table:40s}: {count:7,d} records")
        
        # Print quality report
        logger.info("\n")
        self.db.print_quality_report()
        
        # Save report to JSON
        self._save_report_to_json(duration, stats)
    
    def _save_report_to_json(self, duration: float, stats: Dict):
        """Save detailed ingestion report to JSON"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "total_records_inserted": self.total_records,
            "database_statistics": stats,
            "ingestion_summary": self.ingestion_summary,
            "quality_metrics": self.db.quality_metrics
        }
        
        report_path = Path("ingestion_reports")
        report_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_path / f"ingestion_report_{timestamp}.json"
        
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\n✅ Report saved to: {report_file}\n")


async def main():
    """Main entry point"""
    try:
        engine = ManualDataIngestionEngine()
        await engine.run_all_ingestions()
        logger.info("✅ Data ingestion pipeline completed successfully!")
    except Exception as e:
        logger.error(f"\n❌ Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())