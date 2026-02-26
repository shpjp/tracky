#!/usr/bin/env python3
"""
API Test Script for JWT Authentication
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_api_registration():
    """Test user registration via API"""
    print("🧪 Testing API Registration...")
    
    test_user = {
        "username": "apiuser2",
        "email": "apiuser2@example.com",
        "password": "securepass123",
        "password_confirm": "securepass123",
        "first_name": "API",
        "last_name": "User"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register/",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Registration successful!")
            print(f"Access Token: {data.get('access')[:50]}...")
            print(f"Refresh Token: {data.get('refresh')[:50]}...")
            print(f"User: {data.get('user')}")
            return data.get('access'), data.get('refresh')
        else:
            print(f"❌ Registration failed: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None, None

def test_api_login():
    """Test user login via API"""
    print("\n🧪 Testing API Login...")
    
    login_data = {
        "email": "apiuser2@example.com",
        "password": "securepass123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            return data.get('access'), data.get('refresh')
        else:
            print(f"❌ Login failed: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None, None

def test_protected_endpoint(access_token):
    """Test accessing protected endpoint"""
    print("\n🔐 Testing Protected Endpoint...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard/stats/", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Protected endpoint accessible!")
            print(f"Data: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Protected endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_create_application(access_token):
    """Test creating an application"""
    print("\n📝 Testing Application Creation...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    application_data = {
        "company_name": "Test Company",
        "role": "Software Engineer",
        "location": "Remote",
        "status": "APPLIED",
        "applied_date": "2026-02-26",
        "notes": "Test application created via API"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/applications/",
            json=application_data,
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Application created successfully!")
            print(f"Application ID: {data.get('id')}")
            return data.get('id')
        else:
            print(f"❌ Application creation failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_token_refresh(refresh_token):
    """Test token refresh"""
    print("\n🔄 Testing Token Refresh...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/refresh/",
            json={"refresh": refresh_token},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Token refresh successful!")
            return data.get('access')
        else:
            print(f"❌ Token refresh failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def main():
    print("🚀 JWT API Test Suite")
    print("=" * 50)
    
    # Test 1: Registration
    access_token, refresh_token = test_api_registration()
    
    if not access_token:
        # Try login instead
        access_token, refresh_token = test_api_login()
        
        if not access_token:
            print("❌ Cannot proceed without valid tokens")
            return
    
    # Test 2: Protected endpoint
    test_protected_endpoint(access_token)
    
    # Test 3: Create application
    test_create_application(access_token)
    
    # Test 4: Token refresh
    if refresh_token:
        new_access_token = test_token_refresh(refresh_token)
        if new_access_token:
            # Test protected endpoint with new token
            print("\n🔐 Testing Protected Endpoint with Refreshed Token...")
            test_protected_endpoint(new_access_token)
    
    print("\n✨ API test suite completed!")

if __name__ == "__main__":
    main()