#!/usr/bin/env python3
"""
Test script for JWT authentication system
Run this after setting up the database and migrations
"""

import os
import sys
import django
import requests
import json
from django.conf import settings

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'placement_tracker_project.settings')
django.setup()

from tracker_app.models import CustomUser


def test_user_creation():
    """Test creating a user with bcrypt password hashing"""
    print("🧪 Testing user creation with bcrypt...")
    
    # Create test user
    email = "testuser@example.com"
    username = "testuser"
    password = "securepassword123"
    
    # Delete existing test user if exists
    CustomUser.objects.filter(email=email).delete()
    
    user = CustomUser.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name="Test",
        last_name="User"
    )
    
    print(f"✅ User created: {user.email}")
    
    # Test password verification
    if user.check_password(password):
        print("✅ Password verification successful")
    else:
        print("❌ Password verification failed")
        return False
    
    # Test wrong password
    if not user.check_password("wrongpassword"):
        print("✅ Wrong password correctly rejected")
    else:
        print("❌ Wrong password incorrectly accepted")
        return False
    
    return True


def test_api_endpoints():
    """Test API endpoints if Django server is running"""
    print("\n🌐 Testing API endpoints...")
    base_url = "http://localhost:8000"
    
    # Test data
    test_user = {
        "username": "apitest",
        "email": "apitest@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "API",
        "last_name": "Test"
    }
    
    try:
        # Test registration
        print("📝 Testing user registration...")
        response = requests.post(
            f"{base_url}/api/auth/register/",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Registration successful")
            access_token = data.get('access')
            refresh_token = data.get('refresh')
            
            # Test protected endpoint
            print("🔐 Testing protected endpoint...")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{base_url}/api/dashboard/stats/", headers=headers)
            if response.status_code == 200:
                print("✅ Protected endpoint accessible with token")
            else:
                print(f"❌ Protected endpoint failed: {response.status_code}")
            
            # Test token refresh
            print("🔄 Testing token refresh...")
            response = requests.post(
                f"{base_url}/api/auth/refresh/",
                json={"refresh": refresh_token},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print("✅ Token refresh successful")
            else:
                print(f"❌ Token refresh failed: {response.status_code}")
                
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Django server not running. Start with: python manage.py runserver")
        print("   Then run this test script again to test API endpoints.")
        return False
    except Exception as e:
        print(f"❌ API test error: {str(e)}")
        return False
    
    return True


def main():
    print("🚀 JWT Authentication Test Suite")
    print("=" * 50)
    
    # Test 1: User creation and password hashing
    if not test_user_creation():
        print("❌ User creation tests failed")
        return
    
    # Test 2: API endpoints (if server is running)
    test_api_endpoints()
    
    print("\n✨ Test suite completed!")
    print("\n📋 Next steps:")
    print("1. Set up your Neon DB connection in .env file")
    print("2. Run: python manage.py migrate")
    print("3. Run: python manage.py runserver")
    print("4. Test API endpoints at http://localhost:8000/api/")


if __name__ == "__main__":
    main()