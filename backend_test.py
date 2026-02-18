#!/usr/bin/env python3
import requests
import json
import sys
from datetime import datetime
import time

class PharmaAITester:
    def __init__(self):
        self.base_url = "https://pharma-ai-optimizer.preview.emergentagent.com/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.analysis_id = None

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=60):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        self.log(f"Testing {name}...")
        self.log(f"  URL: {method} {url}")
        
        try:
            start_time = time.time()
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            
            elapsed = time.time() - start_time
            
            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                self.log(f"  ✅ PASSED - Status: {response.status_code} (took {elapsed:.1f}s)")
                
                # Try to parse response
                try:
                    response_data = response.json()
                    if endpoint == "/analyze" and "id" in response_data:
                        self.analysis_id = response_data["id"]
                        self.log(f"  📝 Analysis ID saved: {self.analysis_id}")
                    return True, response_data
                except:
                    return True, {"status": "success", "raw_response": response.text}
            else:
                self.log(f"  ❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    self.log(f"  📄 Error response: {json.dumps(error_data, indent=2)[:500]}")
                except:
                    self.log(f"  📄 Raw error: {response.text[:200]}")
                return False, {}

        except requests.exceptions.Timeout:
            self.log(f"  ⏱️ TIMEOUT - Request took longer than {timeout}s")
            return False, {}
        except Exception as e:
            self.log(f"  ❌ EXCEPTION - {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test GET / for version info"""
        return self.run_test("Root API Endpoint", "GET", "/", 200)

    def test_get_drugs(self):
        """Test GET /drugs for 30 drugs"""
        success, response = self.run_test("Get All Drugs", "GET", "/drugs", 200)
        
        if success and isinstance(response, dict):
            drug_count = len(response.get("drugs", []))
            total_reported = response.get("total", 0)
            
            if drug_count == 30 and total_reported == 30:
                self.log(f"  ✅ Correct drug count: {drug_count} drugs found")
                return True
            else:
                self.log(f"  ❌ Expected 30 drugs, got {drug_count} (total: {total_reported})")
                return False
        
        return success

    def test_get_single_drug(self):
        """Test GET /drugs/{drug_name} for specific drug"""
        return self.run_test("Get Single Drug (Aspirin)", "GET", "/drugs/Aspirin", 200)

    def test_analyze_aspirin(self):
        """Test POST /analyze with Aspirin and 500mg dose"""
        analysis_data = {
            "drug_name": "Aspirin",
            "dose_mg": 500
        }
        
        # Use longer timeout since AI analysis takes 15-30 seconds
        success, response = self.run_test(
            "AI Analysis (Aspirin 500mg)", 
            "POST", 
            "/analyze", 
            200, 
            analysis_data, 
            timeout=60
        )
        
        if success and isinstance(response, dict):
            # Verify required analysis fields are present
            required_fields = ["id", "drug_name", "solubility", "excipients", "stability", "pk_compatibility"]
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                self.log(f"  ❌ Missing analysis fields: {missing_fields}")
                return False
            else:
                self.log(f"  ✅ All analysis panels present: {required_fields}")
                return True
        
        return success

    def test_get_analyses(self):
        """Test GET /analyses to retrieve saved analyses"""
        return self.run_test("Get All Analyses", "GET", "/analyses", 200)

    def test_get_specific_analysis(self):
        """Test GET /analyses/{id} to retrieve specific analysis"""
        if not self.analysis_id:
            self.log("  ⚠️ Skipping - No analysis ID available from previous test")
            return True
            
        return self.run_test(
            f"Get Specific Analysis ({self.analysis_id[:8]}...)", 
            "GET", 
            f"/analyses/{self.analysis_id}", 
            200
        )

    def test_invalid_drug(self):
        """Test POST /analyze with invalid drug name"""
        invalid_data = {
            "drug_name": "NonExistentDrug123",
            "dose_mg": 100
        }
        
        success, response = self.run_test(
            "Invalid Drug Analysis", 
            "POST", 
            "/analyze", 
            404, 
            invalid_data
        )
        
        return success

    def run_all_tests(self):
        """Run the complete test suite"""
        self.log("🧪 Starting PHARMA-AI Backend API Test Suite")
        self.log("=" * 60)
        
        test_methods = [
            self.test_root_endpoint,
            self.test_get_drugs,
            self.test_get_single_drug,
            self.test_analyze_aspirin,
            self.test_get_analyses,
            self.test_get_specific_analysis,
            self.test_invalid_drug
        ]
        
        for test_method in test_methods:
            try:
                test_method()
                # Brief pause between tests
                time.sleep(0.5)
            except Exception as e:
                self.log(f"Test {test_method.__name__} failed with exception: {e}", "ERROR")
        
        # Print summary
        self.log("=" * 60)
        self.log(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            self.log("🎉 ALL TESTS PASSED!")
            return 0
        else:
            self.log(f"❌ {self.tests_run - self.tests_passed} test(s) failed")
            return 1

def main():
    tester = PharmaAITester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()