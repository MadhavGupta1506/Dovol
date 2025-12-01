"""Test current SMTP configuration and OTP signup"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

print("=" * 60)
print("Current SMTP Configuration:")
print("=" * 60)
print(f"SMTP Host: {settings.smtp_host}")
print(f"SMTP Port: {settings.smtp_port}")
print(f"SMTP Username: {settings.smtp_username}")
print(f"SMTP Password: {'*' * len(settings.smtp_password) if settings.smtp_password else 'NOT SET'}")
print(f"SMTP From Email: {settings.smtp_from_email}")
print("=" * 60)

# Test with SSL
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_smtp_ssl():
    """Test SMTP with SSL on port 465"""
    try:
        print("\nTesting SMTP_SSL (Port 465)...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL(settings.smtp_host, 465, context=context, timeout=30) as server:
            print("✓ SSL Connection established")
            server.set_debuglevel(0)
            server.login(settings.smtp_username, settings.smtp_password)
            print("✓ Login successful")
            
            # Send test email
            message = MIMEMultipart()
            message["Subject"] = "Test - Dovol OTP"
            message["From"] = settings.smtp_from_email
            message["To"] = "gupta.madhav1506@gmail.com"
            message.attach(MIMEText("Test OTP: 123456", "plain"))
            
            server.send_message(message)
            print("✓ Test email sent successfully!")
        
        return True
    except Exception as e:
        print(f"✗ Error: {type(e).__name__} - {str(e)}")
        return False

def test_smtp_starttls():
    """Test SMTP with STARTTLS on port 587"""
    try:
        print("\nTesting SMTP with STARTTLS (Port 587)...")
        
        with smtplib.SMTP(settings.smtp_host, 587, timeout=30) as server:
            print("✓ Connection established")
            server.set_debuglevel(0)
            server.starttls()
            print("✓ STARTTLS successful")
            server.login(settings.smtp_username, settings.smtp_password)
            print("✓ Login successful")
            
            # Send test email
            message = MIMEMultipart()
            message["Subject"] = "Test - Dovol OTP"
            message["From"] = settings.smtp_from_email
            message["To"] = "gupta.madhav1506@gmail.com"
            message.attach(MIMEText("Test OTP: 654321", "plain"))
            
            server.send_message(message)
            print("✓ Test email sent successfully!")
        
        return True
    except Exception as e:
        print(f"✗ Error: {type(e).__name__} - {str(e)}")
        return False

if __name__ == "__main__":
    ssl_works = test_smtp_ssl()
    starttls_works = test_smtp_starttls()
    
    print("\n" + "=" * 60)
    print("Results:")
    print(f"  SSL (Port 465): {'✓ Working' if ssl_works else '✗ Failed'}")
    print(f"  STARTTLS (Port 587): {'✓ Working' if starttls_works else '✗ Failed'}")
    print("=" * 60)
    
    if ssl_works:
        print("\nRecommendation: Use port 465 (SSL) in your .env file")
    elif starttls_works:
        print("\nRecommendation: Use port 587 (STARTTLS) in your .env file")
    else:
        print("\nBoth methods failed. Consider using SendGrid or another email service.")
