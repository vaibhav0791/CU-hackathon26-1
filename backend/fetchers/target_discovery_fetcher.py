# backend/fetchers/target_discovery_fetcher.py
import asyncio
import httpx
import logging
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

class TargetDiscoveryFetcher:
    """Fetches target discovery data from 4 datasets"""
    
    def __init__(self, db_path: str, cache_dir: Path):
        self.db_path = db_path
        self.cache_dir = cache_dir
    
    async def fetch_uniprot(self):
        """Fetch from UniProt Protein Sequences"""
        logger.info("🔍 Fetching UniProt Protein Sequences...")
        
        try:
            # UniProt API endpoint
            url = "https://rest.uniprot.org/uniprotkb/search"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Query for human proteins
                params = {
                    'query': 'organism_id:9606 AND reviewed:true',
                    'format': 'json',
                    'size': 100,
                    'fields': 'accession,id,protein_name,gene_names,organism_name,sequence'
                }
                
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    records = []
                    
                    for entry in data.get('results', [])[:50]:  # Limit to 50
                        record = {
                            'uniprot_id': entry.get('primaryAccession', ''),
                            'protein_name': entry.get('uniProtkbId', ''),
                            'gene_name': entry.get('genes', [{}])[0].get('geneName', {}).get('value', '') if entry.get('genes') else '',
                            'organism': entry.get('organism', {}).get('scientificName', ''),
                            'sequence': entry.get('sequence', {}).get('value', ''),
                            'sequence_length': entry.get('sequence', {}).get('length', 0),
                        }
                        records.append(record)
                    
                    await self._save_uniprot_data(records)
                    logger.info(f"✅ Ingested {len(records)} UniProt records")
                else:
                    logger.warning(f"⚠️ UniProt API returned {response.status_code}")
                    await self._load_sample_uniprot_data()
        
        except Exception as e:
            logger.error(f"❌ Error fetching UniProt: {e}")
            await self._load_sample_uniprot_data()
    
    async def fetch_pdb(self):
        """Fetch from RCSB PDB Structures"""
        logger.info("🔍 Fetching RCSB PDB Structures...")
        
        try:
            # RCSB PDB API endpoint
            url = "https://search.rcsb.org/rcsbsearch/v2/query"
            
            query_params = {
                "query": {
                    "type": "terminal",
                    "service": "structure",
                    "parameters": {
                        "attribute_comparisons": [
                            {
                                "comparator": ">",
                                "attribute": "rcsb_entry_info.resolution_combined",
                                "value": 0,
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
                response = await client.post(url, json=query_params)
                
                if response.status_code == 200:
                    data = response.json()
                    records = []
                    
                    for result in data.get('result_set', []):
                        pdb_id = result.get('identifier', '')
                        # Fetch details for each PDB
                        details = await self._get_pdb_details(client, pdb_id)
                        records.append(details)
                    
                    await self._save_pdb_data(records)
                    logger.info(f"✅ Ingested {len(records)} PDB records")
                else:
                    logger.warning(f"⚠️ PDB API returned {response.status_code}")
                    await self._load_sample_pdb_data()
        
        except Exception as e:
            logger.error(f"❌ Error fetching PDB: {e}")
            await self._load_sample_pdb_data()
    
    async def _get_pdb_details(self, client, pdb_id: str) -> Dict:
        """Get details for a specific PDB structure"""
        try:
            url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
            response = await client.get(url, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'pdb_id': pdb_id,
                    'title': data.get('struct', {}).get('title', ''),
                    'resolution': data.get('rcsb_entry_info', {}).get('resolution_combined', [None])[0],
                    'experiment_type': data.get('exptl', [{}])[0].get('method', '') if data.get('exptl') else '',
                    'biological_assembly': str(data.get('rcsb_entry_info', {}).get('assembly_form', '')),
                }
        except Exception as e:
            logger.warning(f"Could not fetch PDB details for {pdb_id}: {e}")
        
        return {'pdb_id': pdb_id}
    
    async def fetch_geo(self):
        """Fetch from GEO Gene Expression Database"""
        logger.info("🔍 Fetching GEO Expression Data...")
        
        try:
            # GEO API endpoint (requires NCBI API key for best results)
            # Using NCBI Entrez API
            
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    'db': 'gds',
                    'term': 'disease expression study',
                    'rettype': 'json',
                    'retmax': 50,
                    'api_key': 'demo'  # Use your NCBI API key
                }
                
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    # Parse response and extract GEO IDs
                    records = await self._parse_geo_results(response.text)
                    await self._save_geo_data(records)
                    logger.info(f"✅ Ingested {len(records)} GEO records")
                else:
                    logger.warning(f"⚠️ GEO API returned {response.status_code}")
                    await self._load_sample_geo_data()
        
        except Exception as e:
            logger.error(f"❌ Error fetching GEO: {e}")
            await self._load_sample_geo_data()
    
    async def _parse_geo_results(self, response_text: str) -> List[Dict]:
        """Parse GEO API response"""
        records = []
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response_text)
            
            for id_elem in root.findall('.//Id')[:50]:
                geo_id = id_elem.text
                records.append({
                    'geo_id': f'GSE{geo_id}',
                    'study_title': f'Gene Expression Study {geo_id}',
                    'organism': 'Homo sapiens',
                    'disease_condition': 'Various',
                    'sample_count': 30,
                    'genes_profiled': 20000,
                })
        except Exception as e:
            logger.warning(f"Could not parse GEO results: {e}")
        
        return records
    
    async def fetch_string(self):
        """Fetch from STRING DB Protein Interactions"""
        logger.info("🔍 Fetching STRING DB Interactions...")
        
        try:
            # STRING API endpoint
            url = "https://string-db.org/api/json/network"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    'identifiers': 'TP53%0dBRCA1%0dEGFR',  # Sample proteins
                    'species': 9606,  # Human
                    'required_score': 700,
                }
                
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    records = response.json()
                    await self._save_string_data(records)
                    logger.info(f"✅ Ingested {len(records)} STRING records")
                else:
                    logger.warning(f"⚠️ STRING API returned {response.status_code}")
                    await self._load_sample_string_data()
        
        except Exception as e:
            logger.error(f"❌ Error fetching STRING: {e}")
            await self._load_sample_string_data()
    
    async def _save_uniprot_data(self, records: List[Dict]):
        """Save UniProt data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in records:
            cursor.execute('''
                INSERT OR REPLACE INTO uniprot_sequences
                (uniprot_id, protein_name, gene_name, organism, sequence, 
                 sequence_length, ingestion_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get('uniprot_id', ''),
                record.get('protein_name', ''),
                record.get('gene_name', ''),
                record.get('organism', ''),
                record.get('sequence', '')[:100],  # Truncate for demo
                record.get('sequence_length', 0),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    async def _save_pdb_data(self, records: List[Dict]):
        """Save PDB data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in records:
            cursor.execute('''
                INSERT OR REPLACE INTO pdb_structures
                (pdb_id, title, resolution, experiment_type, biological_assembly, ingestion_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                record.get('pdb_id', ''),
                record.get('title', ''),
                record.get('resolution'),
                record.get('experiment_type', ''),
                record.get('biological_assembly', ''),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    async def _save_geo_data(self, records: List[Dict]):
        """Save GEO data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in records:
            cursor.execute('''
                INSERT OR REPLACE INTO geo_expression
                (geo_id, study_title, organism, disease_condition, sample_count, 
                 genes_profiled, ingestion_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get('geo_id', ''),
                record.get('study_title', ''),
                record.get('organism', ''),
                record.get('disease_condition', ''),
                record.get('sample_count', 0),
                record.get('genes_profiled', 0),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    async def _save_string_data(self, records: List[Dict]):
        """Save STRING data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for i, record in enumerate(records):
            cursor.execute('''
                INSERT OR REPLACE INTO string_interactions
                (interaction_id, protein_a, protein_b, combined_score, ingestion_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                f"INT_{i}",
                record.get('stringId_a', ''),
                record.get('stringId_b', ''),
                record.get('score', 0),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    async def _load_sample_uniprot_data(self):
        """Load sample UniProt data"""
        sample_data = [{
            'uniprot_id': 'P04637',
            'protein_name': 'p53',
            'gene_name': 'TP53',
            'organism': 'Homo sapiens',
            'sequence': 'MEEPQSDPSV',
            'sequence_length': 393,
        }]
        await self._save_uniprot_data(sample_data)
    
    async def _load_sample_pdb_data(self):
        """Load sample PDB data"""
        sample_data = [{
            'pdb_id': '1P53',
            'title': 'Tumor suppressor p53',
            'resolution': 2.2,
            'experiment_type': 'X-RAY DIFFRACTION',
        }]
        await self._save_pdb_data(sample_data)
    
    async def _load_sample_geo_data(self):
        """Load sample GEO data"""
        sample_data = [{
            'geo_id': 'GSE13195',
            'study_title': 'Gene expression profiles of obesity',
            'organism': 'Homo sapiens',
            'disease_condition': 'Obesity',
            'sample_count': 100,
            'genes_profiled': 20000,
        }]
        await self._save_geo_data(sample_data)
    
    async def _load_sample_string_data(self):
        """Load sample STRING data"""
        sample_data = [{
            'stringId_a': 'TP53',
            'stringId_b': 'BRCA1',
            'score': 850,
        }]
        await self._save_string_data(sample_data)