import json
import asyncio
import httpx
import os
import time
import sqlite3
from datetime import datetime
from pathlib import Path

# ========== V-3 ENHANCED: PubChem Data Scraper with Retries & Caching ==========
class PubChemCache:
    """Simple in-memory cache for PubChem queries"""
    def __init__(self):
        self.cache = {}
        self.failed_cids = []

    def get(self, cid):
        return self.cache.get(cid)

    def set(self, cid, smiles):
        self.cache[cid] = smiles

    def mark_failed(self, cid):
        self.failed_cids.append(cid)

    def get_failed(self):
        return self.failed_cids


# Initialize cache
pubchem_cache = PubChemCache()


async def get_smiles_from_pubchem(cid: str, max_retries: int = 3) -> str:
    """
    Fetch SMILES from PubChem with:
    - Retry logic for failed requests
    - Rate limit handling (HTTP 429)
    - Caching to avoid redundant API calls
    - Timeout handling

    Args:
        cid: PubChem Compound ID
        max_retries: Number of retry attempts

    Returns:
        SMILES string or None if failed
    """

    # Check cache first
    cached_result = pubchem_cache.get(cid)
    if cached_result is not None:
        print(f"[CACHE HIT] CID {cid}")
        return cached_result

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/CanonicalSMILES/JSON"

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=15.0)

                # Success
                if response.status_code == 200:
                    smiles = response.json()["PropertyTable"]["Properties"][0]["CanonicalSMILES"]
                    pubchem_cache.set(cid, smiles)  # Cache it
                    print(f"[SUCCESS] Fetched SMILES for CID {cid} (Attempt {attempt + 1})")
                    return smiles

                # Rate limit - exponential backoff
                elif response.status_code in [429, 503]:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s...
                    print(f"[RATE LIMIT] HTTP {response.status_code}. Waiting {wait_time}s before retry... [CID {cid}]")
                    await asyncio.sleep(wait_time)
                    continue

                # Not found
                elif response.status_code == 404:
                    print(f"[NOT FOUND] CID {cid} not found in PubChem (404)")
                    pubchem_cache.mark_failed(cid)
                    return None

                # Other errors
                else:
                    print(f"[ERROR] Unexpected status {response.status_code} for CID {cid}")

        except asyncio.TimeoutError:
            print(f"[TIMEOUT] Attempt {attempt + 1} for CID {cid}")
            await asyncio.sleep(2 ** attempt)
            continue

        except httpx.ConnectError:
            print(f"[CONNECTION ERROR] Attempt {attempt + 1} for CID {cid}")
            await asyncio.sleep(2 ** attempt)
            continue

        except Exception as e:
            print(f"[ERROR] Attempt {attempt + 1} for CID {cid}: {type(e).__name__} - {e}")
            await asyncio.sleep(2 ** attempt)
            continue

    # All retries exhausted
    print(f"[FAILED] Failed to fetch SMILES for CID {cid} after {max_retries} attempts. Skipping.")
    pubchem_cache.mark_failed(cid)
    return None


async def validate_analysis_before_save(entry: dict) -> tuple:
    """
    V-4: Validates AI-returned JSON matches expected schema before SQLite save

    Returns:
        tuple: (is_valid: bool, error_message: str)
    """

    # 1. Check all required fields exist
    required_fields = ["drug_name", "smiles", "bcs_class"]
    for field in required_fields:
        if field not in entry or entry[field] is None:
            return False, f"Missing required field: {field}"

    # 2. Validate drug_name is not empty string
    if not entry.get("drug_name", "").strip():
        return False, "drug_name cannot be empty"

    # 3. Validate SMILES is not empty
    if not entry.get("smiles", "").strip():
        return False, f"SMILES cannot be empty for {entry.get('drug_name')}"

    # 4. Validate BCS class is one of: I, II, III, IV
    bcs_class = entry.get("bcs_class", "").strip().upper()
    if bcs_class not in ["I", "II", "III", "IV"]:
        return False, f"Invalid BCS class: {bcs_class}. Must be one of: I, II, III, IV"

        # 5. Validate solubility_score is between 0-100 (if provided and not None)
    if "solubility_score" in entry and entry["solubility_score"] is not None:
        try:
            solubility = float(entry["solubility_score"])
            if not (0 <= solubility <= 100):
                return False, f"solubility_score must be between 0-100, got {solubility}"
        except (ValueError, TypeError):
            return False, f"solubility_score must be a number, got {entry['solubility_score']}"

        # 6. Validate confidence_score is between 0-100 (if provided and not None)
    if "confidence_score" in entry and entry["confidence_score"] is not None:
        try:
            confidence = float(entry["confidence_score"])
            if not (0 <= confidence <= 100):
                return False, f"confidence_score must be between 0-100, got {confidence}"
        except (ValueError, TypeError):
            return False, f"confidence_score must be a number, got {entry['confidence_score']}"

    # 7. Basic SMILES validation - should have reasonable length and not be obviously malformed
    smiles = entry.get("smiles", "").strip()
    if len(smiles) < 1 or len(smiles) > 500:
        return False, f"SMILES length invalid (must be 1-500 chars) for {entry.get('drug_name')}"

    # All validations passed
    return True, "Validation passed"


async def clean_and_ingest():
    """Main data ingestion pipeline with V-3 & V-4 enhancements - SQLite Version"""
    
    # SQLITE CONNECTION (replaces MongoDB)
    db_path = os.path.join(os.path.dirname(__file__), "pharma.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ensure schema exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_blueprint (
            _id TEXT PRIMARY KEY,
            drug_name TEXT NOT NULL,
            smiles TEXT NOT NULL,
            bcs_class TEXT NOT NULL,
            category TEXT,              -- H-4: Therapeutic category tag
            solubility_score REAL,
            confidence_score REAL,
            molecular_weight REAL,
            dose_mg REAL,
            timestamp TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    conn.commit()

    # Path logic to make sure we find the file
    file_path = os.path.join(os.path.dirname(__file__), "drugs.json")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                print("[ERROR] drugs.json is empty! Please paste data into it.")
                return
            raw_data = json.loads(content)
            print(f"Processing {len(raw_data)} entries...\n")

        accepted_count = 0
        rejected_count = 0
        skipped_count = 0

        for entry in raw_data:
            try:
                d_name = entry.get('drug_name')
                d_smiles = entry.get('smiles')
                d_cid = entry.get('cid')

                # If SMILES is missing, try to fetch from PubChem
                if not d_smiles and d_cid:
                    print(f"[FETCH] SMILES missing for {d_name}. Fetching from PubChem...")
                    d_smiles = await get_smiles_from_pubchem(d_cid)

                if not d_smiles:
                    print(f"[SKIP] {d_name}: No SMILES found.")
                    skipped_count += 1
                    continue

                # Construct cleaned entry
                cleaned_entry = {
                    "drug_name": d_name,
                    "smiles": d_smiles,
                    "bcs_class": entry.get('bcs_class', 'Unknown').upper(),
                    "category": entry.get('category', 'Uncategorized'),  # H-4: Category tag
                    "solubility_score": entry.get('solubility_score'),
                    "confidence_score": entry.get('confidence_score', 100.0),
                    "molecular_weight": entry.get('molecular_weight'),
                    "dose_mg": entry.get('dose_mg'),
                    "timestamp": entry.get('timestamp', datetime.now().isoformat()),
                    "created_at": entry.get('created_at', datetime.now().isoformat()),
                    "updated_at": entry.get('updated_at', datetime.now().isoformat()),
                }

                # Validate before save (V-4)
                is_valid, validation_msg = await validate_analysis_before_save(cleaned_entry)
                if not is_valid:
                    print(f"[VALIDATION FAILED] {validation_msg}")
                    rejected_count += 1
                    continue

                # SAVE TO SQLite (replaces MongoDB)
                entry_id = str(entry.get('_id', f"{d_name}_{int(time.time())}"))
                
                cursor.execute('''
                    INSERT OR REPLACE INTO analysis_blueprint 
                    (_id, drug_name, smiles, bcs_class, category, solubility_score, confidence_score, 
                     molecular_weight, dose_mg, timestamp, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry_id,
                    cleaned_entry['drug_name'],
                    cleaned_entry['smiles'],
                    cleaned_entry['bcs_class'],
                    cleaned_entry['category'],  # H-4: Category tag
                    cleaned_entry['solubility_score'],
                    cleaned_entry['confidence_score'],
                    cleaned_entry['molecular_weight'],
                    cleaned_entry['dose_mg'],
                    cleaned_entry['timestamp'],
                    cleaned_entry['created_at'],
                    cleaned_entry['updated_at']
                ))
                conn.commit()

                print(f"[SAVED] {cleaned_entry['drug_name']} | BCS: {cleaned_entry['bcs_class']} | Confidence: {cleaned_entry['confidence_score']}%")
                accepted_count += 1

            except Exception as e:
                print(f"[ERROR PROCESSING] {e}")
                rejected_count += 1
                continue

        # Summary
        print(f"\n{'='*60}")
        print(f"INGESTION COMPLETE")
        print(f"{'='*60}")
        print(f"Accepted:  {accepted_count}")
        print(f"Rejected:  {rejected_count}")
        print(f"Skipped:   {skipped_count}")
        print(f"{'='*60}\n")

        conn.close()

    except FileNotFoundError:
        print(f"[ERROR] Could not find {file_path}")
        print("Please ensure 'drugs.json' exists in the backend folder.")
    except json.JSONDecodeError:
        print("[ERROR] drugs.json contains invalid JSON. Please fix the format.")
    except Exception as e:
        print(f"[FATAL ERROR] {e}")
    finally:
        if conn:
            conn.close()


# ========== ENTRY POINT ==========
if __name__ == "__main__":
    print("Starting PubChem Data Ingestion Pipeline (SQLite)...\n")
    asyncio.run(clean_and_ingest())