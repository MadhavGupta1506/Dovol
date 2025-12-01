"""
Password Reset Testing Script for Dovol

This script helps test the forgot password flow with OTP.
Make sure your backend server is running and SMTP is configured.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"

def test_forgot_password(email):
    """Step 1: Request OTP"""
    print("\n" + "="*60)
    print("STEP 1: Request Password Reset OTP")
    print("="*60)
    
    url = f"{BASE_URL}/users/forgot-password"
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

def test_verify_otp(email, otp):
    """Step 2: Verify OTP"""
    print("\n" + "="*60)
    print("STEP 2: Verify OTP")
    print("="*60)
    
    url = f"{BASE_URL}/users/verify-otp"
    payload = {
        "email": email,
        "otp": otp
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ OTP Verified!")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"❌ Verification Failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_reset_password(email, otp, new_password):
    """Step 3: Reset Password"""
    print("\n" + "="*60)
    print("STEP 3: Reset Password")
    print("="*60)
    
    url = f"{BASE_URL}/users/reset-password"
    payload = {
        "email": email,
        "otp": otp,
        "new_password": new_password
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Password Reset Successful!")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"❌ Reset Failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_login(email, password):
    """Test login with new password"""
    print("\n" + "="*60)
    print("STEP 4: Test Login with New Password")
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
    print("DOVOL PASSWORD RESET TESTING")
    print("="*60)
    print("\n⚠️  Make sure:")
    print("  1. Backend server is running (http://localhost:8000)")
    print("  2. SMTP settings are configured in .env")
    print("  3. User account exists\n")
    
    # Get user input
    email = input("Enter email address: ").strip()
    
    if not email:
        print("❌ Email is required")
        return
    
    # Step 1: Request OTP
    if not test_forgot_password(email):
        print("\n❌ Failed to request OTP. Stopping test.")
        return
    
    # Wait for user to check email
    print("\n" + "="*60)
    otp = input("Enter the OTP from your email: ").strip()
    
    if not otp:
        print("❌ OTP is required")
        return
    
    # Step 2: Verify OTP (optional but recommended)
    verify = input("\nDo you want to verify OTP before reset? (y/n): ").strip().lower()
    if verify == 'y':
        if not test_verify_otp(email, otp):
            print("\n❌ OTP verification failed. Stopping test.")
            return
    
    # Step 3: Reset Password
    new_password = input("\nEnter new password: ").strip()
    
    if not new_password:
        print("❌ Password is required")
        return
    
    if not test_reset_password(email, otp, new_password):
        print("\n❌ Password reset failed.")
        return
    
    # Step 4: Test login with new password
    test_login_prompt = input("\nDo you want to test login with new password? (y/n): ").strip().lower()
    if test_login_prompt == 'y':
        test_login(email, new_password)
    
    print("\n" + "="*60)
    print("✅ PASSWORD RESET TESTING COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Testing cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
