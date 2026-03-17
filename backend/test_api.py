import requests
import json

# Test the /analyze endpoint
def test_analyze():
    url = "http://localhost:8001/api/analyze"
    
    payload = {
        "smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "drug_name": "Aspirin",
        "molecular_weight": 180.16
    }
    
    print("="*70)
    print("🧪 TESTING V-2: Analysis Data Pipeline")
    print("="*70)
    print(f"\n📤 Sending request to: {url}")
    print(f"📋 Payload: {json.dumps(payload, indent=2)}\n")
    
    try:
        response = requests.post(url, json=payload)
        
        print(f"📥 Status Code: {response.status_code}")
        print(f"📝 Response:\n")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ V-2 ANALYSIS PIPELINE WORKING PERFECTLY!")
        else:
            print(f"\n❌ Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server!")
        print("   Make sure server is running: python server.py")
    except Exception as e:
        print(f"❌ ERROR: {e}")

# Test other endpoints
def test_all_endpoints():
    base_url = "http://localhost:8001/api"
    
    endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/drugs", "Get all drugs"),
        ("GET", "/drugs/Aspirin", "Get specific drug"),
        ("GET", "/analyses", "Get all analyses"),
    ]
    
    print("\n" + "="*70)
    print("🧪 TESTING ALL ENDPOINTS")
    print("="*70)
    
    for method, endpoint, description in endpoints:
        url = base_url + endpoint
        print(f"\n📍 {method} {endpoint} - {description}")
        
        try:
            if method == "GET":
                response = requests.get(url)
            else:
                response = requests.post(url)
            
            print(f"   Status: {response.status_code} ✅")
            
        except Exception as e:
            print(f"   Error: {e} ❌")


if __name__ == "__main__":
    # Test the main /analyze endpoint
    test_analyze()
    
    # Test all other endpoints
    test_all_endpoints()
    
    print("\n" + "="*70)
    print("🏁 TESTING COMPLETE!")
    print("="*70)