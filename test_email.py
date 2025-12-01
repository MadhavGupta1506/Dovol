"""
Quick test script to verify SMTP credentials
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Test SMTP connection
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "app.notenest@gmail.com"
SMTP_PASSWORD = "ijdpsuombncozywh"  # App password without spaces
SMTP_FROM = "app.notenest@gmail.com"
TEST_TO = "gupta.madhav1506@gmail.com"

def test_smtp_connection():
    """Test SMTP connection and authentication"""
    try:
        print(f"Connecting to {SMTP_HOST}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            print("Starting TLS...")
            server.starttls()
            print(f"Logging in as {SMTP_USERNAME}...")
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            print("✓ Login successful!")
            
            # Send a test email
            message = MIMEMultipart()
            message["Subject"] = "Test Email - Dovol OTP System"
            message["From"] = SMTP_FROM
            message["To"] = TEST_TO
            
            body = "This is a test email to verify SMTP credentials are working correctly."
            message.attach(MIMEText(body, "plain"))
            
            print(f"Sending test email to {TEST_TO}...")
            server.send_message(message)
            print("✓ Test email sent successfully!")
            
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("SMTP Configuration Test")
    print("=" * 60)
    success = test_smtp_connection()
    print("=" * 60)
    if success:
        print("✓ All tests passed! SMTP is configured correctly.")
    else:
        print("✗ SMTP configuration failed. Please check:")
        print("  1. App Password is correct (no spaces)")
        print("  2. 2-Step Verification is enabled on Gmail")
        print("  3. App Password is generated for 'Mail' application")
    print("=" * 60)
