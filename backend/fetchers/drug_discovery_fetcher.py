# backend/fetchers/drug_discovery_fetcher.py
"""Fetch drug discovery data from multiple pharmaceutical databases"""
import logging
import asyncio
import httpx
from typing import List, Dict, Any
from fetchers.base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class DrugDiscoveryFetcher(BaseFetcher):
    """Fetch drug discovery data from ChEMBL, PubChem, ZINC15, and QM9"""
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """
        Main fetch method - combines all data sources
        Returns list of drug records ready for ingestion
        """
        logger.info("🔍 Fetching drug discovery data from all sources...")
        
        # Try to load from cache first
        cached_data = self._load_from_cache("drug_discovery")
        if cached_data:
            logger.info(f"✅ Loaded {len(cached_data)} drug records from cache")
            return self._add_metadata(cached_data)
        
        try:
            # Fetch from all sources in parallel
            logger.info("📡 Fetching from multiple sources (ChEMBL, PubChem, ZINC15, QM9)...")
            
            chembl_data = await self.fetch_chembl()
            pubchem_data = await self.fetch_pubchem()
            zinc15_data = await self.fetch_zinc15()
            qm9_data = await self.fetch_qm9()
            
            # Combine all data
            all_drug_data = chembl_data + pubchem_data + zinc15_data + qm9_data
            
            # Remove duplicates by compound_id
            unique_drugs = {}
            for drug in all_drug_data:
                compound_id = drug.get('compound_id')
                if compound_id and compound_id not in unique_drugs:
                    unique_drugs[compound_id] = drug
            
            final_data = list(unique_drugs.values())
            
            if final_data:
                self._save_to_cache("drug_discovery", final_data)
                logger.info(f"✅ Fetched {len(final_data)} unique drug records (after dedup)")
            
            return self._add_metadata(final_data)
        
        except Exception as e:
            logger.error(f"❌ Error in drug discovery fetch: {e}")
            return []
    
    async def fetch_chembl(self) -> List[Dict[str, Any]]:
        """Fetch from ChEMBL Bioactivity Database"""
        logger.info("  📊 ChEMBL: Fetching bioactivity data...")
        
        try:
            url = "https://www.ebi.ac.uk/chembl/api/data/activity.json"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Fetch first 100 records as sample
                response = await client.get(url, params={"limit": 100})
                
                if response.status_code == 200:
                    data = response.json()
                    records = data.get('results', []) or data.get('activities', [])
                    
                    chembl_data = []
                    for record in records:
                        try:
                            drug = {
                                'compound_id': record.get('molecule_chembl_id', ''),
                                'compound_name': record.get('molecule_pref_name', ''),
                                'smiles': record.get('canonical_smiles', ''),
                                'target': record.get('target_pref_name', ''),
                                'activity_value': record.get('standard_value'),
                                'activity_type': record.get('type', '')
                            }
                            if drug['compound_id']:  # Only add if has ID
                                chembl_data.append(drug)
                        except Exception as e:
                            logger.warning(f"    ⚠️ Skipping ChEMBL record: {e}")
                    
                    logger.info(f"  ✅ ChEMBL: Got {len(chembl_data)} records")
                    return chembl_data
                else:
                    logger.warning(f"  ⚠️ ChEMBL API returned {response.status_code}")
                    return await self._load_sample_chembl_data()
        
        except Exception as e:
            logger.error(f"  ❌ ChEMBL fetch error: {e}")
            return await self._load_sample_chembl_data()
    
    async def fetch_pubchem(self) -> List[Dict[str, Any]]:
        """Fetch from PubChem Molecular Properties"""
        logger.info("  📊 PubChem: Fetching molecular properties...")
        
        try:
            # Sample drug CIDs (Aspirin, Ibuprofen, Naproxen, Acetaminophen, Naproxen, Diclofenac)
            sample_cids = [2244, 3672, 5280343, 2662, 5360545, 3033]
            
            compounds = []
            async with httpx.AsyncClient(timeout=30.0) as client:
                for cid in sample_cids:
                    try:
                        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/JSON"
                        response = await client.get(url, timeout=10.0)
                        
                        if response.status_code == 200:
                            data = response.json()
                            compound = self._parse_pubchem_response(data, cid)
                            if compound:
                                compounds.append(compound)
                        
                        await asyncio.sleep(0.3)  # Rate limiting
                    
                    except Exception as e:
                        logger.warning(f"    ⚠️ Could not fetch PubChem CID {cid}: {e}")
            
            if compounds:
                logger.info(f"  ✅ PubChem: Got {len(compounds)} records")
                return compounds
            else:
                logger.warning("  ⚠️ PubChem: No data fetched, using sample data")
                return await self._load_sample_pubchem_data()
        
        except Exception as e:
            logger.error(f"  ❌ PubChem fetch error: {e}")
            return await self._load_sample_pubchem_data()
    
    async def fetch_zinc15(self) -> List[Dict[str, Any]]:
        """Fetch from ZINC15 Database"""
        logger.info("  📊 ZINC15: Fetching compounds...")
        
        try:
            url = "https://zinc.docking.org/api/substances/"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params={"limit": 50}, timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    records = data.get('results', [])
                    
                    zinc_data = []
                    for record in records:
                        try:
                            drug = {
                                'compound_id': record.get('zinc_id', ''),
                                'compound_name': record.get('substance_name', ''),
                                'smiles': record.get('smiles', ''),
                                'molecular_weight': record.get('molecular_weight'),
                                'price': record.get('price_min')
                            }
                            if drug['compound_id']:
                                zinc_data.append(drug)
                        except Exception as e:
                            logger.warning(f"    ⚠️ Skipping ZINC15 record: {e}")
                    
                    logger.info(f"  ✅ ZINC15: Got {len(zinc_data)} records")
                    return zinc_data
                else:
                    logger.warning(f"  ⚠️ ZINC15 API returned {response.status_code}")
                    return await self._load_sample_zinc15_data()
        
        except Exception as e:
            logger.error(f"  ❌ ZINC15 fetch error: {e}")
            return await self._load_sample_zinc15_data()
    
    async def fetch_qm9(self) -> List[Dict[str, Any]]:
        """Load QM9 Quantum Properties"""
        logger.info("  📊 QM9: Fetching quantum properties...")
        
        try:
            try:
                from datasets import load_dataset
                
                logger.info("    Loading QM9 from HuggingFace (first 100 molecules)...")
                dataset = load_dataset('qm9', split='train[:100]')
                
                qm9_data = []
                for idx, item in enumerate(dataset):
                    try:
                        record = {
                            'compound_id': f'QM9_{idx}',
                            'molecule_id': item.get('ID', ''),
                            'smiles': item.get('SMILES', ''),
                            'homo_energy': float(item.get('homo', 0)) if item.get('homo') else 0,
                            'lumo_energy': float(item.get('lumo', 0)) if item.get('lumo') else 0,
                            'gap_energy': float(item.get('gap', 0)) if item.get('gap') else 0,
                        }
                        qm9_data.append(record)
                    except Exception as e:
                        logger.warning(f"    ⚠️ Skipping QM9 record: {e}")
                
                logger.info(f"  ✅ QM9: Got {len(qm9_data)} records")
                return qm9_data
            
            except ImportError:
                logger.warning("  ⚠️ HuggingFace datasets not installed, using sample data")
                return await self._load_sample_qm9_data()
        
        except Exception as e:
            logger.error(f"  ❌ QM9 fetch error: {e}")
            return await self._load_sample_qm9_data()
    
    def _parse_pubchem_response(self, data: Dict, cid: int) -> Dict[str, Any]:
        """Parse PubChem API response and calculate metrics using RDKit"""
        try:
            compound = data['PC_Compounds'][0]
            
            # Extract SMILES securely from atomic arrays
            smiles = ''
            if compound.get('atoms') and compound['atoms'].get('aid'):
                smiles = compound.get('atoms', {}).get('aid', [{}])[0].get('smiles', '')
            
            # Alternate structural path scan if properties list is active
            if not smiles and compound.get('props'):
                for prop in compound['props']:
                    if prop.get('urn', {}).get('label') == 'SMILES':
                        smiles = prop.get('value', {}).get('sval', '')
                        break
            
            # Compute RDKit descriptors natively
            mw = 0.0
            logp = 0.0
            if smiles:
                try:
                    from rdkit import Chem
                    from rdkit.Chem import Descriptors
                    from rdkit.Chem import Crippen
                    
                    mol = Chem.MolFromSmiles(smiles)
                    if mol:
                        mw = round(Descriptors.MolWt(mol), 2)
                        logp = round(Crippen.MolLogP(mol), 2)
                except Exception as rdkit_err:
                    logger.warning(f"    ⚠️ RDKit local computation bypassed for CID {cid}: {rdkit_err}")

            record = {
                'compound_id': f'PUBCHEM_{cid}',
                'compound_name': f'PubChem_CID_{cid}',
                'smiles': smiles,
                'molecular_weight': mw if mw > 0 else 180.16, # Logical default fallback
                'logp': logp
            }
            
            return record
        except Exception as e:
            logger.warning(f"Could not parse PubChem response for CID {cid}: {e}")
            return None
            
    async def _load_sample_chembl_data(self) -> List[Dict[str, Any]]:
        return [
            {'compound_id': 'CHEMBL100001', 'compound_name': 'Aspirin', 'smiles': 'CC(=O)Oc1ccccc1C(=O)O', 'target': 'Cyclooxygenase', 'activity_value': 8.5, 'activity_type': 'IC50'},
            {'compound_id': 'CHEMBL100002', 'compound_name': 'Ibuprofen', 'smiles': 'CC(C)Cc1ccc(cc1)C(C)C(=O)O', 'target': 'Cyclooxygenase', 'activity_value': 9.2, 'activity_type': 'IC50'}
        ]

    async def _load_sample_pubchem_data(self) -> List[Dict[str, Any]]:
        return [
            {'compound_id': 'PUBCHEM_2244', 'compound_name': 'Aspirin', 'smiles': 'CC(=O)Oc1ccccc1C(=O)O', 'molecular_weight': 180.16, 'logp': 1.19}
        ]

    async def _load_sample_zinc15_data(self) -> List[Dict[str, Any]]:
        return [{'compound_id': 'ZINC000000001', 'compound_name': 'Sample 1', 'smiles': 'CC(=O)Oc1ccccc1C(=O)O', 'molecular_weight': 180.0, 'price': 50.0}]

    async def _load_sample_qm9_data(self) -> List[Dict[str, Any]]:
        return [{'compound_id': 'QM9_1', 'molecule_id': 'QM9_001', 'smiles': 'C', 'homo_energy': -0.50, 'lumo_energy': 0.10, 'gap_energy': 0.60}]