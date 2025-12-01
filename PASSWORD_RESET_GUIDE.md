# Password Reset with OTP - Implementation Guide

## Overview

Complete forgot password functionality with email-based OTP (One-Time Password) verification for Dovol backend.

## Features Implemented

✅ **3-Step Password Reset Flow**

1. Request OTP via email
2. Verify OTP code
3. Reset password with verified OTP

✅ **Security Features**

- 6-digit random OTP generation
- 10-minute OTP expiration
- One-time use OTPs
- Email verification required
- Secure password hashing
- No user enumeration (security best practice)

✅ **Email Service**

- Beautiful HTML email templates
- Plain text fallback
- Professional formatting
- Security warnings included

---

## Files Created

### 1. `/backend/app/models/password_reset.py`

Database model for storing OTP records:

- `email`: User's email address
- `otp_code`: 6-digit OTP
- `is_used`: Prevents OTP reuse
- `is_verified`: Tracks verification status
- `expires_at`: 10-minute expiration
- `created_at`, `used_at`: Timestamps

### 2. `/backend/app/services/email_service.py`

Email service for OTP delivery:

- `generate_otp()`: Creates 6-digit OTP
- `get_otp_expiration()`: Sets expiration time
- `send_otp_email()`: Sends HTML/plain text email
- `is_otp_expired()`: Checks expiration

### 3. `/backend/.env.example`

Example environment configuration with SMTP settings

---

## Files Modified

### 1. `/backend/app/schemas/user.py`

Added three new schemas:

- `ForgotPasswordRequest`: Request OTP
- `VerifyOTPRequest`: Verify OTP
- `ResetPasswordRequest`: Reset password

### 2. `/backend/app/routers/user.py`

Added three new endpoints:

- `POST /users/forgot-password`: Request OTP
- `POST /users/verify-otp`: Verify OTP
- `POST /users/reset-password`: Reset password

### 3. `/backend/app/config.py`

Added SMTP configuration settings:

- `smtp_host`, `smtp_port`
- `smtp_username`, `smtp_password`
- `smtp_from_email`

---

## API Endpoints

### 1. Request OTP

**POST** `/users/forgot-password`

Request an OTP to be sent to the user's email.

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Response:**

```json
{
  "message": "OTP has been sent to your email",
  "success": true,
  "expires_in_minutes": 10
}
```

**Notes:**

- Always returns success message (doesn't reveal if email exists)
- OTP expires in 10 minutes
- New OTP invalidates previous unused OTPs

---

### 2. Verify OTP

**POST** `/users/verify-otp`

Verify the OTP sent to email (optional step before reset).

**Request Body:**

```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Response:**

```json
{
  "message": "OTP verified successfully",
  "success": true,
  "verified": true
}
```

**Error Responses:**

- `400`: Invalid OTP
- `400`: OTP has expired

---

### 3. Reset Password

**POST** `/users/reset-password`

Reset password using verified OTP.

**Request Body:**

```json
{
  "email": "user@example.com",
  "otp": "123456",
  "new_password": "newSecurePassword123"
}
```

**Response:**

```json
{
  "message": "Password has been reset successfully",
  "success": true
}
```

**Error Responses:**

- `400`: Invalid or unverified OTP
- `400`: OTP has expired
- `404`: User not found

---

## Email Configuration

### Setup Gmail SMTP (Recommended for Development)

1. **Enable 2-Factor Authentication**

   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password**

   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password

3. **Update .env file**
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   SMTP_FROM_EMAIL=your-email@gmail.com
   ```

### Alternative SMTP Providers

**Outlook/Office365:**

```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

**SendGrid (Production Recommended):**

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

**Mailgun:**

```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=your-mailgun-username
SMTP_PASSWORD=your-mailgun-password
```

---

## Testing the Flow

### Using cURL

**Step 1: Request OTP**

```bash
curl -X POST "http://localhost:8000/users/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**Step 2: Check your email for OTP (e.g., 123456)**

**Step 3: Verify OTP (optional)**

```bash
curl -X POST "http://localhost:8000/users/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "otp": "123456"
  }'
```

**Step 4: Reset Password**

```bash
curl -X POST "http://localhost:8000/users/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "otp": "123456",
    "new_password": "myNewPassword123"
  }'
```

---

## Database Migration

After implementing this feature, you need to create the new table:

### Option 1: Automatic (if using create_all)

Just restart your server - the table will be created automatically:

```bash
uvicorn app.main:app --reload
```

### Option 2: Manual SQL (if needed)

```sql
CREATE TABLE password_reset_otps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_password_reset_email ON password_reset_otps(email);
CREATE INDEX idx_password_reset_otp ON password_reset_otps(otp_code);
```

---

## Security Best Practices

### Implemented:

✅ OTP expires in 10 minutes
✅ OTP can only be used once
✅ No user enumeration (same response for existing/non-existing emails)
✅ Passwords are hashed using bcrypt
✅ OTP verification before password reset
✅ Rate limiting should be added in production

### Recommended for Production:

- Add rate limiting (max 3 requests per email per hour)
- Implement CAPTCHA on forgot password form
- Add IP-based rate limiting
- Log all password reset attempts
- Send email notification when password is changed
- Consider SMS OTP as alternative

---

## Email Template

The OTP email includes:

- Professional HTML design
- Clear OTP display in large font
- Expiration warning (10 minutes)
- Security warning about sharing OTP
- Company branding (Dovol)
- Plain text fallback for email clients

---

## Frontend Integration

### Password Reset Flow (3 Pages)

**Page 1: Forgot Password**

```javascript
// Request OTP
const requestOTP = async (email) => {
  const response = await fetch("/users/forgot-password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  return response.json();
};
```

**Page 2: Verify OTP (Optional)**

```javascript
// Verify OTP
const verifyOTP = async (email, otp) => {
  const response = await fetch("/users/verify-otp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, otp }),
  });
  return response.json();
};
```

**Page 3: Reset Password**

```javascript
// Reset Password
const resetPassword = async (email, otp, newPassword) => {
  const response = await fetch("/users/reset-password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, otp, new_password: newPassword }),
  });
  return response.json();
};
```

---

## Troubleshooting

### Email not sending?

**Check 1: SMTP Configuration**

```python
# Test in Python console
from app.config import settings
print(f"SMTP Host: {settings.smtp_host}")
print(f"SMTP Port: {settings.smtp_port}")
print(f"SMTP User: {settings.smtp_username}")
print(f"From Email: {settings.smtp_from_email}")
```

**Check 2: Gmail App Password**

- Must be 16 characters (no spaces)
- 2FA must be enabled
- Regular password won't work

**Check 3: Firewall/Network**

- Ensure port 587 is not blocked
- Check if SMTP is allowed on your network

**Check 4: Error Logs**

- Check server console for error messages
- Email errors are printed to console

### OTP not working?

**Check 1: Expiration**

- OTP expires in 10 minutes
- Request a new OTP if expired

**Check 2: Case Sensitivity**

- OTP is case-sensitive (though typically numbers only)

**Check 3: Multiple Requests**

- Only the most recent OTP is valid
- Previous OTPs are invalidated

---

## Production Checklist

- [ ] Configure production SMTP service (SendGrid, Mailgun, etc.)
- [ ] Add rate limiting to prevent abuse
- [ ] Implement CAPTCHA on forgot password form
- [ ] Set up email delivery monitoring
- [ ] Add logging for password reset attempts
- [ ] Configure email templates with company branding
- [ ] Test email delivery across different providers
- [ ] Set up email bounce handling
- [ ] Implement notification emails for successful password changes
- [ ] Add analytics tracking for password reset funnel

---

## Testing Checklist

- [ ] Request OTP with valid email
- [ ] Request OTP with invalid email (should not reveal)
- [ ] Verify valid OTP
- [ ] Verify invalid OTP (should fail)
- [ ] Verify expired OTP (should fail)
- [ ] Reset password with valid verified OTP
- [ ] Reset password with unverified OTP (should fail)
- [ ] Try to reuse OTP (should fail)
- [ ] Check email delivery
- [ ] Test HTML and plain text email rendering
- [ ] Verify OTP expiration after 10 minutes
- [ ] Test multiple OTP requests (only latest should work)

---

**Status**: ✅ Complete and ready to use
**Last Updated**: November 23, 2025
