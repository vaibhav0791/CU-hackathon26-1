import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

print("=" * 70)
print("🧪 Testing PHARMA-AI Analytics (V-5)")
print("=" * 70)

# 1. Analyze multiple drugs to generate analytics
print("\n1️⃣ Analyzing drugs to generate analytics...")
drugs = [
    {"smiles": "CC(=O)Oc1ccccc1C(=O)O", "drug_name": "Aspirin"},
    {"smiles": "CC1=C(C(C(=C(N1)COCCN)C2=CC=CC=C2Cl)C(=O)OC)C(=O)OCC", "drug_name": "Amlodipine"},
    {"smiles": "C1CC(N(C1)C(CCCCN)C(=O)NC(CCC2=CC=CC=C2)C(=O)O)C(=O)O", "drug_name": "Lisinopril"},
]

for drug in drugs:
    response = requests.post(f"{BASE_URL}/analyze", json=drug)
    if response.status_code == 200:
        print(f"   ✅ {drug['drug_name']} analyzed")
    else:
        print(f"   ❌ {drug['drug_name']} failed")

# 2. Get Analytics Requests
print("\n2️⃣ Testing /analytics/requests endpoint...")
response = requests.get(f"{BASE_URL}/analytics/requests")
if response.status_code == 200:
    data = response.json()
    print(f"   Status: {response.status_code} ✅")
    print(f"   Total requests logged: {data.get('total', 0)}")
    if data.get('requests'):
        latest = data['requests'][0]
        print(f"   Latest request: {latest.get('request_type')} - {latest.get('endpoint')}")
        print(f"   Response time: {latest.get('response_time_ms')}ms")
        print(f"   Status code: {latest.get('status_code')}")
        print(f"   Cached: {latest.get('was_cached')}")
else:
    print(f"   Status: {response.status_code} ❌")

# 3. Get Daily Analytics Summary
print("\n3️⃣ Testing /analytics/summary endpoint...")
response = requests.get(f"{BASE_URL}/analytics/summary")
if response.status_code == 200:
    data = response.json()
    print(f"   Status: {response.status_code} ✅")
    print(f"   Date: {data.get('date')}")
    print(f"   Total requests: {data.get('total_requests')}")
    print(f"   Total errors: {data.get('total_errors')}")
    print(f"   Total cache hits: {data.get('total_cache_hits')}")
    print(f"   Avg response time: {data.get('avg_response_time_ms')}ms")
    print(f"   Cache hit rate: {data.get('cache_hit_rate')}%")
    print(f"   Most analyzed drugs: {data.get('most_analyzed_drugs')}")
else:
    print(f"   Status: {response.status_code} ❌")

# 4. Get Daily Analytics
print("\n4️⃣ Testing /analytics/daily endpoint...")
response = requests.get(f"{BASE_URL}/analytics/daily")
if response.status_code == 200:
    data = response.json()
    print(f"   Status: {response.status_code} ✅")
    print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
else:
    print(f"   Status: {response.status_code} ❌")
    print(f"   Response: {response.text[:200]}")

# 5. Check Cache Stats
print("\n5️⃣ Testing /cache/stats endpoint...")
response = requests.get(f"{BASE_URL}/cache/stats")
if response.status_code == 200:
    data = response.json()
    print(f"   Status: {response.status_code} ✅")
    print(f"   Cache enabled: {data.get('cache_enabled')}")
    print(f"   Total cached: {data.get('total_cached')}")
    print(f"   Hit count: {data.get('hit_count')}")
    print(f"   Miss count: {data.get('miss_count')}")
    print(f"   Hit rate: {data.get('hit_rate')}%")
else:
    print(f"   Status: {response.status_code} ❌")

# 6. Check Analyses
print("\n6️⃣ Testing /analyses endpoint...")
response = requests.get(f"{BASE_URL}/analyses")
if response.status_code == 200:
    data = response.json()
    print(f"   Status: {response.status_code} ✅")
    print(f"   Total analyses stored: {data.get('total', 0)}")
    if data.get('analyses'):
        latest = data['analyses'][-1]
        print(f"   Latest analysis:")
        print(f"      - Drug: {latest.get('drug_name')}")
        print(f"      - BCS Class: {latest.get('bcs_class')}")
        print(f"      - Solubility: {latest.get('solubility_score')}")
        print(f"      - Confidence: {latest.get('confidence_score')}")
else:
    print(f"   Status: {response.status_code} ❌")

print("\n" + "=" * 70)
print("✅ ALL ANALYTICS TESTS COMPLETED!")
print("=" * 70)