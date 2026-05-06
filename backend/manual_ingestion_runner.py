# backend/manual_ingestion_runner.py
import asyncio
import logging
import sys
from datetime import datetime
from ingestors.enhanced_db_handler import EnhancedDatabaseHandler
from fetchers.drug_discovery_fetcher import DrugDiscoveryFetcher
from fetchers.target_discovery_fetcher import TargetDiscoveryFetcher
from fetchers.clinical_trial_fetcher import ClinicalTrialFetcher
from fetchers.formulation_fetcher import FormulationFetcher

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ManualDataIngestionEngine:
    """Manual data ingestion engine for all 19 datasets"""
    
    def __init__(self):
        self.db = EnhancedDatabaseHandler("pharma_enhanced.db")
        self.drug_fetcher = DrugDiscoveryFetcher()
        self.target_fetcher = TargetDiscoveryFetcher()
        self.trial_fetcher = ClinicalTrialFetcher()
        self.formulation_fetcher = FormulationFetcher()
        self.total_records = 0
    
    async def ingest_all(self):
        """Ingest all datasets"""
        logger.info("=" * 80)
        logger.info("🚀 MANUAL DATA INGESTION ENGINE - ALL 19 DATASETS")
        logger.info(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        logger.info("")
        
        try:
            # PHASE 1: Drug Discovery
            logger.info("=" * 80)
            logger.info("📊 PHASE 1: DRUG DISCOVERY DATASETS (4/19)")
            logger.info("=" * 80)
            logger.info("")
            
            await self._ingest_chembl()
            await self._ingest_pubchem()
            await self._ingest_zinc15()
            await self._ingest_qm9()
            
            # PHASE 2: Target Discovery
            logger.info("=" * 80)
            logger.info("🔬 PHASE 2: TARGET DISCOVERY DATASETS (4/19)")
            logger.info("=" * 80)
            logger.info("")
            
            await self._ingest_uniprot()
            await self._ingest_pdb()
            await self._ingest_geo()
            await self._ingest_string()
            
            # PHASE 3: Clinical Trials
            logger.info("=" * 80)
            logger.info("🏥 PHASE 3: CLINICAL TRIAL DATASETS (3/19)")
            logger.info("=" * 80)
            logger.info("")
            
            await self._ingest_clinical_trials()
            await self._ingest_mimic()
            await self._ingest_aact()
            
            # PHASE 4: Formulation
            logger.info("=" * 80)
            logger.info("⚗️  PHASE 4: FORMULATION DATASETS (4/19)")
            logger.info("=" * 80)
            logger.info("")
            
            await self._ingest_drugbank()
            await self._ingest_gras()
            await self._ingest_esol()
            await self._ingest_tox21()
            
            # Summary
            self._print_summary()
            
        except Exception as e:
            logger.error(f"❌ Error during ingestion: {e}")
            import traceback
            traceback.print_exc()
        finally:
            logger.info("✅ Ingestion engine closing...")
    
    async def _ingest_chembl(self):
        chembl_records = await self.drug_fetcher.fetch_chembl()
        inserted = self.db.batch_insert('chembl_bioactivity', chembl_records)
        self.db.log_ingestion('chembl_bioactivity', inserted, 'SUCCESS')
        self.total_records += inserted
    
    async def _ingest_pubchem(self):
        pubchem_records = await self.drug_fetcher.fetch_pubchem()
        inserted = self.db.batch_insert('pubchem_properties', pubchem_records)
        self.db.log_ingestion('pubchem_properties', inserted, 'SUCCESS')
        self.total_records += inserted
    
    async def _ingest_zinc15(self):
        zinc_records = await self.drug_fetcher.fetch_zinc15()
        inserted = self.db.batch_insert('zinc15_compounds', zinc_records)
        self.db.log_ingestion('zinc15_compounds', inserted, 'SUCCESS')
        self.total_records += inserted
    
    async def _ingest_qm9(self):
        qm9_records = await self.drug_fetcher.fetch_qm9()
        inserted = self.db.batch_insert('qm9_properties', qm9_records)
        self.db.log_ingestion('qm9_properties', inserted, 'SUCCESS')
        self.total_records += inserted
    
    async def _ingest_uniprot(self):
        uniprot_records = await self.target_fetcher.fetch_uniprot()
        inserted = self.db.batch_insert('uniprot_sequences', uniprot_records)
        self.db.log_ingestion('uniprot_sequences', inserted, 'SUCCESS')
        self.total_records += inserted
    
    async def _ingest_pdb(self):
        pdb_records = await self.target_fetcher.fetch_pdb()
        inserted = self.db.batch_insert('pdb_structures', pdb_records)
        self.db.log_ingestion('pdb_structures', inserted, 'SUCCESS')
        self.total_records += inserted
    
    async def _ingest_geo(self):
        geo_records = await self.target_fetcher.fetch_geo()
        inserted = self.db.batch_insert('geo_expression', geo_records)
        self.db.log_ingestion('geo_expression', inserted, 'SUCCESS')
        self.total_records += inserted
    
    async def _ingest_string(self):
        string_records = await self.target_fetcher.fetch_string()
        inserted = self.db.batch_insert('string_interactions', string_records)
        self.db.log_ingestion('string_interactions', inserted, 'SUCCESS')
        self.total_records += inserted
    
    async def _ingest_clinical_trials(self):
        ct_records = await self.trial_fetcher.fetch_clinical_trials()
        inserted = self.db.batch_insert('clinical_trials', ct_records)
        self.db.log_ingestion('clinical_trials', inserted, 'SUCCESS')
        self.total_records += inserted
    
    async def _ingest_mimic(self):
        mimic_records = await self.trial_fetcher.fetch_mimic()
        inserted = self.db.batch_insert('mimic_patients', mimic_records)
        self.db.log_ingestion('mimic_patients', inserted, 'SUCCESS')
        self.total_records += inserted
    
    async def _ingest_aact(self):
        aact_records = await self.trial_fetcher.fetch_aact()
        inserted = self.db.batch_insert('aact_trials', aact_records)
        self.db.log_ingestion('aact_trials', inserted, 'SUCCESS')
        self.total_records += inserted
    
    async def _ingest_drugbank(self):
        drugbank_records = await self.formulation_fetcher.fetch_drugbank()
        inserted = self.db.batch_insert('drugbank_formulations', drugbank_records)
        self.db.log_ingestion('drugbank_formulations', inserted, 'SUCCESS')
        self.total_records += inserted
    
    async def _ingest_gras(self):
        gras_records = await self.formulation_fetcher.fetch_gras_excipients()
        inserted = self.db.batch_insert('gras_excipients', gras_records)
        self.db.log_ingestion('gras_excipients', inserted, 'SUCCESS')
        self.total_records += inserted
    
    async def _ingest_esol(self):
        esol_records = await self.formulation_fetcher.fetch_esol_solubility()
        inserted = self.db.batch_insert('esol_solubility', esol_records)
        self.db.log_ingestion('esol_solubility', inserted, 'SUCCESS')
        self.total_records += inserted
    
    async def _ingest_tox21(self):
        tox21_records = await self.formulation_fetcher.fetch_tox21()
        inserted = self.db.batch_insert('tox21_toxicity', tox21_records)
        self.db.log_ingestion('tox21_toxicity', inserted, 'SUCCESS')
        self.total_records += inserted
    
    def _print_summary(self):
        """Print ingestion summary"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("📈 FINAL INGESTION SUMMARY")
        logger.info("=" * 80)
        
        stats = self.db.get_stats()
        total = 0
        
        for table, count in sorted(stats.items()):
            total += count
            status = "✅" if count > 0 else "⚠️"
            logger.info(f"{status} {table}: {count} records")
        
        logger.info("")
        logger.info(f"🎉 TOTAL RECORDS INGESTED: {total}")
        logger.info(f"⏱️  Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)

async def main():
    engine = ManualDataIngestionEngine()
    await engine.ingest_all()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Ingestion cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        sys.exit(1)