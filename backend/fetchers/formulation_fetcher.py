# backend/fetchers/formulation_fetcher.py
import asyncio
import httpx
import logging
import sqlite3
import csv
import io
from pathlib import Path
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

class FormulationFetcher:
    """Fetches formulation data from 4 datasets"""
    
    def __init__(self, db_path: str, cache_dir: Path):
        self.db_path = db_path
        self.cache_dir = cache_dir
    
    async def fetch_drugbank(self):
        """Fetch from DrugBank"""
        logger.info("🔍 Fetching DrugBank Formulations...")
        
        try:
            # DrugBank API (requires API key)
            # Using sample data as fallback
            await self._load_sample_drugbank_data()
        
        except Exception as e:
            logger.error(f"❌ Error fetching DrugBank: {e}")
            await self._load_sample_drugbank_data()
    
    async def fetch_esol(self):
        """Load ESOL Solubility Dataset from HuggingFace"""
        logger.info("🔍 Fetching ESOL Solubility...")
        
        try:
            from datasets import load_dataset
            
            # Load ESOL dataset
            logger.info("Loading ESOL from HuggingFace...")
            dataset = load_dataset('delaney', split='train[:100]')
            
            records = []
            for item in dataset:
                record = {
                    'compound_id': f"ESOL_{len(records)}",
                    'smiles': item.get('smiles', ''),
                    'solubility_value': float(item.get('measured log solubility in mols per litre', 0)),
                    'mw': float(item.get('Molecular Weight', 0)),
                    'logp': float(item.get('LogP', 0)),
                    'hbd': int(item.get('Number of H and D atoms', 0)),
                    'hba': int(item.get('Number of Heteroatoms', 0)),
                }
                records.append(record)
            
            await self._save_esol_data(records)
            logger.info(f"✅ Ingested {len(records)} ESOL records")
        
        except Exception as e:
            logger.error(f"❌ Error fetching ESOL: {e}")
            await self._load_sample_esol_data()
    
    async def fetch_tox21(self):
        """Load Tox21 Toxicity Dataset"""
        logger.info("🔍 Fetching Tox21 Toxicity...")
        
        try:
            # Tox21 dataset from HuggingFace or NIH
            from datasets import load_dataset
            
            logger.info("Loading Tox21 from HuggingFace...")
            dataset = load_dataset('tox21', split='train[:100]')
            
            records = []
            for item in dataset:
                record = {
                    'compound_id': f"TOX21_{len(records)}",
                    'smiles': item.get('smiles', ''),
                    'nr_ar_lbd': int(item.get('NR-AR-LBD', 0)),
                    'nr_ar': int(item.get('NR-AR', 0)),
                    'nr_ahr': int(item.get('NR-AhR', 0)),
                    'sr_hse': int(item.get('SR-HSE', 0)),
                    'sr_mmp': int(item.get('SR-MMP', 0)),
                    'sr_p53': int(item.get('SR-p53', 0)),
                }
                records.append(record)
            
            await self._save_tox21_data(records)
            logger.info(f"✅ Ingested {len(records)} Tox21 records")
        
        except Exception as e:
            logger.error(f"❌ Error fetching Tox21: {e}")
            await self._load_sample_tox21_data()
    
    async def fetch_gras(self):
        """Load FDA GRAS Excipients List"""
        logger.info("🔍 Fetching GRAS Excipients...")
        
        try:
            # FDA GRAS list - typically available as CSV
            # Using sample data
            await self._load_sample_gras_data()
        
        except Exception as e:
            logger.error(f"❌ Error fetching GRAS: {e}")
            await self._load_sample_gras_data()
    
    async def _save_drugbank_data(self, records: List[Dict]):
        """Save DrugBank data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in records:
            cursor.execute('''
                INSERT OR REPLACE INTO drugbank_formulations
                (drug_id, drug_name, smiles, route_of_administration, dosage_form,
                 excipients, solubility_comment, ingestion_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get('drug_id', ''),
                record.get('drug_name', ''),
                record.get('smiles', ''),
                record.get('route_of_administration', ''),
                record.get('dosage_form', ''),
                record.get('excipients', ''),
                record.get('solubility_comment', ''),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    async def _save_esol_data(self, records: List[Dict]):
        """Save ESOL solubility data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in records:
            cursor.execute('''
                INSERT OR REPLACE INTO esol_solubility
                (compound_id, smiles, solubility_value, mw, logp, hbd, hba, ingestion_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get('compound_id', ''),
                record.get('smiles', ''),
                record.get('solubility_value', 0),
                record.get('mw', 0),
                record.get('logp', 0),
                record.get('hbd', 0),
                record.get('hba', 0),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    async def _save_tox21_data(self, records: List[Dict]):
        """Save Tox21 data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in records:
            cursor.execute('''
                INSERT OR REPLACE INTO tox21_toxicity
                (compound_id, smiles, nr_ar_lbd, nr_ar, nr_ahr, nr_aromatase, nr_er,
                 nr_er_lbd, nr_pxr, sr_atad5, sr_hse, sr_mmp, sr_p53, ingestion_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get('compound_id', ''),
                record.get('smiles', ''),
                record.get('nr_ar_lbd', 0),
                record.get('nr_ar', 0),
                record.get('nr_ahr', 0),
                record.get('nr_aromatase', 0),
                record.get('nr_er', 0),
                record.get('nr_er_lbd', 0),
                record.get('nr_pxr', 0),
                record.get('sr_atad5', 0),
                record.get('sr_hse', 0),
                record.get('sr_mmp', 0),
                record.get('sr_p53', 0),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    async def _save_gras_data(self, records: List[Dict]):
        """Save GRAS excipients data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in records:
            cursor.execute('''
                INSERT OR REPLACE INTO gras_excipients
                (excipient_id, excipient_name, usage_type, fda_status, molecular_weight,
                 solubility, ph_range, ingestion_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get('excipient_id', ''),
                record.get('excipient_name', ''),
                record.get('usage_type', ''),
                record.get('fda_status', ''),
                record.get('molecular_weight', 0),
                record.get('solubility', ''),
                record.get('ph_range', ''),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    async def _load_sample_drugbank_data(self):
        """Load sample DrugBank data"""
        sample_data = [{
            'drug_id': 'DB00001',
            'drug_name': 'Aspirin',
            'smiles': 'CC(=O)Oc1ccccc1C(=O)O',
            'route_of_administration': 'Oral',
            'dosage_form': 'Tablet',
            'excipients': 'Cellulose, Starch',
        }]
        await self._save_drugbank_data(sample_data)
    
    async def _load_sample_esol_data(self):
        """Load sample ESOL data"""
        sample_data = [{
            'compound_id': 'ESOL_1',
            'smiles': 'CC(=O)Oc1ccccc1C(=O)O',
            'solubility_value': -0.77,
            'mw': 180.16,
            'logp': 1.19,
            'hbd': 2,
            'hba': 4,
        }]
        await self._save_esol_data(sample_data)
    
    async def _load_sample_tox21_data(self):
        """Load sample Tox21 data"""
        sample_data = [{
            'compound_id': 'TOX21_1',
            'smiles': 'CC(=O)Oc1ccccc1C(=O)O',
            'nr_ar_lbd': 0,
            'nr_ar': 0,
            'nr_ahr': 0,
            'sr_hse': 0,
            'sr_mmp': 0,
            'sr_p53': 0,
        }]
        await self._save_tox21_data(sample_data)
    
    async def _load_sample_gras_data(self):
        """Load sample GRAS data"""
        sample_data = [
            {
                'excipient_id': 'GRAS_001',
                'excipient_name': 'Cellulose',
                'usage_type': 'Binder',
                'fda_status': 'GRAS',
                'molecular_weight': 162.14,
                'solubility': 'Insoluble',
            },
            {
                'excipient_id': 'GRAS_002',
                'excipient_name': 'Lactose',
                'usage_type': 'Filler',
                'fda_status': 'GRAS',
                'molecular_weight': 342.3,
                'solubility': 'Soluble',
            }
        ]
        await self._save_gras_data(sample_data)