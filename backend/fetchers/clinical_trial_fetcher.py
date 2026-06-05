# backend/fetchers/clinical_trial_fetcher.py
"""Fetch clinical trial data from multiple sources"""
import logging
import asyncio
import httpx
from typing import List, Dict, Any
from fetchers.base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class ClinicalTrialFetcher(BaseFetcher):
    """Fetch clinical trial data from ClinicalTrials.gov, MIMIC, and AACT"""
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """
        Main fetch method - combines all clinical trial data sources
        Returns list of trial records ready for ingestion
        """
        logger.info("🔍 Fetching clinical trial data from all sources...")
        
        # Try to load from cache first
        cached_data = self._load_from_cache("clinical_trials")
        if cached_data:
            logger.info(f"✅ Loaded {len(cached_data)} clinical trial records from cache")
            return self._add_metadata(cached_data)
        
        try:
            # Fetch from all sources in parallel
            logger.info("📡 Fetching from multiple sources (ClinicalTrials.gov, MIMIC, AACT)...")
            
            ct_data = await self.fetch_clinicaltrials()
            mimic_data = await self.fetch_mimic()
            aact_data = await self.fetch_aact()
            
            # Combine all data
            all_trial_data = ct_data + mimic_data + aact_data
            
            # Remove duplicates by nct_id or patient_id
            unique_trials = {}
            for trial in all_trial_data:
                # Use nct_id for trials, patient_id for patient data
                unique_id = trial.get('nct_id') or trial.get('patient_id')
                if unique_id and unique_id not in unique_trials:
                    unique_trials[unique_id] = trial
            
            final_data = list(unique_trials.values())
            
            if final_data:
                self._save_to_cache("clinical_trials", final_data)
                logger.info(f"✅ Fetched {len(final_data)} unique clinical trial records (after dedup)")
            
            return self._add_metadata(final_data)
        
        except Exception as e:
            logger.error(f"❌ Error in clinical trial fetch: {e}")
            return []
    
    async def fetch_clinicaltrials(self) -> List[Dict[str, Any]]:
        """Fetch from ClinicalTrials.gov API"""
        logger.info("  📊 ClinicalTrials.gov: Fetching trial data...")
        
        try:
            url = "https://clinicaltrials.gov/api/v2/studies"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    'pageSize': 100,
                    'countTotal': 'true',
                    'query.cond': 'cancer',  # Sample query
                }
                
                response = await client.get(url, params=params, timeout=15.0)
                
                if response.status_code == 200:
                    data = response.json()
                    records = []
                    
                    for study in data.get('studies', [])[:100]:
                        try:
                            proto = study.get('protocolSection', {})
                            
                            trial = {
                                'nct_id': proto.get('identificationModule', {}).get('nctId', ''),
                                'title': proto.get('identificationModule', {}).get('briefTitle', ''),
                                'condition': ', '.join([c.get('name', '') for c in proto.get('conditionsModule', {}).get('conditions', [])]) or 'Unknown',
                                'phase': proto.get('designModule', {}).get('phases', ['Unknown'])[0] if proto.get('designModule', {}).get('phases') else 'Unknown',
                                'status': proto.get('statusModule', {}).get('overallStatus', 'Unknown'),
                                'enrollment': proto.get('designModule', {}).get('enrollmentInfo', {}).get('count', 0),
                            }
                            
                            if trial['nct_id']:
                                records.append(trial)
                        
                        except Exception as e:
                            logger.warning(f"    ⚠️ Skipping trial: {e}")
                    
                    logger.info(f"  ✅ ClinicalTrials.gov: Got {len(records)} records")
                    return records
                else:
                    logger.warning(f"  ⚠️ ClinicalTrials API returned {response.status_code}")
                    return await self._load_sample_clinicaltrials_data()
        
        except Exception as e:
            logger.error(f"  ❌ ClinicalTrials fetch error: {e}")
            return await self._load_sample_clinicaltrials_data()
    
    async def fetch_mimic(self) -> List[Dict[str, Any]]:
        """Fetch MIMIC-III Sample Patient Data"""
        logger.info("  📊 MIMIC-III: Fetching patient data...")
        
        try:
            # MIMIC-III requires credentialing and database access
            # Using sample data as fallback
            logger.info("    ⚠️ MIMIC-III requires credentialing, using sample data...")
            return await self._load_sample_mimic_data()
        
        except Exception as e:
            logger.error(f"  ❌ MIMIC fetch error: {e}")
            return await self._load_sample_mimic_data()
    
    async def fetch_aact(self) -> List[Dict[str, Any]]:
        """Fetch from AACT Database"""
        logger.info("  📊 AACT: Fetching trial metadata...")
        
        try:
            # AACT is a PostgreSQL database aggregating ClinicalTrials data
            # Using sample data as fallback
            logger.info("    ⚠️ AACT requires database credentials, using sample data...")
            return await self._load_sample_aact_data()
        
        except Exception as e:
            logger.error(f"  ❌ AACT fetch error: {e}")
            return await self._load_sample_aact_data()
    
    async def _load_sample_clinicaltrials_data(self) -> List[Dict[str, Any]]:
        """Load sample ClinicalTrials.gov data"""
        logger.info("    Loading sample ClinicalTrials.gov data...")
        return [
            {
                'nct_id': 'NCT04412565',
                'title': 'COVID-19 Vaccine Study Phase 3',
                'condition': 'COVID-19',
                'phase': 'Phase 3',
                'status': 'COMPLETED',
                'enrollment': 44000
            },
            {
                'nct_id': 'NCT04567890',
                'title': 'Phase 3 Study of Drug X in Type 2 Diabetes',
                'condition': 'Type 2 Diabetes Mellitus',
                'phase': 'Phase 3',
                'status': 'Recruiting',
                'enrollment': 500
            },
            {
                'nct_id': 'NCT04567891',
                'title': 'Phase 2 Study of Drug Z in Hypertension',
                'condition': 'Hypertension',
                'phase': 'Phase 2',
                'status': 'Active, not recruiting',
                'enrollment': 300
            },
            {
                'nct_id': 'NCT04567892',
                'title': 'Phase 4 Study of Drug Y in Cardiovascular Disease',
                'condition': 'Cardiovascular Disease',
                'phase': 'Phase 4',
                'status': 'Recruiting',
                'enrollment': 1000
            },
            {
                'nct_id': 'NCT04567893',
                'title': 'Phase 1 Study of Novel Compound in Healthy Volunteers',
                'condition': 'Healthy',
                'phase': 'Phase 1',
                'status': 'Active, not recruiting',
                'enrollment': 50
            }
        ]
    
    async def _load_sample_mimic_data(self) -> List[Dict[str, Any]]:
        """Load sample MIMIC-III patient data"""
        logger.info("    Loading sample MIMIC-III patient data...")
        return [
            {
                'patient_id': 'MIMIC_001',
                'gender': 'M',
                'age': 65,
                'admission_type': 'EMERGENCY',
                'mortality': 0
            },
            {
                'patient_id': 'MIMIC_002',
                'gender': 'F',
                'age': 72,
                'admission_type': 'URGENT',
                'mortality': 1
            },
            {
                'patient_id': 'MIMIC_003',
                'gender': 'M',
                'age': 55,
                'admission_type': 'ELECTIVE',
                'mortality': 0
            },
            {
                'patient_id': 'MIMIC_004',
                'gender': 'F',
                'age': 68,
                'admission_type': 'EMERGENCY',
                'mortality': 0
            }
        ]
    
    async def _load_sample_aact_data(self) -> List[Dict[str, Any]]:
        """Load sample AACT aggregated trial data"""
        logger.info("    Loading sample AACT trial data...")
        return [
            {
                'nct_id': 'AACT_NCT04412565',
                'title': 'AACT: COVID-19 Vaccine Study',
                'condition': 'COVID-19',
                'phase': 'Phase 3',
                'status': 'COMPLETED',
                'enrollment': 44000
            },
            {
                'nct_id': 'AACT_NCT04567890',
                'title': 'AACT: Type 2 Diabetes Study',
                'condition': 'Type 2 Diabetes',
                'phase': 'Phase 3',
                'status': 'Recruiting',
                'enrollment': 500
            }
        ]