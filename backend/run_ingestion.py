# backend/run_ingestion.py
import asyncio
import logging
import sys
from data_ingestion_engine import DataIngestionEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Run the complete data ingestion pipeline"""
    
    logger.info("=" * 80)
    logger.info("🚀 PHARMA-AI DATA INGESTION ENGINE")
    logger.info("Ingesting data from 19 datasets...")
    logger.info("=" * 80)
    
    # Create engine
    engine = DataIngestionEngine(db_path="pharma.db", cache_dir="ingestion_cache")
    
    # Run ingestion
    try:
        await engine.ingest_all_datasets()
        logger.info("\n✅ INGESTION COMPLETE!")
        logger.info("All datasets have been ingested successfully.")
    
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Ingestion cancelled by user")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"\n❌ Ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())