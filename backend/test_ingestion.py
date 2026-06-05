# backend/test_ingestion.py
"""Quick test to verify ingestion pipeline works"""
import logging
from ingestors.enhanced_db_handler import EnhancedDatabaseHandler

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def test_basic_ingestion():
    """Test basic ingestion with sample data"""
    
    logger.info("🧪 Starting ingestion test...")
    
    # Initialize database
    db = EnhancedDatabaseHandler("test_pharma.db")
    
    # Test data 1: Valid records
    test_proteins = [
        {
            "uniprot_id": "P12345",
            "protein_name": "Test Protein 1",
            "gene_name": "TP1",
            "organism": "Homo sapiens",
            "sequence_length": 250,
            "sequence": "MVLSWVPTSMQ" + "A" * 240
        },
        {
            "uniprot_id": "P12346",
            "protein_name": "Test Protein 2",
            "gene_name": "TP2",
            "organism": "Homo sapiens",
            "sequence_length": 180,
            "sequence": "MVLSWVPTSMQ" + "A" * 170
        }
    ]
    
    # Test data 2: With duplicates (should be skipped)
    duplicate_proteins = [
        {
            "uniprot_id": "P12345",  # DUPLICATE - will be skipped
            "protein_name": "Test Protein 1",
            "gene_name": "TP1",
            "organism": "Homo sapiens",
            "sequence_length": 250,
            "sequence": "MVLSWVPTSMQ" + "A" * 240
        }
    ]
    
    # Test data 3: Invalid data (should fail validation)
    invalid_proteins = [
        {
            "uniprot_id": "P12347",
            "protein_name": "Test Protein 3",
            "gene_name": "TP3",
            "organism": "Homo sapiens",
            "sequence_length": 5,  # TOO SHORT - validation will fail
            "sequence": "MVLSW"
        }
    ]
    
    # Insert valid records
    logger.info("\n✅ TEST 1: Inserting valid records...")
    stats1 = db.batch_insert_with_validation(
        table="uniprot_sequences",
        records=test_proteins,
        unique_field="uniprot_id"
    )
    logger.info(f"Results: {stats1}")
    
    # Insert duplicate records (should be skipped)
    logger.info("\n✅ TEST 2: Inserting duplicate records (should be skipped)...")
    stats2 = db.batch_insert_with_validation(
        table="uniprot_sequences",
        records=duplicate_proteins,
        unique_field="uniprot_id"
    )
    logger.info(f"Results: {stats2}")
    
    # Insert invalid records (should fail validation)
    logger.info("\n✅ TEST 3: Inserting invalid records (should fail validation)...")
    stats3 = db.batch_insert_with_validation(
        table="uniprot_sequences",
        records=invalid_proteins,
        unique_field="uniprot_id"
    )
    logger.info(f"Results: {stats3}")
    
    # Log ingestion
    logger.info("\n✅ Logging ingestion event...")
    db.log_ingestion(
        dataset_name="test_proteins",
        total_records=len(test_proteins) + len(duplicate_proteins) + len(invalid_proteins),
        status="COMPLETED"
    )
    
    # Print quality report
    logger.info("\n")
    db.print_quality_report()
    
    logger.info("\n✅ Test completed!")

if __name__ == "__main__":
    test_basic_ingestion()