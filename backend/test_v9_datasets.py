import asyncio
import httpx
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000/api"

async def test_datasets():
    """Test all dataset endpoints"""
    
    async with httpx.AsyncClient() as client:
        
        # 1. Get available datasets
        logger.info("\n" + "="*60)
        logger.info("TEST 1: Get Available Datasets")
        logger.info("="*60)
        response = await client.get(f"{BASE_URL}/datasets/available")
        print(json.dumps(response.json(), indent=2))
        
        # 2. Get dataset statistics
        logger.info("\n" + "="*60)
        logger.info("TEST 2: Get Dataset Statistics")
        logger.info("="*60)
        response = await client.get(f"{BASE_URL}/datasets/stats")
        print(json.dumps(response.json(), indent=2))
        
        # 3. Get compound profile
        logger.info("\n" + "="*60)
        logger.info("TEST 3: Get Compound Profile (Aspirin)")
        logger.info("="*60)
        smiles = "CC(=O)Oc1ccccc1C(=O)O"
        response = await client.get(
            f"{BASE_URL}/datasets/compound-profile",
            params={"smiles": smiles}
        )
        print(json.dumps(response.json(), indent=2))
        
        # 4. Get solubility prediction
        logger.info("\n" + "="*60)
        logger.info("TEST 4: Get Solubility Prediction")
        logger.info("="*60)
        response = await client.get(
            f"{BASE_URL}/datasets/solubility",
            params={"smiles": smiles}
        )
        print(json.dumps(response.json(), indent=2))
        
        # 5. Get toxicity profile
        logger.info("\n" + "="*60)
        logger.info("TEST 5: Get Toxicity Profile")
        logger.info("="*60)
        response = await client.get(
            f"{BASE_URL}/datasets/toxicity",
            params={"smiles": smiles}
        )
        print(json.dumps(response.json(), indent=2))
        
        # 6. Validate formulation
        logger.info("\n" + "="*60)
        logger.info("TEST 6: Validate Formulation")
        logger.info("="*60)
        response = await client.post(
            f"{BASE_URL}/datasets/validate-formulation",
            params={
                "excipients": [
                    "Microcrystalline Cellulose",
                    "Lactose Monohydrate",
                    "Magnesium Stearate"
                ]
            }
        )
        print(json.dumps(response.json(), indent=2))
        
        # 7. Ingest ESOL dataset (dry run)
        logger.info("\n" + "="*60)
        logger.info("TEST 7: Ingest ESOL Dataset (Dry Run)")
        logger.info("="*60)
        response = await client.post(
            f"{BASE_URL}/datasets/ingest/esol_solubility",
            params={"dry_run": True}
        )
        print(json.dumps(response.json(), indent=2))
        
        # 8. Ingest GRAS dataset (dry run)
        logger.info("\n" + "="*60)
        logger.info("TEST 8: Ingest GRAS Dataset (Dry Run)")
        logger.info("="*60)
        response = await client.post(
            f"{BASE_URL}/datasets/ingest/gras_excipients",
            params={"dry_run": True}
        )
        print(json.dumps(response.json(), indent=2))
        
        logger.info("\n✅ All dataset tests completed!")

if __name__ == "__main__":
    asyncio.run(test_datasets())