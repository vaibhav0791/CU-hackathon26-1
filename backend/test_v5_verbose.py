import requests
import json

BASE_URL = "http://localhost:8001/api"

print("="*70)
print("🧪 TESTING V-5: Analytics Collection (VERBOSE)")
print("="*70)

try:
    # Test 1: Check if server is alive
    print("\n1️⃣ Checking if server is alive...")
    response = requests.get(f"{BASE_URL}/")
    print(f"✓ Server is alive: {response.status_code}")
    
    # Test 2: Analyze a drug
    print("\n2️⃣ Analyzing Aspirin...")
    payload = {
        "smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "drug_name": "Aspirin",
        "molecular_weight": 180.16
    }
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    print(f"✓ Analysis status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  - Drug: {data['drug_name']}")
        print(f"  - Cached: {data['cached']}")
    else:
        print(f"  - Error: {response.text}")
    
    # Test 3: Get analytics
    print("\n3️⃣ Getting analytics summary...")
    response = requests.get(f"{BASE_URL}/analytics/summary")
    print(f"✓ Analytics status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print(f"  - Error: {response.text}")
    
    print("\n" + "="*70)
    print("✅ TESTS COMPLETED!")
    print("="*70)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
