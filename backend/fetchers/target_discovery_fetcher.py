# backend/fetchers/target_discovery_fetcher.py
"""Fetch target discovery data from multiple bioinformatics databases"""
import logging
import asyncio
import httpx
from typing import List, Dict, Any
from fetchers.base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class TargetDiscoveryFetcher(BaseFetcher):
    """Fetch target discovery data from UniProt, PDB, GEO, and STRING DB"""
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """
        Main fetch method - combines all target discovery data sources
        Returns list of target records ready for ingestion
        """
        logger.info("🔍 Fetching target discovery data from all sources...")
        
        # Try to load from cache first
        cached_data = self._load_from_cache("target_discovery")
        if cached_data:
            logger.info(f"✅ Loaded {len(cached_data)} target records from cache")
            return self._add_metadata(cached_data)
        
        try:
            # Fetch from all sources in parallel
            logger.info("📡 Fetching from multiple sources (UniProt, PDB, GEO, STRING)...")
            
            uniprot_data = await self.fetch_uniprot()
            pdb_data = await self.fetch_pdb()
            geo_data = await self.fetch_geo()
            string_data = await self.fetch_string()
            
            # Combine all data
            all_target_data = uniprot_data + pdb_data + geo_data + string_data
            
            # Remove duplicates by unique identifier
            unique_targets = {}
            for target in all_target_data:
                unique_id = (target.get('uniprot_id') or target.get('pdb_id') or 
                           target.get('geo_id') or target.get('interaction_id'))
                if unique_id and unique_id not in unique_targets:
                    unique_targets[unique_id] = target
            
            final_data = list(unique_targets.values())
            
            if final_data:
                self._save_to_cache("target_discovery", final_data)
                logger.info(f"✅ Fetched {len(final_data)} unique target records (after dedup)")
            
            return self._add_metadata(final_data)
        
        except Exception as e:
            logger.error(f"❌ Error in target discovery fetch: {e}")
            return []
    
    async def fetch_uniprot(self) -> List[Dict[str, Any]]:
        """Fetch from UniProt Protein Sequences"""
        logger.info("  📊 UniProt: Fetching protein sequences...")
        
        try:
            url = "https://rest.uniprot.org/uniprotkb/search"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    'query': 'organism_id:9606 AND reviewed:true AND (TP53 OR BRCA1 OR EGFR OR KRAS)',
                    'format': 'json',
                    'size': 50,
                    'fields': 'accession,id,protein_name,gene_names,organism_name,sequence'
                }
                
                response = await client.get(url, params=params, timeout=15.0)
                
                if response.status_code == 200:
                    data = response.json()
                    records = []
                    
                    for entry in data.get('results', [])[:50]:
                        try:
                            sequence = entry.get('sequence', {})
                            genes = entry.get('genes', [])
                            
                            record = {
                                'uniprot_id': entry.get('primaryAccession', ''),
                                'protein_name': entry.get('uniProtkbId', ''),
                                'gene_name': genes[0].get('geneName', {}).get('value', '') if genes else '',
                                'organism': entry.get('organism', {}).get('scientificName', 'Unknown'),
                                'sequence': sequence.get('value', '')[:500],
                                'sequence_length': sequence.get('length', 0),
                            }
                            
                            if record['uniprot_id']:
                                records.append(record)
                        except Exception as e:
                            logger.warning(f"    ⚠️ Skipping UniProt entry: {e}")
                    
                    logger.info(f"  ✅ UniProt: Got {len(records)} records")
                    return records
                else:
                    logger.warning(f"  ⚠️ UniProt API returned {response.status_code}")
                    return await self._load_sample_uniprot_data()
        
        except Exception as e:
            logger.error(f"  ❌ UniProt fetch error: {e}")
            return await self._load_sample_uniprot_data()
    
    async def fetch_pdb(self) -> List[Dict[str, Any]]:
        """Fetch from RCSB PDB Structures"""
        logger.info("  📊 PDB: Fetching protein structures...")
        
        try:
            url = "https://search.rcsb.org/rcsbsearch/v2/query"
            
            query_params = {
                "query": {
                    "type": "terminal",
                    "service": "structure",
                    "parameters": {
                        "attribute_comparisons": [
                            {
                                "comparator": "<",
                                "attribute": "rcsb_entry_info.resolution_combined",
                                "value": 3.0,
                                "operator": "and"
                            }
                        ]
                    }
                },
                "request_options": {
                    "paginate": {
                        "start": 0,
                        "rows": 50
                    }
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=query_params, timeout=15.0)
                
                if response.status_code == 200:
                    data = response.json()
                    records = []
                    
                    for result in data.get('result_set', [])[:50]:
                        try:
                            pdb_id = result.get('identifier', '')
                            
                            details_url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
                            details_response = await client.get(details_url, timeout=10.0)
                            
                            if details_response.status_code == 200:
                                details = details_response.json()
                                
                                record = {
                                    'pdb_id': pdb_id,
                                    'title': details.get('struct', {}).get('title', ''),
                                    'resolution': details.get('rcsb_entry_info', {}).get('resolution_combined', [None])[0],
                                    'experimental_method': details.get('exptl', [{}])[0].get('method', '') if details.get('exptl') else 'Unknown',
                                    'interaction_id': f'PDB_{pdb_id}'
                                }
                                records.append(record)
                            
                            await asyncio.sleep(0.1)
                        except Exception as e:
                            logger.warning(f"    ⚠️ Skipping PDB {pdb_id}: {e}")
                    
                    logger.info(f"  ✅ PDB: Got {len(records)} records")
                    return records
                else:
                    logger.warning(f"  ⚠️ PDB API returned {response.status_code}")
                    return await self._load_sample_pdb_data()
        
        except Exception as e:
            logger.error(f"  ❌ PDB fetch error: {e}")
            return await self._load_sample_pdb_data()
    
    async def fetch_geo(self) -> List[Dict[str, Any]]:
        """Fetch from GEO Gene Expression Database"""
        logger.info("  📊 GEO: Fetching gene expression data...")
        
        try:
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    'db': 'gds',
                    'term': 'cancer expression profiling',
                    'rettype': 'xml',  # ✅ FIXED: Force XML response format to match ElementTree expectations
                    'retmax': 50,
                }
                
                response = await client.get(url, params=params, timeout=15.0)
                
                if response.status_code == 200:
                    records = await self._parse_geo_results(response.text)
                    logger.info(f"  ✅ GEO: Got {len(records)} records")
                    return records
                else:
                    logger.warning(f"  ⚠️ GEO API returned {response.status_code}")
                    return await self._load_sample_geo_data()
        
        except Exception as e:
            logger.error(f"  ❌ GEO fetch error: {e}")
            return await self._load_sample_geo_data()
    
    async def fetch_string(self) -> List[Dict[str, Any]]:
        """Fetch from STRING DB Protein Interactions"""
        logger.info("  📊 STRING DB: Fetching protein interactions...")
        
        try:
            url = "https://string-db.org/api/json/network"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                proteins = ['TP53', 'BRCA1', 'EGFR', 'KRAS', 'PIK3CA']
                records = []
                
                for protein in proteins:
                    try:
                        params = {
                            'identifiers': protein,
                            'species': 9606,
                            'required_score': 700,
                            'limit': 20
                        }
                        
                        response = await client.get(url, params=params, timeout=10.0)
                        
                        if response.status_code == 200:
                            interactions = response.json()
                            
                            for idx, interaction in enumerate(interactions):
                                try:
                                    record = {
                                        'interaction_id': f"STRING_{protein}_{idx}",
                                        'protein_a': protein,
                                        'protein_b': interaction.get('preferredName_b', '') or interaction.get('stringId_b', ''),
                                        'combined_score': float(interaction.get('score', 0)) / 1000.0
                                    }
                                    records.append(record)
                                except Exception as e:
                                    logger.warning(f"    ⚠️ Skipping interaction: {e}")
                        
                        await asyncio.sleep(0.2)
                    except Exception as e:
                        logger.warning(f"    ⚠️ Could not fetch {protein}: {e}")
                
                return records if records else await self._load_sample_string_data()
        
        except Exception as e:
            logger.error(f"  ❌ STRING DB fetch error: {e}")
            return await self._load_sample_string_data()
            
    async def _parse_geo_results(self, response_text: str) -> List[Dict[str, Any]]:
        records = []
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response_text)
            for idx, id_elem in enumerate(root.findall('.//Id')[:50]):
                records.append({
                    'geo_id': f'GSE{id_elem.text}',
                    'interaction_id': f'GEO_{idx}',
                    'title': f'Gene Expression Study {id_elem.text}',
                    'organism': 'Homo sapiens',
                })
        except Exception as e:
            logger.warning(f"  ⚠️ Could not parse GEO results: {e}")
        return records

    async def _load_sample_uniprot_data(self):
        return [{'uniprot_id': 'P00533', 'protein_name': 'EGFR', 'gene_name': 'EGFR', 'organism': 'Homo sapiens', 'sequence': 'MRPSGTAGAALLALLCGGGRKCCEVGPGK', 'sequence_length': 1210}]

    async def _load_sample_pdb_data(self):
        return [{'pdb_id': '1JNX', 'interaction_id': 'PDB_1JNX', 'title': 'EGFR structure', 'resolution': 2.5, 'experimental_method': 'X-RAY'}]

    async def _load_sample_geo_data(self):
        return [{'geo_id': 'GSE15870', 'interaction_id': 'GEO_2', 'title': 'Expression profiling', 'organism': 'Homo sapiens'}]

    async def _load_sample_string_data(self):
        return [{'interaction_id': 'STRING_2', 'protein_a': 'EGFR', 'protein_b': 'KRAS', 'combined_score': 0.92}]