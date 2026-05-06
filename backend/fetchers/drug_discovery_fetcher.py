# backend/fetchers/drug_discovery_fetcher.py
import asyncio
import httpx
import logging
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DrugDiscoveryFetcher:
    """Fetches drug discovery data from 4 datasets"""
    
    def __init__(self, db_path: str, cache_dir: Path):
        self.db_path = db_path
        self.cache_dir = cache_dir
        self.session = None
    
    async def fetch_chembl(self):
        """Fetch from ChEMBL Bioactivity Database"""
        logger.info("🔍 Fetching ChEMBL Bioactivity data...")
        
        try:
            # ChEMBL API endpoint for bioactivity data
            url = "https://www.ebi.ac.uk/chembl/api/data/activity.json"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Fetch first 100 records as sample
                response = await client.get(url, params={"limit": 100})
                
                if response.status_code == 200:
                    data = response.json()
                    records = data.get('results', [])
                    
                    await self._save_chembl_data(records)
                    logger.info(f"✅ Ingested {len(records)} ChEMBL records")
                else:
                    logger.warning(f"⚠️ ChEMBL API returned {response.status_code}")
                    await self._load_sample_chembl_data()
        
        except Exception as e:
            logger.error(f"❌ Error fetching ChEMBL: {e}")
            await self._load_sample_chembl_data()
    
    async def fetch_pubchem(self):
        """Fetch from PubChem Molecular Properties"""
        logger.info("🔍 Fetching PubChem Molecular Properties...")
        
        try:
            # Sample drug CIDs to fetch
            sample_cids = [2244, 5288826, 5360545, 2662]  # Aspirin, Ibuprofen, Naproxen, Acetaminophen
            
            compounds = []
            async with httpx.AsyncClient(timeout=30.0) as client:
                for cid in sample_cids:
                    try:
                        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/JSON"
                        response = await client.get(url)
                        
                        if response.status_code == 200:
                            data = response.json()
                            props = data['PC_Compounds'][0]
                            
                            compound = {
                                'cid': cid,
                                'compound_name': props.get('props', [{}])[0].get('urn', {}).get('label', f'CID_{cid}'),
                                'smiles': props.get('atoms', {}).get('smiles', ''),
                                'molecular_weight': props.get('props', [{}])[1].get('ival', 0) if len(props.get('props', [])) > 1 else 0,
                                'logp': props.get('props', [{}])[2].get('fval', 0) if len(props.get('props', [])) > 2 else 0,
                            }
                            compounds.append(compound)
                        
                        await asyncio.sleep(0.5)  # Rate limiting
                    
                    except Exception as e:
                        logger.warning(f"Could not fetch PubChem CID {cid}: {e}")
            
            if compounds:
                await self._save_pubchem_data(compounds)
                logger.info(f"✅ Ingested {len(compounds)} PubChem records")
            else:
                logger.warning("⚠️ No PubChem data fetched, using sample data")
                await self._load_sample_pubchem_data()
        
        except Exception as e:
            logger.error(f"❌ Error fetching PubChem: {e}")
            await self._load_sample_pubchem_data()
    
    async def fetch_zinc15(self):
        """Fetch from ZINC15 Database"""
        logger.info("🔍 Fetching ZINC15 Compounds...")
        
        try:
            # ZINC15 API endpoint
            url = "https://zinc.docking.org/api/substances/"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params={"limit": 50})
                
                if response.status_code == 200:
                    data = response.json()
                    records = data.get('results', [])
                    
                    await self._save_zinc15_data(records)
                    logger.info(f"✅ Ingested {len(records)} ZINC15 records")
                else:
                    logger.warning(f"⚠️ ZINC15 API returned {response.status_code}")
                    await self._load_sample_zinc15_data()
        
        except Exception as e:
            logger.error(f"❌ Error fetching ZINC15: {e}")
            await self._load_sample_zinc15_data()
    
    async def fetch_qm9(self):
        """Load QM9 Quantum Properties from HuggingFace"""
        logger.info("🔍 Fetching QM9 Quantum Properties...")
        
        try:
            from datasets import load_dataset
            
            # Load QM9 dataset from HuggingFace
            logger.info("Loading QM9 from HuggingFace (this may take a moment)...")
            dataset = load_dataset('qm9', split='train[:100]')  # Load first 100
            
            records = []
            for item in dataset:
                record = {
                    'molecule_id': item.get('ID', ''),
                    'smiles': item.get('SMILES', ''),
                    'homo_energy': float(item.get('homo', 0)),
                    'lumo_energy': float(item.get('lumo', 0)),
                    'gap_energy': float(item.get('gap', 0)),
                    'dipole_moment': float(item.get('mu', 0)),
                    'polarizability': float(item.get('alpha', 0)),
                }
                records.append(record)
            
            await self._save_qm9_data(records)
            logger.info(f"✅ Ingested {len(records)} QM9 records")
        
        except Exception as e:
            logger.error(f"❌ Error fetching QM9: {e}")
            await self._load_sample_qm9_data()
    
    async def _save_chembl_data(self, records: List[Dict]):
        """Save ChEMBL data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in records:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO chembl_bioactivity
                    (compound_id, compound_name, smiles, target_name, bioactivity_type, 
                     bioactivity_value, units, assay_type, ingestion_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record.get('molecule_chembl_id', ''),
                    record.get('molecule_pref_name', ''),
                    record.get('canonical_smiles', ''),
                    record.get('target_pref_name', ''),
                    record.get('type', ''),
                    record.get('standard_value'),
                    record.get('standard_units', ''),
                    record.get('assay_type', ''),
                    datetime.now().isoformat()
                ))
            except Exception as e:
                logger.warning(f"Could not insert ChEMBL record: {e}")
        
        conn.commit()
        conn.close()
    
    async def _save_pubchem_data(self, records: List[Dict]):
        """Save PubChem data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in records:
            cursor.execute('''
                INSERT OR REPLACE INTO pubchem_properties
                (cid, compound_name, smiles, molecular_weight, logp, h_bond_donors,
                 h_bond_acceptors, tpsa, rotatable_bonds, ingestion_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get('cid'),
                record.get('compound_name', ''),
                record.get('smiles', ''),
                record.get('molecular_weight', 0),
                record.get('logp', 0),
                record.get('h_bond_donors', 0),
                record.get('h_bond_acceptors', 0),
                record.get('tpsa', 0),
                record.get('rotatable_bonds', 0),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    async def _save_zinc15_data(self, records: List[Dict]):
        """Save ZINC15 data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in records:
            cursor.execute('''
                INSERT OR REPLACE INTO zinc15_compounds
                (zinc_id, compound_name, smiles, molecular_weight, price_min, 
                 price_max, suppliers, ingestion_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get('zinc_id', ''),
                record.get('substance_name', ''),
                record.get('smiles', ''),
                record.get('molecular_weight', 0),
                record.get('price_min'),
                record.get('price_max'),
                record.get('supplier_count', 0),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    async def _save_qm9_data(self, records: List[Dict]):
        """Save QM9 data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in records:
            cursor.execute('''
                INSERT OR REPLACE INTO qm9_properties
                (molecule_id, smiles, homo_energy, lumo_energy, gap_energy, 
                 dipole_moment, polarizability, ingestion_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get('molecule_id', ''),
                record.get('smiles', ''),
                record.get('homo_energy', 0),
                record.get('lumo_energy', 0),
                record.get('gap_energy', 0),
                record.get('dipole_moment', 0),
                record.get('polarizability', 0),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    async def _load_sample_chembl_data(self):
        """Load sample ChEMBL data as fallback"""
        sample_data = [
            {
                'compound_id': 'CHEMBL100001',
                'compound_name': 'Aspirin',
                'smiles': 'CC(=O)Oc1ccccc1C(=O)O',
                'target_name': 'Cyclooxygenase',
                'bioactivity_type': 'IC50',
                'bioactivity_value': 100.0,
                'units': 'nM',
                'assay_type': 'binding'
            }
        ]
        await self._save_chembl_data(sample_data)
    
    async def _load_sample_pubchem_data(self):
        """Load sample PubChem data as fallback"""
        sample_data = [
            {
                'cid': 2244,
                'compound_name': 'Aspirin',
                'smiles': 'CC(=O)Oc1ccccc1C(=O)O',
                'molecular_weight': 180.16,
                'logp': 1.19
            }
        ]
        await self._save_pubchem_data(sample_data)
    
    async def _load_sample_zinc15_data(self):
        """Load sample ZINC15 data as fallback"""
        sample_data = [
            {
                'zinc_id': 'ZINC000000001',
                'substance_name': 'Sample Compound',
                'smiles': 'CC(=O)Oc1ccccc1C(=O)O',
                'molecular_weight': 180.0,
                'supplier_count': 5
            }
        ]
        await self._save_zinc15_data(sample_data)
    
    async def _load_sample_qm9_data(self):
        """Load sample QM9 data as fallback"""
        sample_data = [
            {
                'molecule_id': 'QM9_1',
                'smiles': 'C',
                'homo_energy': -0.50,
                'lumo_energy': 0.10,
                'gap_energy': 0.60,
                'dipole_moment': 0.0,
                'polarizability': 2.5
            }
        ]
        await self._save_qm9_data(sample_data)