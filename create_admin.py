"""
Admin User Setup Script for Dovol

This script helps create an admin user for testing the admin dashboard.
Run this after starting your backend server.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"

def create_admin_user(full_name, email, password, location=None):
    """Create a new admin user"""
    url = f"{BASE_URL}/users/signup"
    
    payload = {
        "full_name": full_name,
        "email": email,
        "password": password,
        "role": "admin",
        "location": location
    }
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("✅ Admin user created successfully!")
            print(f"Email: {email}")
            print(f"Password: {password}")
            print(f"\nResponse: {json.dumps(response.json(), indent=2)}")
            return response.json()
        else:
            print(f"❌ Error creating admin user: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return None

def login_admin(email, password):
    """Login as admin and get token"""
    url = f"{BASE_URL}/users/login"
    
    # OAuth2PasswordRequestForm expects form data, not JSON
    payload = {
        "username": email,  # OAuth2 uses 'username' field for email
        "password": password
    }
    
    try:
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful!")
            print(f"Access Token: {token_data['access_token'][:50]}...")
            return token_data['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return None

def test_admin_dashboard(token):
    """Test admin dashboard stats endpoint"""
    url = f"{BASE_URL}/admin/dashboard/stats"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Dashboard stats retrieved successfully!")
            print(json.dumps(response.json(), indent=2))
            return response.json()
        else:
            print(f"❌ Error getting dashboard stats: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return None

def main():
    print("=" * 60)
    print("DOVOL ADMIN USER SETUP")
    print("=" * 60)
    print()
    
    # Get admin details from user
    print("Enter admin user details:")
    full_name = input("Full Name: ").strip() or "Admin User"
    email = input("Email: ").strip() or "admin@dovol.com"
    password = input("Password: ").strip() or "admin123"
    location = input("Location (optional): ").strip() or "Admin Office"
    
    print("\n" + "=" * 60)
    print("Creating admin user...")
    print("=" * 60)
    
    # Create admin user
    user = create_admin_user(full_name, email, password, location)
    
    if user:
        print("\n" + "=" * 60)
        print("Testing admin login...")
        print("=" * 60)
        
        # Login
        token = login_admin(email, password)
        
        if token:
            print("\n" + "=" * 60)
            print("Testing admin dashboard access...")
            print("=" * 60)
            
            # Test dashboard
            test_admin_dashboard(token)
            
            print("\n" + "=" * 60)
            print("SETUP COMPLETE!")
            print("=" * 60)
            print(f"\nAdmin Credentials:")
            print(f"  Email: {email}")
            print(f"  Password: {password}")
            print(f"\nYou can now use these credentials to access the admin dashboard.")
            print(f"\nSave your token for API testing:")
            print(f"  {token[:50]}...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
