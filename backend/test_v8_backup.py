import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000/api"

print("=" * 70)
print("🧪 Testing V-8: Backup & Recovery")
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

# 1. Create full backup
print("\n1️⃣ Create full backup (compressed)...")
try:
    response = requests.post(f"{BASE_URL}/backup/create?backup_type=full&compress=true", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code} ✅")
        print(f"   Filename: {data.get('filename')}")
        print(f"   Size: {data.get('size_bytes')} bytes")
        print(f"   Compressed: {data.get('compressed')}")
        if data.get('compression_ratio'):
            print(f"   Compression ratio: {data.get('compression_ratio')}%")
    else:
        print(f"   Status: {response.status_code} ❌")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

time.sleep(0.5)

# 2. Create incremental backup
print("\n2️⃣ Create incremental backup...")
try:
    response = requests.post(f"{BASE_URL}/backup/create?backup_type=incremental", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code} ✅")
        print(f"   Filename: {data.get('filename')}")
        print(f"   Records backed up: {data.get('records_backed_up')}")
    else:
        print(f"   Status: {response.status_code} ❌")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

time.sleep(0.5)

# 3. List backups
print("\n3️⃣ List all backups...")
try:
    response = requests.get(f"{BASE_URL}/backup/list", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code} ✅")
        print(f"   Total backups: {data.get('total_backups')}")
        
        if data.get('backups'):
            print(f"   \n   Backups found:")
            for backup in data.get('backups')[:5]:  # Show first 5
                size_mb = backup.get('size_bytes', 0) / (1024 * 1024)
                print(f"      - {backup.get('filename')} ({size_mb:.2f} MB)")
    else:
        print(f"   Status: {response.status_code} ❌")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

time.sleep(0.5)

# 4. List full backups only
print("\n4️⃣ List full backups only...")
try:
    response = requests.get(f"{BASE_URL}/backup/list?backup_type=full", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code} ✅")
        print(f"   Full backups: {data.get('total_backups')}")
        
        if data.get('backups'):
            for backup in data.get('backups')[:3]:
                print(f"      - {backup.get('filename')}")
    else:
        print(f"   Status: {response.status_code} ❌")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

time.sleep(0.5)

# 5. List incremental backups only
print("\n5️⃣ List incremental backups only...")
try:
    response = requests.get(f"{BASE_URL}/backup/list?backup_type=incremental", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code} ✅")
        print(f"   Incremental backups: {data.get('total_backups')}")
        
        if data.get('backups'):
            for backup in data.get('backups')[:3]:
                print(f"      - {backup.get('filename')}")
    else:
        print(f"   Status: {response.status_code} ❌")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

time.sleep(0.5)

# 6. Get backup statistics
print("\n6️⃣ Get backup statistics...")
try:
    response = requests.get(f"{BASE_URL}/backup/stats", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code} ✅")
        print(f"   Total backups: {data.get('total_backups')}")
        print(f"   Full backups: {data.get('full_backups')}")
        print(f"   Incremental backups: {data.get('incremental_backups')}")
        print(f"   Total size: {data.get('total_size_mb')} MB")
        print(f"   Latest backup: {data.get('latest_backup')}")
        print(f"   Oldest backup: {data.get('oldest_backup')}")
    else:
        print(f"   Status: {response.status_code} ❌")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

time.sleep(0.5)

# 7. Validate latest backup
print("\n7️⃣ Validate latest backup...")
try:
    # First get list to find latest backup
    list_response = requests.get(f"{BASE_URL}/backup/list", timeout=5)
    if list_response.status_code == 200:
        backups = list_response.json().get('backups', [])
        if backups:
            latest_backup = backups[0].get('filename')
            print(f"   Validating: {latest_backup}")
            
            validate_response = requests.get(
                f"{BASE_URL}/backup/validate?backup_filename={latest_backup}",
                timeout=5
            )
            
            if validate_response.status_code == 200:
                data = validate_response.json()
                print(f"   Status: {validate_response.status_code} ✅")
                print(f"   Backup: {data.get('backup_file')}")
                print(f"   Valid: {data.get('valid')}")
                print(f"   Size: {data.get('size_mb')} MB")
            else:
                print(f"   Status: {validate_response.status_code} ❌")
        else:
            print(f"   ⚠️  No backups available to validate")
    else:
        print(f"   ❌ Failed to get backup list")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

time.sleep(0.5)

# 8. Cleanup old backups (30+ days)
print("\n8️⃣ Cleanup backups older than 30 days...")
try:
    response = requests.delete(f"{BASE_URL}/backup/cleanup?days=30", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code} ✅")
        print(f"   Deleted backups: {data.get('deleted_backups')}")
        print(f"   Freed space: {data.get('freed_space_mb')} MB")
    else:
        print(f"   Status: {response.status_code} ❌")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

time.sleep(0.5)

# 9. Create another full backup
print("\n9️⃣ Create another full backup (uncompressed)...")
try:
    response = requests.post(f"{BASE_URL}/backup/create?backup_type=full&compress=false", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code} ✅")
        print(f"   Filename: {data.get('filename')}")
        print(f"   Size: {data.get('size_bytes')} bytes")
        print(f"   Compressed: {data.get('compressed')}")
    else:
        print(f"   Status: {response.status_code} ❌")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

time.sleep(0.5)

# 10. Final statistics
print("\n🔟 Final backup statistics...")
try:
    response = requests.get(f"{BASE_URL}/backup/stats", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code} ✅")
        print(f"   \n   Summary:")
        print(f"      Total backups: {data.get('total_backups')}")
        print(f"      Full backups: {data.get('full_backups')}")
        print(f"      Incremental backups: {data.get('incremental_backups')}")
        print(f"      Total storage: {data.get('total_size_mb')} MB")
    else:
        print(f"   Status: {response.status_code} ❌")
except Exception as e:
    print(f"   ❌ ERROR: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
print("✅ V-8 BACKUP & RECOVERY TESTS COMPLETED!")
print("=" * 70)

print("\n" + "=" * 70)
print("📝 RESTORE FUNCTIONALITY")
print("=" * 70)
print("\n⚠️  WARNING: To restore a backup, use this command:")
print(f"   curl -X POST '{BASE_URL}/backup/restore?backup_filename=<filename>'")
print("\n   Example:")
print(f"   curl -X POST '{BASE_URL}/backup/restore?backup_filename=pharma_full_backup_20260321_103045.db.gz'")
print("\n   This will:")
print("      1. Create a safety backup of current database")
print("      2. Restore the selected backup")
print("      3. Return confirmation with safety backup location")

print("\n" + "=" * 70)
print("📊 SWAGGER UI")
print("=" * 70)
print("\n   Open your browser to: http://localhost:8000/docs")
print("   You can test all backup endpoints interactively!")

print("\n" + "=" * 70)