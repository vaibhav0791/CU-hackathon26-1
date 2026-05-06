# backend/ingestors/enhanced_db_handler.py
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class EnhancedDatabaseHandler:
    """Enhanced SQLite database handler"""
    
    def __init__(self, db_path: str = "pharma_enhanced.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database with all tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ingestion log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingestion_log (
                id INTEGER PRIMARY KEY,
                dataset_name TEXT,
                total_records INTEGER,
                ingestion_date TEXT,
                status TEXT,
                errors TEXT
            )
        ''')
        
        # Main data tables
        tables = {
            'chembl_bioactivity': '''(
                id INTEGER PRIMARY KEY,
                compound_id TEXT UNIQUE,
                compound_name TEXT,
                smiles TEXT,
                target TEXT,
                activity_value REAL,
                activity_type TEXT,
                ingestion_date TEXT
            )''',
            
            'pubchem_properties': '''(
                id INTEGER PRIMARY KEY,
                cid INTEGER UNIQUE,
                compound_name TEXT,
                smiles TEXT,
                molecular_weight REAL,
                logp REAL,
                tpsa REAL,
                hbd INTEGER,
                hba INTEGER,
                ingestion_date TEXT
            )''',
            
            'zinc15_compounds': '''(
                id INTEGER PRIMARY KEY,
                zinc_id TEXT UNIQUE,
                compound_name TEXT,
                smiles TEXT,
                molecular_weight REAL,
                price REAL,
                ingestion_date TEXT
            )''',
            
            'qm9_properties': '''(
                id INTEGER PRIMARY KEY,
                molecule_id TEXT UNIQUE,
                smiles TEXT,
                homo_energy REAL,
                lumo_energy REAL,
                gap_energy REAL,
                ingestion_date TEXT
            )''',
            
            'uniprot_sequences': '''(
                id INTEGER PRIMARY KEY,
                uniprot_id TEXT UNIQUE,
                protein_name TEXT,
                gene_name TEXT,
                organism TEXT,
                sequence_length INTEGER,
                ingestion_date TEXT
            )''',
            
            'pdb_structures': '''(
                id INTEGER PRIMARY KEY,
                pdb_id TEXT UNIQUE,
                title TEXT,
                resolution REAL,
                experimental_method TEXT,
                ingestion_date TEXT
            )''',
            
            'geo_expression': '''(
                id INTEGER PRIMARY KEY,
                geo_id TEXT UNIQUE,
                title TEXT,
                organism TEXT,
                ingestion_date TEXT
            )''',
            
            'string_interactions': '''(
                id INTEGER PRIMARY KEY,
                interaction_id TEXT UNIQUE,
                protein_a TEXT,
                protein_b TEXT,
                combined_score REAL,
                ingestion_date TEXT
            )''',
            
            'clinical_trials': '''(
                id INTEGER PRIMARY KEY,
                nct_id TEXT UNIQUE,
                title TEXT,
                condition TEXT,
                phase TEXT,
                status TEXT,
                enrollment INTEGER,
                ingestion_date TEXT
            )''',
            
            'mimic_patients': '''(
                id INTEGER PRIMARY KEY,
                patient_id TEXT UNIQUE,
                gender TEXT,
                age INTEGER,
                admission_type TEXT,
                mortality INTEGER,
                ingestion_date TEXT
            )''',
            
            'aact_trials': '''(
                id INTEGER PRIMARY KEY,
                nct_id TEXT UNIQUE,
                title TEXT,
                condition TEXT,
                phase TEXT,
                ingestion_date TEXT
            )''',
            
            'drugbank_formulations': '''(
                id INTEGER PRIMARY KEY,
                drug_id TEXT UNIQUE,
                drug_name TEXT,
                formulation_type TEXT,
                ingestion_date TEXT
            )''',
            
            'esol_solubility': '''(
                id INTEGER PRIMARY KEY,
                compound_id TEXT UNIQUE,
                smiles TEXT,
                solubility REAL,
                ingestion_date TEXT
            )''',
            
            'tox21_toxicity': '''(
                id INTEGER PRIMARY KEY,
                compound_id TEXT UNIQUE,
                smiles TEXT,
                assay_results TEXT,
                ingestion_date TEXT
            )''',
            
            'gras_excipients': '''(
                id INTEGER PRIMARY KEY,
                excipient_id TEXT UNIQUE,
                excipient_name TEXT,
                usage_category TEXT,
                ingestion_date TEXT
            )''',
        }
        
        for table_name, schema in tables.items():
            try:
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} {schema}")
            except Exception as e:
                logger.error(f"Error creating table {table_name}: {e}")
        
        conn.commit()
        conn.close()
        logger.info("✅ Enhanced database initialized")
    
    def batch_insert(self, table: str, records: List[Dict]) -> int:
        """Insert multiple records into a table"""
        if not records:
            return 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            inserted = 0
            for record in records:
                try:
                    columns = ', '.join(record.keys())
                    placeholders = ', '.join(['?' for _ in record])
                    values = tuple(record.values())
                    
                    cursor.execute(
                        f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})",
                        values
                    )
                    inserted += 1
                except sqlite3.IntegrityError:
                    continue
            
            conn.commit()
            conn.close()
            return inserted
        except Exception as e:
            logger.error(f"Batch insert error for {table}: {e}")
            return 0
    
    def log_ingestion(self, dataset_name: str, total_records: int, status: str, errors: str = ""):
        """Log ingestion event"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ingestion_log (dataset_name, total_records, ingestion_date, status, errors)
                VALUES (?, ?, ?, ?, ?)
            ''', (dataset_name, total_records, datetime.now().isoformat(), status, errors))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error logging ingestion: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """Get record counts for all tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'ingestion_log'")
            tables = [row[0] for row in cursor.fetchall()]
            
            stats = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            
            conn.close()
            return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}