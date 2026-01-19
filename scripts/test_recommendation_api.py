"""
Test the medication recommendation API.
"""

import requests
import json
from pathlib import Path
import sys

# Test data
sample_patient = {
    "patient_info": {
        "age": 65,
        "sex": "M",
        "ejection_fraction": 0.35,  # HFrEF
        "systolic_bp": 140,
        "heart_rate": 85,
        "creatinine": 1.2,
        "diabetes": True,
        "high_blood_pressure": True
    },
    "current_medications": [],
    "time_horizon_days": 90
}

def test_api():
    """Test the recommendation API."""
    base_url = "http://localhost:8000"
    
    print("="*70)
    print("Testing Medication Recommendation API")
    print("="*70)
    
    # Test health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/recommendations/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.ConnectionError:
        print("   ✗ API server not running. Start with: uvicorn pdt.api.main:app --reload")
        return
    
    # Test medication recommendations
    print("\n2. Testing medication recommendations...")
    try:
        response = requests.post(
            f"{base_url}/recommendations/medications",
            json=sample_patient
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Recommendations received")
            print(f"   Top recommendation: {result['summary']['top_recommendation']['medication']}")
            print(f"   Optimal combination: {result['optimal_combination']['medications']}")
        else:
            print(f"   ✗ Error: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test scenario comparison
    print("\n3. Testing treatment scenario comparison...")
    comparison_request = {
        "patient_info": sample_patient["patient_info"],
        "scenarios": [
            {
                "medications": ["ace_inhibitor", "beta_blocker"],
                "dosages": {"ace_inhibitor": 1.0, "beta_blocker": 1.0}
            },
            {
                "medications": ["arni", "beta_blocker"],
                "dosages": {"arni": 1.0, "beta_blocker": 1.0}
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{base_url}/recommendations/compare-scenarios",
            json=comparison_request
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print(f"   ✓ Compared {len(results)} scenarios")
            for i, scenario in enumerate(results[:2]):
                print(f"   Scenario {i+1}: {scenario['medications']} - Benefit: {scenario['total_benefit']:.3f}")
        else:
            print(f"   ✗ Error: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "="*70)
    print("API Testing Complete")
    print("="*70)


if __name__ == "__main__":
    test_api()



