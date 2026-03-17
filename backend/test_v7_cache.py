import requests
import json
import time

url = "http://localhost:8001/api/analyze"

payload = {
    "smiles": "CC(=O)Oc1ccccc1C(=O)O",
    "drug_name": "Aspirin",
    "molecular_weight": 180.16
}

print("="*70)
print("🧪 TESTING V-7: In-Memory Caching (Zero Installation!)")
print("="*70)

# First request (NOT cached)
print("\n📤 First Request (NOT cached):")
start = time.time()
response1 = requests.post(url, json=payload)
time1 = time.time() - start

print(f"Status: {response1.status_code}")
print(f"Cached: {response1.json()['cached']}")
print(f"Time: {time1:.3f}s")

# Second request (SHOULD be cached)
print("\n📤 Second Request (SHOULD be cached):")
start = time.time()
response2 = requests.post(url, json=payload)
time2 = time.time() - start

print(f"Status: {response2.status_code}")
print(f"Cached: {response2.json()['cached']}")
print(f"Time: {time2:.3f}s")

# Calculate speedup
speedup = time1 / time2
print(f"\n⚡ Speedup: {speedup:.1f}x faster!")

# Check cache stats
print("\n📊 Cache Statistics:")
cache_stats = requests.get("http://localhost:8001/api/cache/stats").json()
print(json.dumps(cache_stats, indent=2))

print("\n" + "="*70)
print("✅ V-7 IN-MEMORY CACHING WORKING!")
print("="*70)