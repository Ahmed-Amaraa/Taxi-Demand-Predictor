"""
Test script for API
Usage: python test_api.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.status_code == 200

def test_model_info():
    """Test model info endpoint"""
    print("Testing /model-info endpoint...")
    response = requests.get(f"{BASE_URL}/model-info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.status_code == 200

def test_predict():
    """Test prediction endpoint"""
    print("Testing /predict endpoint...")
    features = [0.5, 1.2, 0.3, 2.1, 0.8, 1.5, 0.9, 0.6, 1.1, 0.4]
    data = {"features": features}
    
    response = requests.post(f"{BASE_URL}/predict", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.status_code == 200

def test_batch_predict():
    """Test batch prediction endpoint"""
    print("Testing /batch-predict endpoint...")
    data = [
        {"features": [0.5, 1.2, 0.3, 2.1, 0.8, 1.5, 0.9, 0.6, 1.1, 0.4]},
        {"features": [0.6, 1.3, 0.4, 2.2, 0.9, 1.6, 1.0, 0.7, 1.2, 0.5]},
    ]
    
    response = requests.post(f"{BASE_URL}/batch-predict", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.status_code == 200

def main():
    print("=" * 60)
    print("API Testing Script")
    print("=" * 60)
    print(f"Testing API at: {BASE_URL}\n")
    
    try:
        results = {
            "Health": test_health(),
            "Model Info": test_model_info(),
            "Predict": test_predict(),
            "Batch Predict": test_batch_predict(),
        }
        
        print("=" * 60)
        print("Test Results:")
        print("=" * 60)
        for test_name, passed in results.items():
            status = "✓ PASSED" if passed else "✗ FAILED"
            print(f"{test_name}: {status}")
        
        all_passed = all(results.values())
        print("\n" + ("All tests passed! ✓" if all_passed else "Some tests failed! ✗"))
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API!")
        print("Make sure the FastAPI server is running: python src/api/main.py")

if __name__ == "__main__":
    main()
