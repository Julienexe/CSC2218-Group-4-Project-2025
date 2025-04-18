import pytest
import requests
import time
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Test data
test_checking_account = None
test_savings_account = None

def debug_request(url, method="GET", data=None):
    """Helper function to debug API requests"""
    print(f"\n--- DEBUG {method} {url} ---")
    if method == "GET":
        response = requests.get(url)
    elif method == "POST":
        print(f"Request Body: {data}")
        response = requests.post(url, json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    try:
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response Body: {response.text}")
    print("--- END DEBUG ---\n")
    return response

def test_create_checking_account():
    """Test creating a checking account"""
    global test_checking_account
    
    # Arrange
    url = f"{BASE_URL}/accounts"
    data = {
        "account_type": "CHECKING",
        "initialDeposit": 500.0
    }
    
    # Act
    response = debug_request(url, method="POST", data=data)
    
    if response.status_code == 201:
        test_checking_account = response.json()
        
        # Assert
        assert test_checking_account["account_type"] == "CHECKING"
        assert test_checking_account["balance"] == 500.0
        assert test_checking_account["status"] == "active"
        assert "account_id" in test_checking_account
        assert "creation_date" in test_checking_account
    else:
        # Still fail the test, but provide more info
        pytest.fail(f"Expected status code 201, got {response.status_code}: {response.text}")

# Continue with other tests but add debugging to each...