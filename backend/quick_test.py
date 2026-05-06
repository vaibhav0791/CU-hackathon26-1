# backend/quick_test.py
import requests
import json

BASE_URL = "http://localhost:8000/api"

print("\n" + "="*80)
print("🧪 QUICK API TEST - PHARMA-AI")
print("="*80 + "\n")

# Test 1: Get all drugs
print("1️⃣ Testing: GET /drugs")
try:
    r = requests.get(f"{BASE_URL}/drugs")
    print(f"✅ Status: {r.status_code}")
    print(f"   Drugs: {json.dumps(r.json(), indent=2)[:300]}...\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 2: Analyze a drug
print("2️⃣ Testing: POST /analyze")
try:
    r = requests.post(
        f"{BASE_URL}/analyze",
        json={
            "smiles": "CC(=O)Oc1ccccc1C(=O)O",
            "drug_name": "Aspirin",
            "molecular_weight": 180.16
        }
    )
    print(f"✅ Status: {r.status_code}")
    data = r.json()
    print(f"   Drug: {data.get('drug_name')}")
    print(f"   BCS Class: {data.get('bcs_class')}")
    print(f"   Solubility: {data.get('solubility_score')}")
    print(f"   Confidence: {data.get('confidence_score')}\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 3: Get cache stats
print("3️⃣ Testing: GET /cache/stats")
try:
    r = requests.get(f"{BASE_URL}/cache/stats")
    print(f"✅ Status: {r.status_code}")
    data = r.json()
    print(f"   Cache Hit Rate: {data.get('hit_rate')}%\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 4: Get ALL DATASETS (V-13)
print("4️⃣ Testing: GET /dataset/available (V-13 DATASETS)")
try:
    r = requests.get(f"{BASE_URL}/dataset/available")
    print(f"✅ Status: {r.status_code}")
    data = r.json()
    print(f"   Total Datasets: {data.get('total_datasets')}")
    print(f"   Total Records: {data.get('total_records')}")
    datasets = data.get('datasets', [])
    print(f"   Sample Datasets:")
    for ds in datasets[:5]:
        print(f"     - {ds.get('name')}: {ds.get('records')} records")
    print()
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 5: Get datasets info
print("5️⃣ Testing: GET /datasets/info")
try:
    r = requests.get(f"{BASE_URL}/datasets/info")
    print(f"✅ Status: {r.status_code}")
    data = r.json()
    for category, info in data.get('categories', {}).items():
        count = info.get('count', 0)
        print(f"   {category}: {count} datasets\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 6: Get individual dataset (ChEMBL)
print("6️⃣ Testing: GET /datasets/chembl")
try:
    r = requests.get(f"{BASE_URL}/datasets/chembl")
    print(f"✅ Status: {r.status_code}")
    data = r.json()
    print(f"   Dataset: {data.get('dataset')}")
    print(f"   URL: {data.get('url')}")
    print(f"   Records: {data.get('records')}\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 7: Get dashboard
print("7️⃣ Testing: GET /dashboard")
try:
    r = requests.get(f"{BASE_URL}/dashboard")
    print(f"✅ Status: {r.status_code}")
    data = r.json()
    print(f"   Application: {data.get('application')}")
    print(f"   Version: {data.get('version')}")
    print(f"   Status: {data.get('status_message')}\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

print("="*80)
print("✅ QUICK TEST COMPLETE!")
print("="*80 + "\n")