# -*- coding: utf-8 -*-
"""
H-3: SMILES Verification Script
Validates all SMILES strings in the drug database.
Checks: length, bracket matching, valid characters, and RDKit parsing.
Run: python verify_smiles.py
"""

import json
import os
import sys
# H-3: Fix Windows terminal emoji encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Try to import RDKit for advanced validation
try:
    from rdkit import Chem
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    print("[WARNING] RDKit not installed. Only basic validation will run.\n")


# ========== VALIDATION FUNCTIONS ==========

def check_length(smiles: str, drug_name: str) -> list:
    """Check SMILES length is between 1-500 characters"""
    errors = []
    if len(smiles) < 1:
        errors.append(f"  ❌ SMILES is empty")
    elif len(smiles) > 500:
        errors.append(f"  ❌ SMILES too long ({len(smiles)} chars, max 500)")
    else:
        errors.append(f"  ✅ Length OK ({len(smiles)} chars)")
    return errors


def check_brackets(smiles: str, drug_name: str) -> list:
    """Check that all brackets are properly matched: (), [], {}"""
    errors = []
    bracket_pairs = {'(': ')', '[': ']', '{': '}'}
    stack = []

    for i, char in enumerate(smiles):
        if char in bracket_pairs:
            stack.append((char, i))
        elif char in bracket_pairs.values():
            if not stack:
                errors.append(f"  ❌ Unmatched closing bracket '{char}' at position {i}")
                return errors
            open_bracket, _ = stack.pop()
            if bracket_pairs[open_bracket] != char:
                errors.append(f"  ❌ Mismatched bracket: '{open_bracket}' closed with '{char}' at position {i}")
                return errors

    if stack:
        for bracket, pos in stack:
            errors.append(f"  ❌ Unclosed bracket '{bracket}' at position {pos}")
    else:
        errors.append(f"  ✅ Brackets OK")

    return errors


def check_valid_chars(smiles: str, drug_name: str) -> list:
    """Check SMILES contains only valid characters"""
    errors = []
    # Valid SMILES characters: atoms, bonds, branches, rings, charges, stereo
    valid_chars = set("BCNOPSFIHKcnops" +          # Atoms (organic subset + aromatic)
                      "brclBrClAaZzEeDdGgMmTtUuVvWwXxYy" +  # Other atoms
                      "=#:-/\\." +                    # Bonds
                      "()[]{}@" +                     # Branches, rings, stereo
                      "0123456789%" +                 # Ring closures
                      "+- " +                         # Charges
                      "eE")                           # Scientific notation in extensions

    invalid_chars = []
    for i, char in enumerate(smiles):
        if char not in valid_chars:
            invalid_chars.append(f"'{char}' (pos {i})")

    if invalid_chars:
        errors.append(f"  ❌ Invalid characters: {', '.join(invalid_chars)}")
    else:
        errors.append(f"  ✅ Characters OK")

    return errors


def check_rdkit_parsing(smiles: str, drug_name: str) -> list:
    """Use RDKit to validate SMILES can be parsed into a molecule"""
    errors = []
    if not RDKIT_AVAILABLE:
        errors.append(f"  ⚠️  RDKit check skipped (not installed)")
        return errors

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        errors.append(f"  ❌ RDKit FAILED to parse SMILES (invalid structure)")
    else:
        num_atoms = mol.GetNumAtoms()
        errors.append(f"  ✅ RDKit OK ({num_atoms} atoms)")

    return errors


# ========== MAIN VERIFICATION ==========

def verify_drug_database():
    """Load drugs.json and validate every SMILES entry"""

    file_path = os.path.join(os.path.dirname(__file__), "drugs.json")

    if not os.path.exists(file_path):
        print(f"[ERROR] Could not find {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        drugs = json.load(f)

    print(f"{'='*60}")
    print(f"  H-3: SMILES VERIFICATION REPORT")
    print(f"  Total drugs to verify: {len(drugs)}")
    print(f"  RDKit available: {RDKIT_AVAILABLE}")
    print(f"{'='*60}\n")

    passed = 0
    failed = 0

    for drug in drugs:
        name = drug.get("drug_name", "UNKNOWN")
        smiles = drug.get("smiles", "")

        print(f"🔬 {name}")
        print(f"   SMILES: {smiles[:60]}{'...' if len(smiles) > 60 else ''}")

        all_results = []
        all_results.extend(check_length(smiles, name))
        all_results.extend(check_brackets(smiles, name))
        all_results.extend(check_valid_chars(smiles, name))
        all_results.extend(check_rdkit_parsing(smiles, name))

        for line in all_results:
            print(line)

        has_error = any("❌" in r for r in all_results)
        if has_error:
            failed += 1
            print(f"   ⛔ RESULT: FAILED\n")
        else:
            passed += 1
            print(f"   ✅ RESULT: PASSED\n")

    # Summary
    print(f"{'='*60}")
    print(f"  VERIFICATION SUMMARY")
    print(f"{'='*60}")
    print(f"  Total:  {len(drugs)}")
    print(f"  Passed: {passed} ✅")
    print(f"  Failed: {failed} ❌")
    print(f"{'='*60}")

    if failed > 0:
        print(f"\n  ⚠️  {failed} drug(s) have invalid SMILES. Please fix them!")
        sys.exit(1)
    else:
        print(f"\n  🎉 All SMILES are valid!")
        sys.exit(0)


# ========== ENTRY POINT ==========
if __name__ == "__main__":
    print("\nStarting SMILES Verification...\n")
    verify_drug_database()
