"""
Simple test script to verify the Barcode API is working correctly
"""
import requests
import json

# Configuration
API_BASE_URL = "http://localhost:5000"
TEST_BARCODE = "8906007289085"

def test_home_endpoint():
    """Test the home endpoint"""
    print("Testing Home Endpoint...")
    response = requests.get(f"{API_BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_health_check():
    """Test the health check endpoint"""
    print("Testing Health Check Endpoint...")
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_barcode_get():
    """Test GET barcode endpoint"""
    print(f"Testing GET /api/barcode/{TEST_BARCODE}...")
    response = requests.get(f"{API_BASE_URL}/api/barcode/{TEST_BARCODE}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_barcode_post():
    """Test POST barcode endpoint"""
    print(f"Testing POST /api/barcode with barcode {TEST_BARCODE}...")
    response = requests.post(
        f"{API_BASE_URL}/api/barcode",
        headers={'Content-Type': 'application/json'},
        json={'barcode': TEST_BARCODE}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_invalid_barcode():
    """Test with invalid barcode"""
    print("Testing with invalid barcode...")
    response = requests.get(f"{API_BASE_URL}/api/barcode/invalid123abc")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

if __name__ == "__main__":
    print("=" * 60)
    print("Barcode API Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_home_endpoint()
        test_health_check()
        test_barcode_get()
        test_barcode_post()
        test_invalid_barcode()
        
        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API server.")
        print(f"Make sure the server is running at {API_BASE_URL}")
    except Exception as e:
        print(f"ERROR: {str(e)}")

