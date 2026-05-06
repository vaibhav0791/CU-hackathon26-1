import asyncio
import logging
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
    
    async def ingest_all(self):
        """Ingest all datasets"""
        logger.info("=" * 80)
        logger.info("🚀 MANUAL DATA INGESTION ENGINE - ALL 19 DATASETS")
        logger.info("=" * 80)
        logger.info("")
        
        total_records = 0
        
        try:
            # PHASE 1: Drug Discovery
            logger.info("=" * 80)
            logger.info("📊 PHASE 1: DRUG DISCOVERY DATASETS")
            logger.info("=" * 80)
            logger.info("")
            
            # ChEMBL
            chembl_records = await self.drug_fetcher.fetch_chembl()
            inserted = self.db.batch_insert('chembl_bioactivity', chembl_records)
            self.db.log_ingestion('chembl_bioactivity', inserted, 'SUCCESS')
            total_records += inserted
            logger.info(f"✅ ChEMBL: {inserted} records\n")
            
            # PubChem
            pubchem_records = await self.drug_fetcher.fetch_pubchem()
            inserted = self.db.batch_insert('pubchem_properties', pubchem_records)
            self.db.log_ingestion('pubchem_properties', inserted, 'SUCCESS')
            total_records += inserted
            logger.info(f"✅ PubChem: {inserted} records\n")
            
            # ZINC15
            zinc_records = await self.drug_fetcher.fetch_zinc15()
            inserted = self.db.batch_insert('zinc15_compounds', zinc_records)
            self.db.log_ingestion('zinc15_compounds', inserted, 'SUCCESS')
            total_records += inserted
            logger.info(f"✅ ZINC15: {inserted} records\n")
            
            # QM9
            qm9_records = await self.drug_fetcher.fetch_qm9()
            inserted = self.db.batch_insert('qm9_properties', qm9_records)
            self.db.log_ingestion('qm9_properties', inserted, 'SUCCESS')
            total_records += inserted
            logger.info(f"✅ QM9: {inserted} records\n")
            
            # PHASE 2: Target Discovery
            logger.info("=" * 80)
            logger.info("🔬 PHASE 2: TARGET DISCOVERY DATASETS")
            logger.info("=" * 80)
            logger.info("")
            
            # UniProt
            uniprot_records = await self.target_fetcher.fetch_uniprot()
            inserted = self.db.batch_insert('uniprot_sequences', uniprot_records)
            self.db.log_ingestion('uniprot_sequences', inserted, 'SUCCESS')
            total_records += inserted
            logger.info(f"✅ UniProt: {inserted} records\n")
            
            # PDB
            pdb_records = await self.target_fetcher.fetch_pdb()
            inserted = self.db.batch_insert('pdb_structures', pdb_records)
            self.db.log_ingestion('pdb_structures', inserted, 'SUCCESS')
            total_records += inserted
            logger.info(f"✅ PDB: {inserted} records\n")
            
            # STRING
            string_records = await self.target_fetcher.fetch_string()
            inserted = self.db.batch_insert('string_interactions', string_records)
            self.db.log_ingestion('string_interactions', inserted, 'SUCCESS')
            total_records += inserted
            logger.info(f"✅ STRING: {inserted} records\n")
            
            # PHASE 3: Clinical Trials
            logger.info("=" * 80)
            logger.info("🏥 PHASE 3: CLINICAL TRIAL DATASETS")
            logger.info("=" * 80)
            logger.info("")
            
            # ClinicalTrials.gov
            ct_records = await self.trial_fetcher.fetch_clinical_trials()
            inserted = self.db.batch_insert('clinical_trials', ct_records)
            self.db.log_ingestion('clinical_trials', inserted, 'SUCCESS')
            total_records += inserted
            logger.info(f"✅ ClinicalTrials.gov: {inserted} records\n")
            
            # MIMIC
            mimic_records = await self.trial_fetcher.fetch_mimic()
            inserted = self.db.batch_insert('mimic_patients', mimic_records)
            self.db.log_ingestion('mimic_patients', inserted, 'SUCCESS')
            total_records += inserted
            logger.info(f"✅ MIMIC-III: {inserted} records\n")
            
            # PHASE 4: Formulation
            logger.info("=" * 80)
            logger.info("⚗️  PHASE 4: FORMULATION DATASETS")
            logger.info("=" * 80)
            logger.info("")
            
            # DrugBank
            drugbank_records = await self.formulation_fetcher.fetch_drugbank()
            inserted = self.db.batch_insert('drugbank_formulations', drugbank_records)
            self.db.log_ingestion('drugbank_formulations', inserted, 'SUCCESS')
            total_records += inserted
            logger.info(f"✅ DrugBank: {inserted} records\n")
            
            # GRAS
            gras_records = await self.formulation_fetcher.fetch_gras_excipients()
            inserted = self.db.batch_insert('gras_excipients', gras_records)
            self.db.log_ingestion('gras_excipients', inserted, 'SUCCESS')
            total_records += inserted
            logger.info(f"✅ GRAS: {inserted} records\n")
            
            # ESOL
            esol_records = await self.formulation_fetcher.fetch_esol_solubility()
            inserted = self.db.batch_insert('esol_solubility', esol_records)
            self.db.log_ingestion('esol_solubility', inserted, 'SUCCESS')
            total_records += inserted
            logger.info(f"✅ ESOL: {inserted} records\n")
            
            # Tox21
            tox21_records = await self.formulation_fetcher.fetch_tox21()
            inserted = self.db.batch_insert('tox21_toxicity', tox21_records)
            self.db.log_ingestion('tox21_toxicity', inserted, 'SUCCESS')
            total_records += inserted
            logger.info(f"✅ Tox21: {inserted} records\n")
            
            # Summary
            logger.info("=" * 80)
            logger.info("📈 INGESTION SUMMARY")
            logger.info("=" * 80)
            
            stats = self.db.get_stats()
            for table, count in stats.items():
                logger.info(f"  {table}: {count} records")
            
            logger.info("")
            logger.info(f"🎉 TOTAL RECORDS INGESTED: {total_records}")
            logger.info(f"⏱️  Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ Error during ingestion: {e}")
        finally:
            await self.drug_fetcher.close()
            await self.target_fetcher.close()
            await self.trial_fetcher.close()
            await self.formulation_fetcher.close()

async def main():
    engine = ManualDataIngestionEngine()
    await engine.ingest_all()

if __name__ == "__main__":
    asyncio.run(main())