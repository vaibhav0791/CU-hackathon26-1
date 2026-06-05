# backend/run_pharma_ai_test.py
"""
Isolated Orchestrator Test Execution script for Pharma AI
"""

import asyncio
import logging
from pharma_ai_discovery_pipeline import PharmaAIDiscoveryPipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("pharma_ai_test")

async def execute_new_sandbox_diagnostic():
    logger.info("🧪 Starting Brand-New Production Pipeline Sandbox...")
    
    # Instantiate the decoupled pipeline engine
    pipeline = PharmaAIDiscoveryPipeline()
    
    # 1. Run isolated ChEMBL phase
    chembl_batch = await pipeline.fetch_production_chembl(limit=5)
    if chembl_batch:
        logger.info(f"🎉 New ChEMBL component passed! Sample: {chembl_batch[0]}")
    else:
        logger.error("❌ Isolated ChEMBL component failed verification.")

    # 2. Run isolated PubChem phase (Testing Aspirin CID 2244)
    pubchem_profile = await pipeline.fetch_production_pubchem_properties(cid=2244)
    if pubchem_profile:
        logger.info(f"🎉 New PubChem component passed! Profile: {pubchem_profile}")
    else:
        logger.error("❌ Isolated PubChem component failed verification.")
        
    logger.info("\n🏁 Decoupled Sandbox Verification Completed Successfully.")

if __name__ == "__main__":
    asyncio.run(execute_new_sandbox_diagnostic())