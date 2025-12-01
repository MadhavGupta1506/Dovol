import smtplib
import ssl
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, timezone
from typing import Optional
from ..config import settings

def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def get_otp_expiration(minutes: int = 10) -> datetime:
    """Get OTP expiration time (default 10 minutes from now)"""
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)

async def send_otp_email(email: str, otp: str, user_name: str = "User") -> bool:
    """
    Send OTP email to user using SSL (port 465) - better for Render deployment
    Returns True if email sent successfully, False otherwise
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Dovol - Password Reset OTP"
        message["From"] = settings.smtp_from_email
        message["To"] = email

        # Create HTML email body
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4F46E5;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9fafb;
                    padding: 30px;
                    border: 1px solid #e5e7eb;
                }}
                .otp-box {{
                    background-color: white;
                    border: 2px dashed #4F46E5;
                    border-radius: 5px;
                    padding: 20px;
                    text-align: center;
                    margin: 20px 0;
                }}
                .otp-code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #4F46E5;
                    letter-spacing: 5px;
                }}
                .footer {{
                    background-color: #f3f4f6;
                    padding: 15px;
                    text-align: center;
                    font-size: 12px;
                    color: #6b7280;
                    border-radius: 0 0 5px 5px;
                }}
                .warning {{
                    color: #dc2626;
                    font-size: 14px;
                    margin-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hello {user_name},</p>
                    <p>We received a request to reset your password for your Dovol account.</p>
                    <p>Your One-Time Password (OTP) is:</p>
                    
                    <div class="otp-box">
                        <div class="otp-code">{otp}</div>
                    </div>
                    
                    <p><strong>This OTP will expire in 10 minutes.</strong></p>
                    
                    <p>If you didn't request this password reset, please ignore this email or contact support if you have concerns.</p>
                    
                    <p class="warning">⚠️ Never share this OTP with anyone. Dovol staff will never ask for your OTP.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 Dovol. All rights reserved.</p>
                    <p>This is an automated message, please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Create plain text version
        text = f"""
        Hello {user_name},

        We received a request to reset your password for your Dovol account.

        Your One-Time Password (OTP) is: {otp}

        This OTP will expire in 10 minutes.

        If you didn't request this password reset, please ignore this email or contact support if you have concerns.

        Never share this OTP with anyone. Dovol staff will never ask for your OTP.

        © 2025 Dovol. All rights reserved.
        """

        # Attach both versions
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)

        # Create SSL context
        context = ssl.create_default_context()
        
        # Use SSL on port 465 instead of STARTTLS on port 587
        smtp_port = 465 if settings.smtp_port == 587 else settings.smtp_port
        
        # Send email using SMTP_SSL
        with smtplib.SMTP_SSL(settings.smtp_host, smtp_port, context=context, timeout=30) as server:
            server.set_debuglevel(0)
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)

        return True

    except smtplib.SMTPException as e:
        print(f"SMTP Error sending email: {str(e)}")
        return False
    except ConnectionError as e:
        print(f"Connection Error sending email: {str(e)}")
        return False
    except TimeoutError as e:
        print(f"Timeout Error sending email: {str(e)}")
        return False
    except Exception as e:
        print(f"Error sending email: {type(e).__name__} - {str(e)}")
        return False

def is_otp_expired(expires_at: datetime) -> bool:
    """Check if OTP has expired"""
    return datetime.now(timezone.utc) > expires_at

async def send_signup_otp_email(email: str, otp: str) -> bool:
    """
    Send OTP email for signup verification using SSL (port 465) - better for Render deployment
    Returns True if email sent successfully, False otherwise
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Dovol - Email Verification OTP"
        message["From"] = settings.smtp_from_email
        message["To"] = email

        # Create HTML email body
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #10B981;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9fafb;
                    padding: 30px;
                    border: 1px solid #e5e7eb;
                }}
                .otp-box {{
                    background-color: white;
                    border: 2px dashed #10B981;
                    border-radius: 5px;
                    padding: 20px;
                    text-align: center;
                    margin: 20px 0;
                }}
                .otp-code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #10B981;
                    letter-spacing: 5px;
                }}
                .footer {{
                    background-color: #f3f4f6;
                    padding: 15px;
                    text-align: center;
                    font-size: 12px;
                    color: #6b7280;
                    border-radius: 0 0 5px 5px;
                }}
                .warning {{
                    color: #dc2626;
                    font-size: 14px;
                    margin-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome to Dovol!</h1>
                </div>
                <div class="content">
                    <p>Thank you for signing up with Dovol!</p>
                    <p>To complete your registration, please verify your email address with the following One-Time Password (OTP):</p>
                    
                    <div class="otp-box">
                        <div class="otp-code">{otp}</div>
                    </div>
                    
                    <p><strong>This OTP will expire in 10 minutes.</strong></p>
                    
                    <p>If you didn't create an account with Dovol, please ignore this email.</p>
                    
                    <p class="warning">⚠️ Never share this OTP with anyone. Dovol staff will never ask for your OTP.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 Dovol. All rights reserved.</p>
                    <p>This is an automated message, please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Create plain text version
        text = f"""
        Welcome to Dovol!

        Thank you for signing up with Dovol!

        To complete your registration, please verify your email address with the following One-Time Password (OTP):

        {otp}

        This OTP will expire in 10 minutes.

        If you didn't create an account with Dovol, please ignore this email.

        Never share this OTP with anyone. Dovol staff will never ask for your OTP.

        © 2025 Dovol. All rights reserved.
        """

        # Attach both versions
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)

        # Create SSL context
        context = ssl.create_default_context()
        
        # Use SSL on port 465 instead of STARTTLS on port 587
        smtp_port = 465 if settings.smtp_port == 587 else settings.smtp_port
        
        # Send email using SMTP_SSL
        with smtplib.SMTP_SSL(settings.smtp_host, smtp_port, context=context, timeout=30) as server:
            server.set_debuglevel(0)
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)

        return True

    except smtplib.SMTPException as e:
        print(f"SMTP Error sending signup OTP email: {str(e)}")
        return False
    except ConnectionError as e:
        print(f"Connection Error sending signup OTP email: {str(e)}")
        return False
    except TimeoutError as e:
        print(f"Timeout Error sending signup OTP email: {str(e)}")
        return False
    except Exception as e:
        print(f"Error sending signup OTP email: {type(e).__name__} - {str(e)}")
        return False
