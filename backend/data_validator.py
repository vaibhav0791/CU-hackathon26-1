class DataValidator:
    @staticmethod
    def validate_protein(protein):
        """Validate protein data before insertion"""
        errors = []
        
        # Check required fields
        if not protein.get('uniprot_id'):
            errors.append("Missing uniprot_id")
        
        # Check sequence length
        sequence = protein.get('sequence', '')
        if len(sequence) < 10:
            errors.append(f"Sequence too short: {len(sequence)} chars")
        
        # Check valid amino acids
        valid_aa = set('ACDEFGHIKLMNPQRSTVWY')
        if not all(c in valid_aa for c in sequence.upper()):
            errors.append(f"Invalid amino acids in sequence")
        
        if errors:
            return False, errors
        return True, []
    
    @staticmethod
    def validate_drug(drug):
        """Validate drug data"""
        errors = []
        
        if not drug.get('drug_name'):
            errors.append("Missing drug name")
        
        mol_weight = drug.get('molecular_weight')
        if mol_weight and mol_weight <= 0:
            errors.append(f"Invalid molecular weight: {mol_weight}")
        
        if errors:
            return False, errors
        return True, []