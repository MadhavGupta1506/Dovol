# Fixing OTP Email on Render Deployment

## Problem

Render's free tier has restricted outbound network access, which can block SMTP connections on port 587.

Error: `[Errno 101] Network is unreachable`

## Solutions (Choose One)

### Solution 1: Use Gmail with SSL (Port 465) - RECOMMENDED

Port 465 (SMTP_SSL) often works better on Render than port 587 (STARTTLS).

**Steps:**

1. **Update your Render environment variables:**

   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=465
   SMTP_USERNAME=app.notenest@gmail.com
   SMTP_PASSWORD=ijdpsuombncozywh
   SMTP_FROM_EMAIL=app.notenest@gmail.com
   ```

2. **Use the SSL email service:**

   Replace imports in `app/routers/user.py`:

   ```python
   from ..services.email_service_ssl import generate_otp, get_otp_expiration, send_otp_email, send_signup_otp_email, is_otp_expired
   ```

3. **Redeploy on Render**

---

### Solution 2: Use SendGrid (Free & Reliable) - BEST FOR PRODUCTION

SendGrid offers 100 emails/day for free and works perfectly on Render.

**Steps:**

1. **Sign up for SendGrid:**

   - Go to https://sendgrid.com/
   - Create a free account
   - Verify your email and set up sender authentication

2. **Create an API Key:**

   - Go to Settings > API Keys
   - Click "Create API Key"
   - Give it a name (e.g., "Dovol Backend")
   - Choose "Full Access" or "Restricted Access" with Mail Send permissions
   - Copy the API key (you won't see it again!)

3. **Install SendGrid SDK:**

   ```bash
   pip install sendgrid
   pip freeze > requirements.txt
   ```

4. **Update environment variables on Render:**

   ```
   SENDGRID_API_KEY=your_sendgrid_api_key_here
   SENDGRID_FROM_EMAIL=app.notenest@gmail.com
   ```

5. **Create new email service** (`app/services/email_service_sendgrid.py`):

   ```python
   from sendgrid import SendGridAPIClient
   from sendgrid.helpers.mail import Mail
   import random
   from datetime import datetime, timedelta, timezone
   from ..config import settings

   def generate_otp() -> str:
       return str(random.randint(100000, 999999))

   def get_otp_expiration(minutes: int = 10) -> datetime:
       return datetime.now(timezone.utc) + timedelta(minutes=minutes)

   async def send_signup_otp_email(email: str, otp: str) -> bool:
       try:
           message = Mail(
               from_email=settings.sendgrid_from_email,
               to_emails=email,
               subject='Dovol - Email Verification OTP',
               html_content=f'''
               <h1>Welcome to Dovol!</h1>
               <p>Your OTP is: <strong style="font-size: 24px;">{otp}</strong></p>
               <p>This OTP will expire in 10 minutes.</p>
               '''
           )

           sg = SendGridAPIClient(settings.sendgrid_api_key)
           response = sg.send(message)
           return response.status_code == 202
       except Exception as e:
           print(f"SendGrid Error: {str(e)}")
           return False
   ```

6. **Update config.py:**
   ```python
   sendgrid_api_key: str = ""
   sendgrid_from_email: str = ""
   ```

---

### Solution 3: Upgrade Render Plan

Render's paid plans ($7/month) have unrestricted outbound access and port 587 will work.

---

### Solution 4: Use Resend (Modern Alternative)

Resend offers 100 emails/day free and is very developer-friendly.

**Steps:**

1. **Sign up:** https://resend.com/
2. **Get API Key:** From the dashboard
3. **Install:** `pip install resend`
4. **Set environment variable:** `RESEND_API_KEY=your_api_key`
5. **Use their simple API:**

   ```python
   import resend
   resend.api_key = settings.resend_api_key

   resend.Emails.send({
       "from": "onboarding@resend.dev",
       "to": email,
       "subject": "Dovol OTP",
       "html": f"Your OTP is: {otp}"
   })
   ```

---

## Quick Test on Render

Add this endpoint to test email functionality:

```python
@router.get("/test-email")
async def test_email():
    try:
        success = await send_signup_otp_email("gupta.madhav1506@gmail.com", "123456")
        return {"success": success, "message": "Check email service logs"}
    except Exception as e:
        return {"error": str(e)}
```

---

## Recommendation

**For development:** Use Gmail with SSL (Solution 1)
**For production:** Use SendGrid or Resend (Solutions 2 or 4)

The network unreachability on Render is a known limitation of free tier hosting. The best solution is to use a dedicated email service API rather than direct SMTP.
