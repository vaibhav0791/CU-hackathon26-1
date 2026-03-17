import json
import asyncio
import httpx
import os
import time
import functools
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from database_schema import AnalysisBlueprint
from motor.motor_asyncio import AsyncIOMotorClient


# ─── V-3 ENHANCED: PubChem Data Scraper with Retries & Caching ─────────────────
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
    ✅ V-3 ENHANCED: Fetch SMILES from PubChem with:
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
        print(f"💾 Cache hit for CID {cid}")
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
                    print(f"✅ Fetched SMILES for CID {cid} (Attempt {attempt + 1})")
                    return smiles
                
                # Rate limit - exponential backoff
                elif response.status_code in [429, 503]:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s...
                    print(f"⚠️  PubChem rate limit (HTTP {response.status_code}). Waiting {wait_time}s before retry... [CID {cid}]")
                    await asyncio.sleep(wait_time)
                    continue
                
                # Not found
                elif response.status_code == 404:
                    print(f"❌ CID {cid} not found in PubChem (404)")
                    pubchem_cache.mark_failed(cid)
                    return None
                
                # Other errors
                else:
                    print(f"⚠️  Unexpected status {response.status_code} for CID {cid}")
                    
        except asyncio.TimeoutError:
            print(f"⏱️  Timeout on attempt {attempt + 1} for CID {cid}")
            await asyncio.sleep(2 ** attempt)
            continue
            
        except httpx.ConnectError:
            print(f"🔗 Connection error on attempt {attempt + 1} for CID {cid}")
            await asyncio.sleep(2 ** attempt)
            continue
            
        except Exception as e:
            print(f"❌ Error on attempt {attempt + 1} for CID {cid}: {type(e).__name__} - {e}")
            await asyncio.sleep(2 ** attempt)
            continue
    
    # All retries exhausted
    print(f"❌ Failed to fetch SMILES for CID {cid} after {max_retries} attempts. Skipping.")
    pubchem_cache.mark_failed(cid)
    return None


async def validate_analysis_before_save(entry: dict) -> tuple[bool, str]:
    """
    ✅ V-4: Validates AI-returned JSON matches expected schema before MongoDB save
    
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    
    # 1. Check all required fields exist
    required_fields = ["drug_name", "smiles", "bcs_class"]
    for field in required_fields:
        if field not in entry or entry[field] is None:
            return False, f"❌ Missing required field: {field}"
    
    # 2. Validate drug_name is not empty string
    if not entry.get("drug_name", "").strip():
        return False, "❌ drug_name cannot be empty"
    
    # 3. Validate SMILES is not empty
    if not entry.get("smiles", "").strip():
        return False, f"❌ SMILES cannot be empty for {entry.get('drug_name')}"
    
    # 4. Validate BCS class is one of: I, II, III, IV
    bcs_class = entry.get("bcs_class", "").strip().upper()
    if bcs_class not in ["I", "II", "III", "IV"]:
        return False, f"❌ Invalid BCS class: {bcs_class}. Must be one of: I, II, III, IV"
    
    # 5. Validate solubility_score is between 0-100 (if provided)
    if "solubility_score" in entry:
        try:
            solubility = float(entry["solubility_score"])
            if not (0 <= solubility <= 100):
                return False, f"❌ solubility_score must be between 0-100, got {solubility}"
        except (ValueError, TypeError):
            return False, f"❌ solubility_score must be a number, got {entry['solubility_score']}"
    
    # 6. Validate confidence_score is between 0-100 (if provided)
    if "confidence_score" in entry:
        try:
            confidence = float(entry["confidence_score"])
            if not (0 <= confidence <= 100):
                return False, f"❌ confidence_score must be between 0-100, got {confidence}"
        except (ValueError, TypeError):
            return False, f"❌ confidence_score must be a number, got {entry['confidence_score']}"
    
    # 7. Basic SMILES validation - should have reasonable length and not be obviously malformed
    smiles = entry.get("smiles", "").strip()
    if len(smiles) < 1 or len(smiles) > 500:
        return False, f"❌ SMILES length invalid (must be 1-500 chars) for {entry.get('drug_name')}"
    
    # ✅ All validations passed
    return True, "✅ Validation passed"


async def clean_and_ingest():
    """Main data ingestion pipeline with V-3 & V-4 enhancements"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(database=client.pharma_db, document_models=[AnalysisBlueprint])
    
    # Path logic to make sure we find the file
    file_path = os.path.join(os.path.dirname(__file__), "drugs.json")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                print("❌ ERROR: 'drugs.json' is empty! Please paste data into it.")
                return
            raw_data = json.loads(content)
            print(f"🔄 Processing {len(raw_data)} entries...\n")

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
                    print(f"🔍 SMILES missing for {d_name}. Fetching from PubChem...")
                    d_smiles = await get_smiles_from_pubchem(d_cid)

                if not d_smiles:
                    print(f"⚠️  Skipping {d_name}: No SMILES found.")
                    skipped_count += 1
                    continue

                # ─── V-4 VALIDATION: Check before saving ───────────────────────────
                prepared_entry = {
                    "drug_name": d_name,
                    "smiles": d_smiles,
                    "bcs_class": entry.get('bcs_class', 'I'),
                    "solubility_score": entry.get('solubility_score', 0.0),
                    "confidence_score": entry.get('confidence_score', 100.0)
                }
                
                is_valid, validation_message = await validate_analysis_before_save(prepared_entry)
                
                if not is_valid:
                    print(f"❌ REJECTED {d_name}: {validation_message}")
                    rejected_count += 1
                    continue
                
                # ─── If validation passed, save to database ───────────────────────
                clean_drug = AnalysisBlueprint(
                    drug_name=prepared_entry["drug_name"],
                    smiles=prepared_entry["smiles"],
                    bcs_class=prepared_entry["bcs_class"],
                    solubility_score=prepared_entry["solubility_score"],
                    confidence_score=prepared_entry["confidence_score"]
                )
                await clean_drug.insert()
                print(f"✅ Cleaned & Saved: {d_name} | BCS: {prepared_entry['bcs_class']} | Confidence: {prepared_entry['confidence_score']}%")
                accepted_count += 1

            except Exception as e:
                print(f"❌ ERROR processing {entry.get('drug_name', 'Unknown')}: {e}")
                rejected_count += 1
                continue

        print("\n" + "="*70)
        print(f"🏁 DATA INGESTION COMPLETE!")
        print(f"📊 SUMMARY:")
        print(f"   ✅ Accepted:  {accepted_count}")
        print(f"   ❌ Rejected:  {rejected_count}")
        print(f"   ⚠️  Skipped:   {skipped_count}")
        print(f"   📈 Total:     {len(raw_data)}")
        print("="*70)
        
        # ✅ V-3 ENHANCEMENT: Show cache stats
        print(f"\n📦 PubChem Cache Statistics:")
        print(f"   Cached requests: {len(pubchem_cache.cache)}")
        if pubchem_cache.get_failed():
            print(f"   Failed CIDs: {pubchem_cache.get_failed()}")

    except FileNotFoundError:
        print(f"❌ ERROR: File not found at {file_path}")
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in drugs.json: {e}")
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(clean_and_ingest())