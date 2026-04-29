import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class DatasetDatabase:
    """SQLite database for storing all dataset records"""
    
    def __init__(self, db_path: str = "pharma_datasets.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._init_schema()
    
    def _init_schema(self):
        """Create all dataset tables"""
        
        # ChEMBL Bioactivity Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chembl_bioactivity (
                _id TEXT PRIMARY KEY,
                chembl_id TEXT UNIQUE NOT NULL,
                smiles TEXT NOT NULL,
                drug_name TEXT NOT NULL,
                target_name TEXT NOT NULL,
                bioactivity_type TEXT,
                bioactivity_value REAL,
                standard_units TEXT,
                assay_id TEXT,
                created_at TEXT
            )
        ''')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_chembl_smiles ON chembl_bioactivity(smiles)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_chembl_drug ON chembl_bioactivity(drug_name)')
        
        # PubChem Properties Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pubchem_properties (
                _id TEXT PRIMARY KEY,
                cid INTEGER UNIQUE NOT NULL,
                smiles TEXT NOT NULL,
                drug_name TEXT NOT NULL,
                molecular_weight REAL,
                log_p REAL,
                h_bond_donors INTEGER,
                h_bond_acceptors INTEGER,
                rotatable_bonds INTEGER,
                topological_psa REAL,
                created_at TEXT
            )
        ''')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_pubchem_smiles ON pubchem_properties(smiles)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_pubchem_cid ON pubchem_properties(cid)')
        
        # UniProt Sequences Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS uniprot_sequences (
                _id TEXT PRIMARY KEY,
                uniprot_id TEXT UNIQUE NOT NULL,
                protein_name TEXT NOT NULL,
                gene_name TEXT,
                organism TEXT,
                sequence TEXT,
                sequence_length INTEGER,
                function TEXT,
                created_at TEXT
            )
        ''')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_uniprot_id ON uniprot_sequences(uniprot_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_uniprot_protein ON uniprot_sequences(protein_name)')
        
        # PDB Structures Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pdb_structures (
                _id TEXT PRIMARY KEY,
                pdb_id TEXT UNIQUE NOT NULL,
                title TEXT,
                protein_name TEXT,
                resolution REAL,
                release_date TEXT,
                ligands TEXT,
                pdb_file_url TEXT,
                created_at TEXT
            )
        ''')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_pdb_id ON pdb_structures(pdb_id)')
        
        # Clinical Trials Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clinical_trials (
                _id TEXT PRIMARY KEY,
                nct_id TEXT UNIQUE NOT NULL,
                title TEXT,
                drug_name TEXT,
                condition TEXT,
                phase TEXT,
                status TEXT,
                enrollment INTEGER,
                start_date TEXT,
                primary_outcome TEXT,
                adverse_events TEXT,
                created_at TEXT
            )
        ''')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_trials_drug ON clinical_trials(drug_name)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_trials_status ON clinical_trials(status)')
        
        # Tox21 Toxicity Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tox21_toxicity (
                _id TEXT PRIMARY KEY,
                smiles TEXT NOT NULL,
                drug_name TEXT,
                assay_name TEXT,
                result TEXT,
                activity_score REAL,
                assay_description TEXT,
                created_at TEXT
            )
        ''')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_tox21_smiles ON tox21_toxicity(smiles)')
        
        # ESOL Solubility Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS esol_solubility (
                _id TEXT PRIMARY KEY,
                smiles TEXT UNIQUE NOT NULL,
                drug_name TEXT,
                solubility_score REAL,
                bcs_class TEXT,
                molecular_weight REAL,
                log_p REAL,
                created_at TEXT
            )
        ''')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_esol_smiles ON esol_solubility(smiles)')
        
        # GRAS Excipients Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS gras_excipients (
                _id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                fda_registry_number TEXT,
                cas_number TEXT,
                category TEXT,
                max_usage TEXT,
                compatible_with TEXT,
                created_at TEXT
            )
        ''')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_gras_name ON gras_excipients(name)')
        
        # Dataset Metadata Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS dataset_metadata (
                _id TEXT PRIMARY KEY,
                dataset_type TEXT UNIQUE,
                total_records INTEGER,
                last_updated TEXT,
                source_url TEXT,
                description TEXT,
                version TEXT
            )
        ''')
        
        self.conn.commit()
        logger.info("✅ Dataset schema initialized")
    
    def insert_record(self, table: str, data: Dict[str, Any]) -> bool:
        """Insert a record into a table"""
        try:
            cols = ", ".join(data.keys())
            placeholders = ", ".join(["?"] * len(data))
            self.cursor.execute(
                f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({placeholders})",
                tuple(data.values())
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Insert error: {e}")
            return False
    
    def query_by_smiles(self, table: str, smiles: str) -> Optional[Dict]:
        """Find record by SMILES"""
        try:
            self.cursor.execute(f"SELECT * FROM {table} WHERE smiles = ?", (smiles,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Query error: {e}")
            return None
    
    def get_table_count(self, table: str) -> int:
        """Get total records in a table"""
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            return self.cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"❌ Count error: {e}")
            return 0
    
    def close(self):
        """Close database connection"""
        self.conn.close()

dataset_db = DatasetDatabase("pharma_datasets.db")