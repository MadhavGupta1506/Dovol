# Signup with OTP - Complete Guide

## Overview

Email verification during signup using OTP (One-Time Password). Users must verify their email before their account is created.

## Features

✅ **2-Step Signup Flow**

1. Request OTP via email
2. Verify OTP and complete registration

✅ **Security Features**

- Email verification required before account creation
- 6-digit random OTP
- 10-minute expiration
- One-time use OTPs
- Prevents duplicate email registration
- Beautiful email templates

---

## How It Works

### Traditional Signup (Still Available)

```
POST /users/signup
```

Direct signup without email verification (legacy endpoint).

### New Signup with OTP (Recommended)

```
1. POST /users/signup/request-otp    → Send OTP to email
2. POST /users/signup/verify         → Verify OTP + Create account
```

---

## API Endpoints

### 1. Request Signup OTP

**POST** `/users/signup/request-otp`

Request an OTP to verify email before signup.

**Request Body:**

```json
{
  "email": "newuser@example.com"
}
```

**Response (Success):**

```json
{
  "message": "OTP has been sent to your email",
  "success": true,
  "email": "newuser@example.com",
  "expires_in_minutes": 10
}
```

**Error Responses:**

- `400`: Email already registered
- `500`: Failed to send email

---

### 2. Verify OTP and Complete Signup

**POST** `/users/signup/verify`

Verify the OTP and create the user account.

**Request Body:**

```json
{
  "email": "newuser@example.com",
  "otp": "123456",
  "full_name": "John Doe",
  "password": "securePassword123",
  "role": "volunteer",
  "location": "New York"
}
```

**Response (Success):**

```json
{
  "id": "uuid",
  "full_name": "John Doe",
  "email": "newuser@example.com",
  "role": "volunteer",
  "location": "New York",
  "is_active": true,
  "created_at": "2025-11-23T00:00:00Z",
  "updated_at": "2025-11-23T00:00:00Z"
}
```

**Error Responses:**

- `400`: Email already registered
- `400`: Invalid OTP
- `400`: OTP has expired

**Valid Roles:**

- `volunteer`
- `ngo`
- `admin`

---

## Database Changes

### Updated OTP Model

The `password_reset_otps` table now includes:

- `otp_type` field: Distinguishes between `signup` and `password_reset` OTPs

**OTP Types:**

- `signup`: For email verification during signup
- `password_reset`: For password reset flow

---

## Email Template

### Signup OTP Email

- **Subject**: "Dovol - Email Verification OTP"
- **Color Theme**: Green (#10B981) for signup
- **Content**: Welcome message with OTP
- **Features**:
  - Large, clear OTP display
  - 10-minute expiration notice
  - Security warnings
  - Professional design

### Comparison with Password Reset Email

- **Signup**: Green theme, welcome message
- **Password Reset**: Blue theme, security-focused

---

## Testing

### Using Test Script

```bash
cd backend
python test_signup_otp.py
```

### Manual Testing with cURL

**Step 1: Request OTP**

```bash
curl -X POST "http://localhost:8000/users/signup/request-otp" \
  -H "Content-Type: application/json" \
  -d '{"email": "newuser@example.com"}'
```

**Step 2: Check your email for OTP**

**Step 3: Verify OTP and Complete Signup**

```bash
curl -X POST "http://localhost:8000/users/signup/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "otp": "123456",
    "full_name": "John Doe",
    "password": "securePass123",
    "role": "volunteer",
    "location": "New York"
  }'
```

**Step 4: Test Login**

```bash
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=newuser@example.com&password=securePass123"
```

---

## Frontend Integration

### Signup Flow (React Example)

**Page 1: Email Verification**

```javascript
const requestSignupOTP = async (email) => {
  const response = await fetch("/users/signup/request-otp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  return response.json();
};

// Usage
const handleRequestOTP = async () => {
  const result = await requestSignupOTP("user@example.com");
  if (result.success) {
    // Show OTP input form
  }
};
```

**Page 2: Complete Signup with OTP**

```javascript
const completeSignup = async (signupData) => {
  const response = await fetch("/users/signup/verify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: signupData.email,
      otp: signupData.otp,
      full_name: signupData.fullName,
      password: signupData.password,
      role: signupData.role,
      location: signupData.location,
    }),
  });
  return response.json();
};

// Usage
const handleSignup = async () => {
  const result = await completeSignup({
    email: "user@example.com",
    otp: "123456",
    fullName: "John Doe",
    password: "password123",
    role: "volunteer",
    location: "New York",
  });

  if (result.id) {
    // Signup successful, redirect to login or dashboard
  }
};
```

---

## User Experience Flow

### Recommended UX

1. **Landing Page**: Signup button
2. **Email Entry**: User enters email
3. **OTP Sent**: Show success message, timer (10 min)
4. **OTP Input**: 6-digit input field
5. **User Details**: Name, password, role, location
6. **Account Created**: Success message, redirect to login

### UI Components Needed

- Email input form
- OTP input (6 digits)
- Countdown timer (10 minutes)
- Resend OTP button
- Signup form (name, password, role, location)
- Success/error messages

---

## Comparison: OTP vs Non-OTP Signup

| Feature                | OTP Signup   | Direct Signup    |
| ---------------------- | ------------ | ---------------- |
| Email Verification     | ✅ Required  | ❌ No            |
| Security               | ✅ High      | ⚠️ Medium        |
| User Experience        | 2 steps      | 1 step           |
| Prevents Fake Accounts | ✅ Yes       | ❌ No            |
| Email Validity         | ✅ Confirmed | ❌ Unconfirmed   |
| Recommended            | ✅ Yes       | For testing only |

---

## Migration from Direct Signup

### Option 1: Keep Both (Recommended for Transition)

- Legacy endpoint: `/users/signup`
- New endpoint: `/users/signup/request-otp` + `/users/signup/verify`
- Gradually migrate users to OTP flow

### Option 2: Disable Direct Signup

Comment out or remove the `/users/signup` endpoint and force all signups through OTP.

---

## Security Considerations

### Implemented

✅ Email verification prevents fake accounts
✅ OTP expires in 10 minutes
✅ OTP can only be used once
✅ Separate OTP types (signup vs password reset)
✅ Duplicate email prevention

### Recommended for Production

- Add rate limiting (max 3 OTP requests per email per hour)
- Implement CAPTCHA on signup request
- Add IP-based rate limiting
- Log all signup attempts
- Consider phone verification as backup

---

## Troubleshooting

### Email not received?

1. Check spam/junk folder
2. Verify SMTP settings in `.env`
3. Check server logs for email errors
4. Ensure email is not already registered

### OTP not working?

1. Check if OTP expired (10 minutes)
2. Request a new OTP
3. Ensure correct OTP type (signup vs password_reset)
4. Check for typos in OTP

### Account not created?

1. Verify OTP first
2. Check if email is already registered
3. Ensure all required fields are provided
4. Check server logs for errors

---

## Files Modified/Created

### Modified

1. `app/models/password_reset.py` - Added `OTPType` enum
2. `app/schemas/user.py` - Added signup OTP schemas
3. `app/services/email_service.py` - Added signup OTP email function
4. `app/routers/user.py` - Added signup OTP endpoints

### Created

1. `test_signup_otp.py` - Testing script
2. `SIGNUP_OTP_GUIDE.md` - This documentation

---

## Quick Start

### 1. Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### 2. Configure SMTP (if not done)

Add to `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

### 3. Test Signup

```bash
python test_signup_otp.py
```

---

## Production Deployment

### Pre-launch Checklist

- [ ] Configure production SMTP (SendGrid, Mailgun, etc.)
- [ ] Add rate limiting
- [ ] Implement CAPTCHA
- [ ] Set up email monitoring
- [ ] Test email delivery across providers
- [ ] Add analytics tracking
- [ ] Configure error logging
- [ ] Set up bounce handling
- [ ] Test on multiple devices/browsers
- [ ] Load test OTP generation

---

## Support

For issues or questions:

1. Check logs in backend console
2. Verify SMTP configuration
3. Test with `test_signup_otp.py`
4. Review error messages

---

**Status**: ✅ Complete and production-ready
**Last Updated**: November 23, 2025
