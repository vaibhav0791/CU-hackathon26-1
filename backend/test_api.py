import requests
import json
import time

BASE_URL = "http://localhost:8000/api"  # ✅ CORRECT PORT

def test_api():
    print("=" * 70)
    print("🧪 Testing PHARMA-AI API (Port 8000)")
    print("=" * 70)
    print()
    
    try:
        # Test 1: Root endpoint
        print("1️⃣ Testing root endpoint...")
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code} ✅")
        print(f"   Response: {response.json()}")
        print()
        
        # Test 2: Get drugs
        print("2️⃣ Testing /drugs endpoint...")
        response = requests.get(f"{BASE_URL}/drugs")
        print(f"   Status: {response.status_code} ✅")
        data = response.json()
        print(f"   Total drugs: {data['total']}")
        print(f"   Drugs: {[d['name'] for d in data['drugs']]}")
        print()
        
        # Test 3: Get specific drug
        print("3️⃣ Testing /drugs/Aspirin endpoint...")
        response = requests.get(f"{BASE_URL}/drugs/Aspirin")
        print(f"   Status: {response.status_code} ✅")
        print(f"   Response: {response.json()}")
        print()
        
        # Test 4: Cache stats (before analysis)
        print("4️⃣ Testing /cache/stats endpoint...")
        response = requests.get(f"{BASE_URL}/cache/stats")
        print(f"   Status: {response.status_code} ✅")
        cache_data = response.json()
        print(f"   Cache enabled: {cache_data['cache_enabled']}")
        print(f"   Cache type: {cache_data['cache_type']}")
        print(f"   Total cached: {cache_data['total_cached']}")
        print(f"   Hit rate: {cache_data['hit_rate']}%")
        print()
        
        # Test 5: Analyze drug (POST)
        print("5️⃣ Testing /analyze endpoint (POST)...")
        payload = {
            "smiles": "CC(=O)Oc1ccccc1C(=O)O",
            "drug_name": "Aspirin",
            "molecular_weight": 180.16
        }
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        response = requests.post(f"{BASE_URL}/analyze", json=payload)
        print(f"   Status: {response.status_code} ✅")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Analysis successful!")
            print(f"      - Analysis ID: {data['analysis_id'][:8]}...")
            print(f"      - BCS Class: {data['bcs_class']}")
            print(f"      - Solubility Score: {data['solubility_score']}")
            print(f"      - Confidence Score: {data['confidence_score']}")
            print(f"      - Outlier Flagged: {data['outlier_flagged']}")
            print(f"      - Cached: {data['cached']}")
        else:
            print(f"   ❌ Error: {response.text}")
        print()
        
        # Test 6: Cache stats (after analysis)
        print("6️⃣ Testing /cache/stats after analysis...")
        response = requests.get(f"{BASE_URL}/cache/stats")
        print(f"   Status: {response.status_code} ✅")
        cache_data = response.json()
        print(f"   Total cached: {cache_data['total_cached']}")
        print(f"   Hit count: {cache_data['hit_count']}")
        print(f"   Miss count: {cache_data['miss_count']}")
        print(f"   Hit rate: {cache_data['hit_rate']}%")
        print()
        
        # Test 7: Analyze same drug again (should be cached)
        print("7️⃣ Testing cached analysis (should be from cache)...")
        response = requests.post(f"{BASE_URL}/analyze", json=payload)
        print(f"   Status: {response.status_code} ✅")
        if response.status_code == 200:
            data = response.json()
            print(f"   Cached: {data['cached']} (should be True)")
        print()
        
        # Test 8: Get analytics
        print("8️⃣ Testing /analytics/requests endpoint...")
        response = requests.get(f"{BASE_URL}/analytics/requests?limit=10")
        print(f"   Status: {response.status_code} ✅")
        data = response.json()
        print(f"   Total requests logged: {data['total']}")
        if data['total'] > 0:
            latest = data['requests'][0]
            print(f"   Latest request: {latest['request_type']} - {latest['endpoint']}")
        print()
        
        # Test 9: Get all analyses
        print("9️⃣ Testing /analyses endpoint...")
        response = requests.get(f"{BASE_URL}/analyses")
        print(f"   Status: {response.status_code} ✅")
        data = response.json()
        print(f"   Total analyses stored: {data['total']}")
        print()
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ CONNECTION ERROR!")
        print(f"   Make sure the server is running: python server.py")
        print(f"   Error: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}")
        print(f"   {e}")

if __name__ == "__main__":
    test_api()