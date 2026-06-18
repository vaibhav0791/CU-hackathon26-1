# pharma_ai_target_discovery_v2/target_discovery_fetcher_v2.py
import logging
import httpx
from typing import List, Dict, Any

logger = logging.getLogger("target_fetcher_v2")

class TargetDiscoveryFetcherV2:
    def __init__(self):
        self.timeout = 25.0

    async def fetch_full_uniprot_chain(self, uniprot_id: str) -> Dict[str, Any]:
        url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id.strip().upper()}.json"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    payload = response.json()
                    full_sequence = payload.get("sequence", {}).get("value", "")
                    return {
                        "uniprot_id": uniprot_id,
                        "gene_name": payload.get("genes", [{}])[0].get("geneName", {}).get("value", "Unknown"),
                        "sequence": full_sequence
                    }
            except Exception as e:
                logger.error(f"❌ Target sequence request failed for UniProt ID {uniprot_id}: {e}")
        return {}

    async def fetch_json_geo_expression(self, query_gene: str) -> List[Dict[str, Any]]:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        query_params = {
            'db': 'gds',
            'term': query_gene,
            'rettype': 'json',
            'retmode': 'json'
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=query_params)
                if response.status_code == 200:
                    ids = response.json().get("esearchresult", {}).get("idlist", [])
                    return [{"geo_dataset_gse": g_id, "gene_symbol": query_gene} for g_id in ids]
            except Exception as e:
                logger.error(f"❌ NCBI gene expression retrieval errored for {query_gene}: {e}")
        return []

    async def fetch_string_interactions_batched(self, target_genes: List[str]) -> List[Dict[str, Any]]:
        url = "https://string-db.org/api/json/network"
        payload = {
            "identifiers": "\n".join([gene.upper().strip() for gene in target_genes]),
            "species": 9606
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, data=payload)
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                logger.error(f"❌ Batched network retrieval blocked on STRING gateway: {e}")
        return []