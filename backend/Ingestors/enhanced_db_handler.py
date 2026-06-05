# backend/ingestors/enhanced_db_handler.py
import sqlite3
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

class EnhancedDatabaseHandler:
    """Enhanced SQLite database handler with field mapping, dedup, and validation"""
    
    def __init__(self, db_path: str = "pharma_enhanced.db"):
        self.db_path = db_path
        self.quality_metrics = {
            "total_records_attempted": 0,
            "total_records_inserted": 0,
            "total_duplicates_skipped": 0,
            "total_validation_errors": 0,
            "total_null_values_found": 0,
        }
        self._init_db()
    
    # ==================== DATABASE INITIALIZATION ====================
    
    def _init_db(self):
        """Initialize database with all tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ingestion log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingestion_log (
                id INTEGER PRIMARY KEY,
                dataset_name TEXT,
                total_records_attempted INTEGER DEFAULT 0,
                total_records_inserted INTEGER DEFAULT 0,
                duplicates_skipped INTEGER DEFAULT 0,
                validation_errors INTEGER DEFAULT 0,
                null_values_found INTEGER DEFAULT 0,
                ingestion_date TEXT,
                status TEXT,
                errors TEXT,
                quality_score REAL DEFAULT 0
            )
        ''')
        
        # Duplicate tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS duplicate_log (
                id INTEGER PRIMARY KEY,
                table_name TEXT,
                unique_identifier TEXT,
                duplicate_count INTEGER,
                first_seen TEXT,
                last_seen TEXT
            )
        ''')
        
        # Data quality report table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_quality_report (
                id INTEGER PRIMARY KEY,
                table_name TEXT,
                total_records INTEGER,
                null_percentage REAL,
                validation_pass_rate REAL,
                duplicate_percentage REAL,
                report_date TEXT,
                quality_score REAL
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
                sequence TEXT,
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
                logger.error(f"❌ Error creating table {table_name}: {e}")
        
        conn.commit()
        conn.close()
        logger.info("✅ Enhanced database initialized with validation & dedup support")
    
    # ==================== DUPLICATE DETECTION ====================
    
    def check_duplicate(self, table: str, unique_field: str, value: Any) -> Tuple[bool, Optional[int]]:
        """Check if a record already exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f"SELECT id FROM {table} WHERE {unique_field} = ?", (value,))
            result = cursor.fetchone()
            conn.close()
            return (True, result[0]) if result else (False, None)
        except Exception as e:
            logger.error(f"❌ Error checking duplicate: {e}")
            return False, None
    
    def log_duplicate(self, table_name: str, unique_id: str, skip_logging: bool = False):
        """Log duplicate occurrence - skip if bulk inserting"""
        if skip_logging:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT COUNT(*) FROM duplicate_log WHERE table_name = ? AND unique_identifier = ?",
                (table_name, unique_id)
            )
            exists = cursor.fetchone()[0]
            
            if exists:
                cursor.execute(
                    "UPDATE duplicate_log SET duplicate_count = duplicate_count + 1, last_seen = ? WHERE table_name = ? AND unique_identifier = ?",
                    (datetime.now().isoformat(), table_name, unique_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO duplicate_log (table_name, unique_identifier, duplicate_count, first_seen, last_seen) VALUES (?, ?, ?, ?, ?)",
                    (table_name, unique_id, 1, datetime.now().isoformat(), datetime.now().isoformat())
                )
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"⚠️ Could not log duplicate: {e}")
    
    # ==================== FIELD MAPPING HELPERS ====================
    
    def _get_valid_columns(self, table: str) -> List[str]:
        """Get valid columns that exist in a specific table"""
        
        table_columns = {
            'chembl_bioactivity': [
                'compound_id', 'compound_name', 'smiles', 'target', 
                'activity_value', 'activity_type', 'ingestion_date'
            ],
            'string_interactions': [
                'interaction_id', 'protein_a', 'protein_b', 
                'combined_score', 'ingestion_date'
            ],
            'clinical_trials': [
                'nct_id', 'title', 'condition', 'phase', 
                'status', 'enrollment', 'ingestion_date'
            ],
            'drugbank_formulations': [
                'drug_id', 'drug_name', 'formulation_type', 'ingestion_date'
            ],
            'uniprot_sequences': [
                'uniprot_id', 'protein_name', 'gene_name', 'organism', 
                'sequence_length', 'sequence', 'ingestion_date'
            ],
            'pubchem_properties': [
                'cid', 'compound_name', 'smiles', 'molecular_weight', 
                'logp', 'tpsa', 'hbd', 'hba', 'ingestion_date'
            ],
            'pdb_structures': [
                'pdb_id', 'title', 'resolution', 'experimental_method', 'ingestion_date'
            ],
            'geo_expression': [
                'geo_id', 'title', 'organism', 'ingestion_date'
            ],
            'zinc15_compounds': [
                'zinc_id', 'compound_name', 'smiles', 'molecular_weight', 'price', 'ingestion_date'
            ],
            'qm9_properties': [
                'molecule_id', 'smiles', 'homo_energy', 'lumo_energy', 'gap_energy', 'ingestion_date'
            ],
            'mimic_patients': [
                'patient_id', 'gender', 'age', 'admission_type', 'mortality', 'ingestion_date'
            ],
            'aact_trials': [
                'nct_id', 'title', 'condition', 'phase', 'ingestion_date'
            ],
            'esol_solubility': [
                'compound_id', 'smiles', 'solubility', 'ingestion_date'
            ],
            'tox21_toxicity': [
                'compound_id', 'smiles', 'assay_results', 'ingestion_date'
            ],
            'gras_excipients': [
                'excipient_id', 'excipient_name', 'usage_category', 'ingestion_date'
            ],
        }
        
        return table_columns.get(table, [])
    
    def _map_fields_to_table(self, table: str, record: Dict) -> Dict:
        """
        Map incoming fields from fetchers to database table columns
        
        Example: 
            Input record: {'compound_id': 'X', 'drug_name': 'Aspirin'}
            Output: Maps these to the chembl_bioactivity table's expected columns
        """
        
        # Define field mappings: database_column -> [list of possible source fields]
        field_mapping = {
            'chembl_bioactivity': {
                'compound_id': ['compound_id', 'id', 'cid'],
                'compound_name': ['compound_name', 'drug_name', 'title', 'name'],
                'smiles': ['smiles'],
                'target': ['target', 'protein_name', 'gene_name'],
                'activity_value': ['activity_value', 'solubility_value', 'solubility', 'score'],
                'activity_type': ['activity_type', 'type']
            },
            
            'string_interactions': {
                'interaction_id': ['interaction_id', 'id', 'stringId'],
                'protein_a': ['protein_a', 'uniprot_id', 'pdb_id', 'geo_id', 'proteinA'],
                'protein_b': ['protein_b', 'protein_name', 'gene_name', 'title', 'proteinB'],
                'combined_score': ['combined_score', 'score']
            },
            
            'clinical_trials': {
                'nct_id': ['nct_id', 'id', 'patient_id'],
                'title': ['title', 'compound_name', 'drug_name', 'study_title'],
                'condition': ['condition', 'organism', 'disease_condition'],
                'phase': ['phase'],
                'status': ['status', 'overall_status'],
                'enrollment': ['enrollment', 'sample_count', 'record_count']
            },
            
            'drugbank_formulations': {
                'drug_id': ['drug_id', 'compound_id', 'excipient_id', 'id'],
                'drug_name': ['drug_name', 'compound_name', 'excipient_name', 'title'],
                'formulation_type': ['formulation_type', 'usage_category']
            },
            
            'uniprot_sequences': {
                'uniprot_id': ['uniprot_id', 'id', 'prot_id'],
                'protein_name': ['protein_name', 'compound_name', 'title'],
                'gene_name': ['gene_name', 'name'],
                'organism': ['organism'],
                'sequence_length': ['sequence_length', 'length'],
                'sequence': ['sequence']
            },
            
            'pubchem_properties': {
                'cid': ['cid', 'id', 'compound_id'],
                'compound_name': ['compound_name', 'name'],
                'smiles': ['smiles'],
                'molecular_weight': ['molecular_weight', 'mw'],
                'logp': ['logp'],
                'tpsa': ['tpsa'],
                'hbd': ['hbd', 'h_bond_donors'],
                'hba': ['hba', 'h_bond_acceptors']
            },
            
            'pdb_structures': {
                'pdb_id': ['pdb_id', 'id'],
                'title': ['title', 'compound_name'],
                'resolution': ['resolution'],
                'experimental_method': ['experimental_method', 'method']
            },
            
            'geo_expression': {
                'geo_id': ['geo_id', 'id'],
                'title': ['title', 'compound_name'],
                'organism': ['organism']
            },
        }
        
        # Get the mapping for this specific table
        if table not in field_mapping:
            logger.debug(f"⚠️ No field mapping for table {table}, using record as-is")
            return record
        
        mapping = field_mapping[table]
        mapped = {}
        
        # For each column the table expects
        for target_col, source_cols in mapping.items():
            # Try each possible source field name (in priority order)
            for source_col in source_cols:
                if source_col in record:
                    value = record[source_col]
                    # Only use non-empty values
                    if value not in [None, '', 'Unknown']:
                        mapped[target_col] = value
                        break
        
        return mapped if mapped else None
    
    def _filter_columns_for_insert(self, table: str, record: Dict) -> Dict:
        """
        Filter record to only include columns that exist in the table
        
        Example:
            Input: {'compound_id': 'X', 'fake_column': 'Y'}
            Output: {'compound_id': 'X'}  (fake_column removed)
        """
        
        valid_cols = self._get_valid_columns(table)
        
        # Keep only valid columns
        filtered = {
            col: record[col] for col in valid_cols 
            if col in record
        }
        
        return filtered
    
    # ==================== DATA VALIDATION ====================
    
    def validate_record(self, table: str, record: Dict) -> Tuple[bool, List[str]]:
        """Validate record - LENIENT mode"""
        errors = []
        
        if not record or len(record) == 0:
            errors.append("⚠️ Record is empty")
            return False, errors
        
        has_data = any(v is not None and v != "" for v in record.values())
        if not has_data:
            errors.append("⚠️ No valid data in record")
            return False, errors
        
        return True, []
    
    # ==================== BATCH INSERT WITH MAPPING & DEDUP ====================
    
    def batch_insert_with_validation(self, table: str, records: List[Dict], unique_field: str = None) -> Dict[str, int]:
        """
        Insert records with:
        1. Field mapping (convert incoming fields to table columns)
        2. Column filtering (keep only valid columns)
        3. Deduplication (using single connection to avoid locks)
        4. Validation
        """
        if not records:
            return {"inserted": 0, "duplicates": 0, "errors": 0}
        
        stats = {"inserted": 0, "duplicates": 0, "errors": 0}
        self.quality_metrics["total_records_attempted"] += len(records)
        
        try:
            # OPEN CONNECTION ONCE for all inserts to avoid database locks
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()
            
            for record in records:
                try:
                    # STEP 1: Map fields to table columns
                    mapped_record = self._map_fields_to_table(table, record)
                    
                    if not mapped_record:
                        stats["errors"] += 1
                        logger.debug(f"⚠️ Could not map fields for record in {table}")
                        continue
                    
                    # STEP 2: Filter to only valid columns
                    filtered_record = self._filter_columns_for_insert(table, mapped_record)
                    
                    if not filtered_record:
                        stats["errors"] += 1
                        logger.debug(f"⚠️ No valid columns after filtering for {table}")
                        continue
                    
                    # STEP 3: Check for duplicates (using SAME connection)
                    if unique_field and unique_field in filtered_record:
                        try:
                            cursor.execute(
                                f"SELECT id FROM {table} WHERE {unique_field} = ?", 
                                (filtered_record[unique_field],)
                            )
                            result = cursor.fetchone()
                            if result:
                                logger.debug(f"⏭️ [DUPLICATE] {table}.{unique_field} = {filtered_record[unique_field]}")
                                stats["duplicates"] += 1
                                self.quality_metrics["total_duplicates_skipped"] += 1
                                continue
                        except Exception as e:
                            logger.warning(f"⚠️ Duplicate check error: {e}")
                    
                    # STEP 4: Validate
                    is_valid, validation_errors = self.validate_record(table, filtered_record)
                    if not is_valid:
                        stats["errors"] += 1
                        logger.error(f"❌ [VALIDATION FAILED] {table}: {validation_errors}")
                        continue
                    
                    # STEP 5: Add metadata
                    if 'ingestion_date' not in filtered_record:
                        filtered_record['ingestion_date'] = datetime.now().isoformat()
                    
                    # STEP 6: Insert (using SAME connection)
                    columns = ', '.join(filtered_record.keys())
                    placeholders = ', '.join(['?' for _ in filtered_record])
                    values = tuple(filtered_record.values())
                    
                    cursor.execute(
                        f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})",
                        values
                    )
                    
                    stats["inserted"] += 1
                    self.quality_metrics["total_records_inserted"] += 1
                
                except sqlite3.IntegrityError:
                    stats["duplicates"] += 1
                    self.quality_metrics["total_duplicates_skipped"] += 1
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"❌ [INSERT ERROR] {table}: {e}")
            
            # COMMIT once at the end
            conn.commit()
            conn.close()
            
            logger.info(f"✅ [{table}] Inserted: {stats['inserted']}, Duplicates: {stats['duplicates']}, Errors: {stats['errors']}")
        
        except Exception as e:
            logger.error(f"❌ Batch insert error for {table}: {e}")
        
        return stats
    
    def batch_insert(self, table: str, records: List[Dict]) -> int:
        """Legacy wrapper for backward compatibility"""
        stats = self.batch_insert_with_validation(table, records)
        return stats["inserted"]
    
    # ==================== LOGGING & REPORTING ====================
    
    def log_ingestion(self, dataset_name: str, total_records: int, status: str, errors: str = ""):
        """Log ingestion event"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            quality_score = self._calculate_quality_score()
            
            cursor.execute('''
                INSERT INTO ingestion_log 
                (dataset_name, total_records_attempted, total_records_inserted, 
                 duplicates_skipped, validation_errors, null_values_found, 
                 ingestion_date, status, errors, quality_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dataset_name,
                self.quality_metrics["total_records_attempted"],
                self.quality_metrics["total_records_inserted"],
                self.quality_metrics["total_duplicates_skipped"],
                self.quality_metrics["total_validation_errors"],
                self.quality_metrics["total_null_values_found"],
                datetime.now().isoformat(),
                status,
                errors,
                quality_score
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Ingestion logged: {dataset_name} (Quality: {quality_score:.1f}/100)")
        except Exception as e:
            logger.warning(f"⚠️ Could not log ingestion: {e}")
    
    def _calculate_quality_score(self) -> float:
        """Calculate quality score based on insertion rate"""
        if self.quality_metrics["total_records_attempted"] == 0:
            return 0.0
        
        insert_rate = (self.quality_metrics["total_records_inserted"] / 
                      max(1, self.quality_metrics["total_records_attempted"])) * 100
        
        return min(100, max(0, insert_rate))
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '%log%'")
            tables = [row[0] for row in cursor.fetchall()]
            
            report = {
                "report_date": datetime.now().isoformat(),
                "overall_quality_score": self._calculate_quality_score(),
                "summary": self.quality_metrics,
                "data_tables": {}
            }
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total = cursor.fetchone()[0]
                report["data_tables"][table] = {"total_records": total}
            
            conn.close()
            return report
        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")
            return {}
    
    def print_quality_report(self):
        """Print quality report to console"""
        report = self.generate_quality_report()
        score = report.get("overall_quality_score", 0)
        
        print("\n" + "="*80)
        print("📊 DATA QUALITY REPORT")
        print("="*80)
        print(f"\n🎯 Overall Quality Score: {score:.1f}/100")
        print(f"\n📋 SUMMARY:")
        for key, value in report.get("summary", {}).items():
            print(f"  {key}: {value}")
        print("\n" + "="*80)
    
    def get_stats(self) -> Dict[str, int]:
        """Get table statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '%log%'")
            tables = [row[0] for row in cursor.fetchall()]
            
            stats = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            
            conn.close()
            return stats
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {}