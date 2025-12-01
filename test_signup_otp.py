"""
Signup with OTP Testing Script for Dovol

This script helps test the new signup flow with email OTP verification.
Make sure your backend server is running and SMTP is configured.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"

def test_request_signup_otp(email):
    """Step 1: Request OTP for signup"""
    print("\n" + "="*60)
    print("STEP 1: Request Signup OTP")
    print("="*60)
    
    url = f"{BASE_URL}/users/signup/request-otp"
    payload = {"email": email}
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(json.dumps(result, indent=2))
            print(f"\n📧 Check {email} for the OTP code")
            print(f"⏰ OTP expires in {result.get('expires_in_minutes', 10)} minutes")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_verify_and_signup(email, otp, full_name, password, role, location=None):
    """Step 2: Verify OTP and complete signup"""
    print("\n" + "="*60)
    print("STEP 2: Verify OTP and Complete Signup")
    print("="*60)
    
    url = f"{BASE_URL}/users/signup/verify"
    payload = {
        "email": email,
        "otp": otp,
        "full_name": full_name,
        "password": password,
        "role": role,
        "location": location
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Signup Successful!")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"❌ Signup Failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_login(email, password):
    """Test login with new account"""
    print("\n" + "="*60)
    print("STEP 3: Test Login with New Account")
    print("="*60)
    
    url = f"{BASE_URL}/users/login"
    payload = {
        "username": email,
        "password": password
    }
    
    try:
        response = requests.post(url, data=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login Successful!")
            print(f"Token: {result.get('access_token', '')[:50]}...")
            return True
        else:
            print(f"❌ Login Failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    print("="*60)
    print("DOVOL SIGNUP WITH OTP TESTING")
    print("="*60)
    print("\n⚠️  Make sure:")
    print("  1. Backend server is running (http://localhost:8000)")
    print("  2. SMTP settings are configured in .env")
    print("  3. Email address is not already registered\n")
    
    # Get user input
    email = input("Enter email address: ").strip()
    if not email:
        print("❌ Email is required")
        return
    
    # Step 1: Request OTP
    if not test_request_signup_otp(email):
        print("\n❌ Failed to request OTP. Stopping test.")
        return
    
    # Wait for user to check email
    print("\n" + "="*60)
    otp = input("Enter the OTP from your email: ").strip()
    if not otp:
        print("❌ OTP is required")
        return
    
    # Get signup details
    print("\n" + "="*60)
    print("Enter your signup details:")
    full_name = input("Full Name: ").strip()
    password = input("Password: ").strip()
    
    print("\nSelect role:")
    print("  1. Volunteer")
    print("  2. NGO")
    role_choice = input("Enter choice (1 or 2): ").strip()
    
    if role_choice == "1":
        role = "volunteer"
    elif role_choice == "2":
        role = "ngo"
    else:
        print("❌ Invalid role choice")
        return
    
    location = input("Location (optional): ").strip() or None
    
    # Step 2: Verify OTP and complete signup
    if not test_verify_and_signup(email, otp, full_name, password, role, location):
        print("\n❌ Signup failed.")
        return
    
    # Step 3: Test login
    test_login_prompt = input("\nDo you want to test login? (y/n): ").strip().lower()
    if test_login_prompt == 'y':
        test_login(email, password)
    
    print("\n" + "="*60)
    print("✅ SIGNUP WITH OTP TESTING COMPLETE!")
    print("="*60)
    print(f"\nYour Account:")
    print(f"  Email: {email}")
    print(f"  Name: {full_name}")
    print(f"  Role: {role}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Testing cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
