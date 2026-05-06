# backend/fetchers/clinical_trial_fetcher.py
import asyncio
import httpx
import logging
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

class ClinicalTrialFetcher:
    """Fetches clinical trial data from 3 datasets"""
    
    def __init__(self, db_path: str, cache_dir: Path):
        self.db_path = db_path
        self.cache_dir = cache_dir
    
    async def fetch_clinicaltrials(self):
        """Fetch from ClinicalTrials.gov API"""
        logger.info("🔍 Fetching ClinicalTrials.gov...")
        
        try:
            # ClinicalTrials.gov API v2
            url = "https://clinicaltrials.gov/api/v2/studies"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    'pageSize': 100,
                    'countTotal': 'true',
                    'query.cond': 'cancer',  # Sample query
                }
                
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    records = []
                    
                    for study in data.get('studies', [])[:100]:
                        proto = study.get('protocolSection', {})
                        record = {
                            'nct_id': proto.get('identificationModule', {}).get('nctId', ''),
                            'trial_title': proto.get('identificationModule', {}).get('briefTitle', ''),
                            'condition': ', '.join([c.get('name', '') for c in proto.get('conditionsModule', {}).get('conditions', [])]),
                            'phase': proto.get('designModule', {}).get('phases', [''])[0],
                            'status': proto.get('statusModule', {}).get('overallStatus', ''),
                            'enrollment': proto.get('designModule', {}).get('enrollmentInfo', {}).get('count', 0),
                        }
                        records.append(record)
                    
                    await self._save_clinical_trials_data(records)
                    logger.info(f"✅ Ingested {len(records)} ClinicalTrials records")
                else:
                    logger.warning(f"⚠️ ClinicalTrials API returned {response.status_code}")
                    await self._load_sample_clinical_trials_data()
        
        except Exception as e:
            logger.error(f"❌ Error fetching ClinicalTrials: {e}")
            await self._load_sample_clinical_trials_data()
    
    async def fetch_mimic(self):
        """Load MIMIC-III Sample Patient Data"""
        logger.info("🔍 Fetching MIMIC-III Patient Data...")
        
        try:
            # MIMIC-III requires credentialing - using sample data
            logger.info("⚠️ MIMIC-III requires credentialing. Loading sample data...")
            await self._load_sample_mimic_data()
        
        except Exception as e:
            logger.error(f"❌ Error with MIMIC data: {e}")
            await self._load_sample_mimic_data()
    
    async def fetch_aact(self):
        """Fetch from AACT Database"""
        logger.info("🔍 Fetching AACT Trial Data...")
        
        try:
            # AACT is a PostgreSQL database - we'll use their data dumps or API
            # For now, using sample data from ClinicalTrials.gov
            await self._load_sample_aact_data()
        
        except Exception as e:
            logger.error(f"❌ Error fetching AACT: {e}")
            await self._load_sample_aact_data()
    
    async def _save_clinical_trials_data(self, records: List[Dict]):
        """Save ClinicalTrials.gov data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in records:
            cursor.execute('''
                INSERT OR REPLACE INTO clinical_trials
                (nct_id, trial_title, condition, phase, status, enrollment, ingestion_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get('nct_id', ''),
                record.get('trial_title', ''),
                record.get('condition', ''),
                record.get('phase', ''),
                record.get('status', ''),
                record.get('enrollment', 0),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    async def _save_mimic_data(self, records: List[Dict]):
        """Save MIMIC-III data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in records:
            cursor.execute('''
                INSERT OR REPLACE INTO mimic_patients
                (patient_id, gender, age, mortality, admission_count, 
                 hospital_expire_flag, ingestion_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get('patient_id', ''),
                record.get('gender', ''),
                record.get('age', 0),
                record.get('mortality', 0),
                record.get('admission_count', 0),
                record.get('hospital_expire_flag', 0),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    async def _save_aact_data(self, records: List[Dict]):
        """Save AACT data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in records:
            cursor.execute('''
                INSERT OR REPLACE INTO aact_trials
                (nct_id, overall_status, phase, enrollment, adverse_events_count, ingestion_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                record.get('nct_id', ''),
                record.get('overall_status', ''),
                record.get('phase', ''),
                record.get('enrollment', 0),
                record.get('adverse_events_count', 0),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    async def _load_sample_clinical_trials_data(self):
        """Load sample ClinicalTrials data"""
        sample_data = [{
            'nct_id': 'NCT04412565',
            'trial_title': 'COVID-19 Vaccine Study',
            'condition': 'COVID-19',
            'phase': 'Phase 3',
            'status': 'COMPLETED',
            'enrollment': 44000,
        }]
        await self._save_clinical_trials_data(sample_data)
    
    async def _load_sample_mimic_data(self):
        """Load sample MIMIC-III data"""
        sample_data = [
            {
                'patient_id': 'MIMIC_001',
                'gender': 'M',
                'age': 65,
                'mortality': 0,
                'admission_count': 2,
                'hospital_expire_flag': 0,
            },
            {
                'patient_id': 'MIMIC_002',
                'gender': 'F',
                'age': 72,
                'mortality': 1,
                'admission_count': 3,
                'hospital_expire_flag': 1,
            }
        ]
        await self._save_mimic_data(sample_data)
    
    async def _load_sample_aact_data(self):
        """Load sample AACT data"""
        sample_data = [{
            'nct_id': 'NCT04412565',
            'overall_status': 'COMPLETED',
            'phase': 'Phase 3',
            'enrollment': 44000,
            'adverse_events_count': 245,
        }]
        await self._save_aact_data(sample_data)