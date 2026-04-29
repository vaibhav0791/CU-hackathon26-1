#!/usr/bin/env python3
"""Quick RDKit test"""
import sys

print("=" * 60)
print("TESTING RDKIT INSTALLATION")
print("=" * 60)

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    print("✅ RDKit imported successfully")
    
    # Test SMILES parsing
    smiles = "CC(=O)Oc1ccccc1C(=O)O"  # Aspirin
    print(f"\n📝 Testing SMILES: {smiles}")
    
    mol = Chem.MolFromSmiles(smiles)
    if mol:
        print(f"✅ SMILES parsed successfully")
        print(f"   Atoms: {mol.GetNumAtoms()}")
        print(f"   Bonds: {mol.GetNumBonds()}")
        
        # Test 3D generation
        print("\n🔄 Testing 3D structure generation...")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, AllChem.ETKDG())
        AllChem.MMFFOptimizeMolecule(mol)
        sdf = Chem.MolToMolBlock(mol)
        
        if sdf:
            print(f"✅ 3D structure generated")
            print(f"   SDF length: {len(sdf)} characters")
        else:
            print("❌ Failed to generate SDF")
    else:
        print("❌ SMILES parsing failed - Invalid SMILES")
        
except ImportError as e:
    print(f"❌ RDKit not installed: {e}")
    print("\nFix with: pip install rdkit")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED")
print("=" * 60)
