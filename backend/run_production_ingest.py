# backend/run_production_ingest.py
"""
Pharma AI Production Runner
Demonstrates live data fetching connected to our structure-based deduplication layer.
"""

import asyncio
import logging
from pharma_ai_discovery_pipeline import PharmaAIDiscoveryPipeline
from pharma_ai_dedup_engine import PharmaAIDedupEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("pharma_production")

async def main():
    logger.info("🚀 --- STARTING PRISTINE DEDUPLICATED INGESTION WORKFLOW ---")
    
    pipeline = PharmaAIDiscoveryPipeline()
    
    # 1. Gather live records from ChEMBL
    chembl_batch = await pipeline.fetch_production_chembl(limit=5)
    
    # 2. Inject an intentional duplicate to test your defenses!
    if chembl_batch:
        logger.info("\n🧪 Simulating data collision risk (Injecting an identical chemical structure from a different source)...")
        simulated_pubchem_entry = {
            "source": "PubChem",
            "raw_id": "PUBCHEM_999999",
            "smiles": chembl_batch[0]["smiles"],  # Exact same structure as the first ChEMBL entry!
            "compound_name": "Aspirin_Duplicate_Test",
            "bioactivity_value": None,
            "bioactivity_type": None
        }
        chembl_batch.append(simulated_pubchem_entry)

    # 3. Pass the mixed batch into the Deduplication Engine
    logger.info("\n🛡️ Passing collected batch into PharmaAIDedupEngine...")
    pristine_training_set = PharmaAIDedupEngine.process_incoming_batch(chembl_batch)
    
    # 4. Display final dataset properties ready for AI ingestion
    print("\n" + "="*80)
    print("🎯 PRISTINE AI-READY CHEMICAL DATASET GENERATED")
    print("="*80)
    for index, record in enumerate(pristine_training_set):
        print(f" [{index+1}] ID: {record['pharma_ai_uid']} | Source: {record['source']} | Raw ID: {record['raw_id']} | Name: {record['compound_name']}")
    print("="*80)
    logger.info(f"🎉 Pipeline Complete! Clean records ready for the Tech Team: {len(pristine_training_set)}")

if __name__ == "__main__":
    asyncio.run(main())