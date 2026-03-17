print("Starting test...")

try:
    import requests
    print("✓ requests imported")
    
    url = "http://localhost:8001/api/"
    print(f"Connecting to {url}")
    
    response = requests.get(url, timeout=5)
    print(f"✓ Response: {response.status_code}")
    print(response.json())
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}")
    print(f"Message: {e}")
    import traceback
    traceback.print_exc()

print("Test finished")