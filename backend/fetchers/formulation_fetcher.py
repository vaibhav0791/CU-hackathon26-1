# backend/fetchers/formulation_fetcher.py
"""Fetch pharmaceutical formulation and compound property data"""
import logging
import asyncio
from typing import List, Dict, Any
from fetchers.base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class FormulationFetcher(BaseFetcher):
    """Fetch pharmaceutical formulation data from DrugBank, ESOL, Tox21, and GRAS"""
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """
        Main fetch method - combines all formulation data sources
        Returns list of formulation records ready for ingestion
        """
        logger.info("🔍 Fetching formulation data from all sources...")
        
        # Try to load from cache first
        cached_data = self._load_from_cache("formulations")
        if cached_data:
            logger.info(f"✅ Loaded {len(cached_data)} formulation records from cache")
            return self._add_metadata(cached_data)
        
        try:
            # Fetch from all sources in parallel
            logger.info("📡 Fetching from multiple sources (DrugBank, ESOL, Tox21, GRAS)...")
            
            drugbank_data = await self.fetch_drugbank()
            esol_data = await self.fetch_esol()
            tox21_data = await self.fetch_tox21()
            gras_data = await self.fetch_gras()
            
            # Combine all data
            all_formulation_data = drugbank_data + esol_data + tox21_data + gras_data
            
            # Remove duplicates by compound_id or drug_id
            unique_formulations = {}
            for formulation in all_formulation_data:
                unique_id = (formulation.get('drug_id') or formulation.get('compound_id') or 
                           formulation.get('excipient_id'))
                if unique_id and unique_id not in unique_formulations:
                    unique_formulations[unique_id] = formulation
            
            final_data = list(unique_formulations.values())
            
            if final_data:
                self._save_to_cache("formulations", final_data)
                logger.info(f"✅ Fetched {len(final_data)} unique formulation records (after dedup)")
            
            return self._add_metadata(final_data)
        
        except Exception as e:
            logger.error(f"❌ Error in formulation fetch: {e}")
            return []
    
    async def fetch_drugbank(self) -> List[Dict[str, Any]]:
        """Fetch from DrugBank"""
        logger.info("  📊 DrugBank: Fetching drug formulations...")
        
        try:
            # DrugBank API requires authentication
            # Using sample data as fallback
            logger.info("    ⚠️ DrugBank requires API key, using sample data")
            return await self._load_sample_drugbank_data()
        
        except Exception as e:
            logger.error(f"  ❌ DrugBank fetch error: {e}")
            return await self._load_sample_drugbank_data()
    
    async def fetch_esol(self) -> List[Dict[str, Any]]:
        """Load ESOL Solubility Dataset"""
        logger.info("  📊 ESOL: Fetching solubility data...")
        
        try:
            try:
                from datasets import load_dataset
                
                logger.info("    Loading ESOL from HuggingFace (first 100 compounds)...")
                dataset = load_dataset('delaney', split='train[:100]')
                
                records = []
                for idx, item in enumerate(dataset):
                    try:
                        record = {
                            'compound_id': f"ESOL_{idx}",
                            'smiles': item.get('smiles', ''),
                            'solubility_value': float(item.get('measured log solubility in mols per litre', 0)),
                            'molecular_weight': float(item.get('Molecular Weight', 0)),
                            'logp': float(item.get('LogP', 0)),
                            'h_bond_donors': int(item.get('Number of H and D atoms', 0)),
                            'h_bond_acceptors': int(item.get('Number of Heteroatoms', 0)),
                        }
                        records.append(record)
                    except Exception as e:
                        logger.warning(f"    ⚠️ Skipping ESOL entry: {e}")
                
                logger.info(f"  ✅ ESOL: Got {len(records)} records")
                return records
            
            except ImportError:
                logger.warning("    ⚠️ HuggingFace datasets not installed, using sample data")
                return await self._load_sample_esol_data()
        
        except Exception as e:
            logger.error(f"  ❌ ESOL fetch error: {e}")
            return await self._load_sample_esol_data()
    
    async def fetch_tox21(self) -> List[Dict[str, Any]]:
        """Load Tox21 Toxicity Dataset"""
        logger.info("  📊 Tox21: Fetching toxicity data...")
        
        try:
            try:
                from datasets import load_dataset
                
                logger.info("    Loading Tox21 from HuggingFace (first 100 compounds)...")
                dataset = load_dataset('tox21', split='train[:100]')
                
                records = []
                for idx, item in enumerate(dataset):
                    try:
                        record = {
                            'compound_id': f"TOX21_{idx}",
                            'smiles': item.get('smiles', ''),
                            'nr_ar_lbd': int(item.get('NR-AR-LBD', 0)),
                            'nr_ar': int(item.get('NR-AR', 0)),
                            'nr_ahr': int(item.get('NR-AhR', 0)),
                            'sr_hse': int(item.get('SR-HSE', 0)),
                            'sr_mmp': int(item.get('SR-MMP', 0)),
                            'sr_p53': int(item.get('SR-p53', 0)),
                        }
                        records.append(record)
                    except Exception as e:
                        logger.warning(f"    ⚠️ Skipping Tox21 entry: {e}")
                
                logger.info(f"  ✅ Tox21: Got {len(records)} records")
                return records
            
            except ImportError:
                logger.warning("    ⚠️ HuggingFace datasets not installed, using sample data")
                return await self._load_sample_tox21_data()
        
        except Exception as e:
            logger.error(f"  ❌ Tox21 fetch error: {e}")
            return await self._load_sample_tox21_data()
    
    async def fetch_gras(self) -> List[Dict[str, Any]]:
        """Load FDA GRAS Excipients List"""
        logger.info("  📊 GRAS: Fetching excipients data...")
        
        try:
            # FDA GRAS list - typically available as CSV or API
            # Using sample data as fallback
            logger.info("    ⚠️ FDA GRAS API not available, using sample data")
            return await self._load_sample_gras_data()
        
        except Exception as e:
            logger.error(f"  ❌ GRAS fetch error: {e}")
            return await self._load_sample_gras_data()
    
    async def _load_sample_drugbank_data(self) -> List[Dict[str, Any]]:
        """Load sample DrugBank data"""
        logger.info("    Loading sample DrugBank data...")
        return [
            {
                'drug_id': 'DB00945',
                'drug_name': 'Aspirin 500mg',
                'formulation_type': 'Tablet'
            },
            {
                'drug_id': 'DB00946',
                'drug_name': 'Ibuprofen 200mg',
                'formulation_type': 'Capsule'
            },
            {
                'drug_id': 'DB00148',
                'drug_name': 'Acetaminophen 325mg',
                'formulation_type': 'Tablet'
            },
            {
                'drug_id': 'DB00788',
                'drug_name': 'Naproxen 500mg',
                'formulation_type': 'Tablet'
            },
            {
                'drug_id': 'DB01050',
                'drug_name': 'Diclofenac 50mg',
                'formulation_type': 'Tablet'
            },
            {
                'drug_id': 'DB01248',
                'drug_name': 'Indomethacin 25mg',
                'formulation_type': 'Capsule'
            }
        ]
    
    async def _load_sample_esol_data(self) -> List[Dict[str, Any]]:
        """Load sample ESOL solubility data"""
        logger.info("    Loading sample ESOL data...")
        return [
            {
                'compound_id': 'ESOL_1',
                'smiles': 'CC(=O)Oc1ccccc1C(=O)O',
                'solubility_value': -0.77,
                'molecular_weight': 180.16,
                'logp': 1.19,
                'h_bond_donors': 2,
                'h_bond_acceptors': 4,
            },
            {
                'compound_id': 'ESOL_2',
                'smiles': 'CC(C)Cc1ccc(cc1)C(C)C(=O)O',
                'solubility_value': -3.97,
                'molecular_weight': 206.28,
                'logp': 3.97,
                'h_bond_donors': 1,
                'h_bond_acceptors': 2,
            },
            {
                'compound_id': 'ESOL_3',
                'smiles': 'CC(=O)Nc1ccc(O)cc1',
                'solubility_value': -0.07,
                'molecular_weight': 151.16,
                'logp': 0.46,
                'h_bond_donors': 2,
                'h_bond_acceptors': 2,
            },
            {
                'compound_id': 'ESOL_4',
                'smiles': 'COc1ccc2cc(ccc2c1)C(C)C(=O)O',
                'solubility_value': -3.18,
                'molecular_weight': 230.26,
                'logp': 3.18,
                'h_bond_donors': 1,
                'h_bond_acceptors': 3,
            }
        ]
    
    async def _load_sample_tox21_data(self) -> List[Dict[str, Any]]:
        """Load sample Tox21 toxicity data"""
        logger.info("    Loading sample Tox21 data...")
        return [
            {
                'compound_id': 'TOX21_1',
                'smiles': 'CC(=O)Oc1ccccc1C(=O)O',
                'nr_ar_lbd': 0,
                'nr_ar': 0,
                'nr_ahr': 0,
                'sr_hse': 0,
                'sr_mmp': 0,
                'sr_p53': 0,
            },
            {
                'compound_id': 'TOX21_2',
                'smiles': 'CC(C)Cc1ccc(cc1)C(C)C(=O)O',
                'nr_ar_lbd': 0,
                'nr_ar': 1,
                'nr_ahr': 0,
                'sr_hse': 1,
                'sr_mmp': 0,
                'sr_p53': 0,
            },
            {
                'compound_id': 'TOX21_3',
                'smiles': 'CC(=O)Nc1ccc(O)cc1',
                'nr_ar_lbd': 1,
                'nr_ar': 0,
                'nr_ahr': 1,
                'sr_hse': 0,
                'sr_mmp': 1,
                'sr_p53': 0,
            }
        ]
    
    async def _load_sample_gras_data(self) -> List[Dict[str, Any]]:
        """Load sample GRAS excipients data"""
        logger.info("    Loading sample GRAS data...")
        return [
            {
                'excipient_id': 'GRAS_001',
                'excipient_name': 'Cellulose',
                'usage_category': 'Binder',
                'fda_status': 'GRAS',
            },
            {
                'excipient_id': 'GRAS_002',
                'excipient_name': 'Lactose',
                'usage_category': 'Filler',
                'fda_status': 'GRAS',
            },
            {
                'excipient_id': 'GRAS_003',
                'excipient_name': 'Magnesium Stearate',
                'usage_category': 'Lubricant',
                'fda_status': 'GRAS',
            },
            {
                'excipient_id': 'GRAS_004',
                'excipient_name': 'Silica Gel',
                'usage_category': 'Desiccant',
                'fda_status': 'GRAS',
            },
            {
                'excipient_id': 'GRAS_005',
                'excipient_name': 'Starch',
                'usage_category': 'Disintegrant',
                'fda_status': 'GRAS',
            }
        ]