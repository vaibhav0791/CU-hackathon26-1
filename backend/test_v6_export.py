import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000/api"

print("=" * 70)
print("🧪 Testing V-6: Data Export API")
print("=" * 70)

# Check if server is running
print("\n🔍 Checking if server is running...")
try:
    response = requests.get(f"{BASE_URL}/", timeout=2)
    if response.status_code == 200:
        print("   ✅ Server is running!")
    else:
        print(f"   ❌ Server responded with status {response.status_code}")
        sys.exit(1)
except requests.exceptions.ConnectionError:
    print("   ❌ ERROR: Cannot connect to server!")
    print("   Please start the server with: python server.py")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")
    sys.exit(1)

# 1. Export analyses as JSON
print("\n1️⃣ Export analyses as JSON...")
try:
    response = requests.get(f"{BASE_URL}/export/analyses?format=json", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code} ✅")
        print(f"   Total records: {data.get('total_records')}")
        print(f"   Format: {data.get('format')}")
    else:
        print(f"   Status: {response.status_code} ❌")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

time.sleep(0.5)

# 2. Export analyses as CSV
print("\n2️⃣ Export analyses as CSV...")
try:
    response = requests.get(f"{BASE_URL}/export/analyses?format=csv", timeout=5)
    if response.status_code == 200:
        print(f"   Status: {response.status_code} ✅")
        print(f"   CSV preview (first 300 chars):")
        print(f"   {response.text[:300]}...")
    else:
        print(f"   Status: {response.status_code} ❌")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

time.sleep(0.5)

# 3. Export with filtering
print("\n3️⃣ Export with filtering (Aspirin only)...")
try:
    response = requests.get(f"{BASE_URL}/export/analyses?format=json&drug_name=Aspirin", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code} ✅")
        print(f"   Total records: {data.get('total_records')}")
        print(f"   Filtered by drug: Aspirin")
    else:
        print(f"   Status: {response.status_code} ❌")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

time.sleep(0.5)

# 4. Export analytics
print("\n4️⃣ Export analytics as JSON...")
try:
    response = requests.get(f"{BASE_URL}/export/analytics?format=json", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code} ✅")
        print(f"   Total records: {data.get('total_records')}")
    else:
        print(f"   Status: {response.status_code} ❌")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

time.sleep(0.5)

# 5. Export analytics as CSV
print("\n5️⃣ Export analytics as CSV...")
try:
    response = requests.get(f"{BASE_URL}/export/analytics?format=csv", timeout=5)
    if response.status_code == 200:
        print(f"   Status: {response.status_code} ✅")
        print(f"   CSV preview (first 300 chars):")
        print(f"   {response.text[:300]}...")
    else:
        print(f"   Status: {response.status_code} ❌")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

time.sleep(0.5)

# 6. Export summary
print("\n6️⃣ Export comprehensive summary...")
try:
    response = requests.get(f"{BASE_URL}/export/summary", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code} ✅")
        print(f"   Total analyses: {data.get('total_analyses')}")
        print(f"   Total analytics records: {data.get('total_analytics_records')}")
        
        analyses_summary = data.get('analyses_summary', {})
        print(f"   Avg confidence: {analyses_summary.get('avg_confidence')}")
        print(f"   Avg solubility: {analyses_summary.get('avg_solubility')}")
        print(f"   Drugs analyzed: {data.get('drugs_analyzed')}")
    else:
        print(f"   Status: {response.status_code} ❌")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

time.sleep(0.5)

# 7. Download as file
print("\n7️⃣ Download analyses as CSV file...")
try:
    response = requests.get(f"{BASE_URL}/export/analyses?format=csv&download=true", timeout=5)
    if response.status_code == 200:
        print(f"   Status: {response.status_code} ✅")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        print(f"   Content-Disposition: {response.headers.get('content-disposition')}")
        print(f"   File size: {len(response.content)} bytes")
    else:
        print(f"   Status: {response.status_code} ❌")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

time.sleep(0.5)

# 8. Export by BCS class
print("\n8️⃣ Export by BCS class (Class I only)...")
try:
    response = requests.get(f"{BASE_URL}/export/analyses?format=json&bcs_class=I", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code} ✅")
        print(f"   Total Class I drugs: {data.get('total_records')}")
    else:
        print(f"   Status: {response.status_code} ❌")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
print("✅ V-6 EXPORT API TESTS COMPLETED!")
print("=" * 70)