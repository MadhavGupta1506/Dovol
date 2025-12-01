# Quick Setup Guide for Password Reset

## Step 1: Configure Email Settings

You need to add SMTP configuration to your `.env` file:

```env
# Add these lines to your .env file
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

### For Gmail Users:

1. **Enable 2-Factor Authentication**

   - Visit: https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Create App Password**

   - Visit: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password (remove spaces)
   - Use this as `SMTP_PASSWORD` in .env

3. **Update .env**
   ```env
   SMTP_USERNAME=youremail@gmail.com
   SMTP_PASSWORD=abcdabcdabcdabcd  # 16-char app password
   SMTP_FROM_EMAIL=youremail@gmail.com
   ```

## Step 2: Start Backend Server

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

The server will automatically create the `password_reset_otps` table.

## Step 3: Test Password Reset

### Option A: Use Test Script

```powershell
python test_password_reset.py
```

### Option B: Manual Testing with cURL

**1. Request OTP:**

```powershell
curl -X POST "http://localhost:8000/users/forgot-password" `
  -H "Content-Type: application/json" `
  -d '{\"email\": \"user@example.com\"}'
```

**2. Check your email for OTP**

**3. Verify OTP (optional):**

```powershell
curl -X POST "http://localhost:8000/users/verify-otp" `
  -H "Content-Type: application/json" `
  -d '{\"email\": \"user@example.com\", \"otp\": \"123456\"}'
```

**4. Reset Password:**

```powershell
curl -X POST "http://localhost:8000/users/reset-password" `
  -H "Content-Type: application/json" `
  -d '{\"email\": \"user@example.com\", \"otp\": \"123456\", \"new_password\": \"newPass123\"}'
```

## Step 4: Integrate with Frontend

See `PASSWORD_RESET_GUIDE.md` for complete frontend integration examples.

## Troubleshooting

**Email not sending?**

- Check SMTP credentials in .env
- Verify 2FA is enabled and app password is correct
- Check server logs for error messages
- Ensure port 587 is not blocked

**OTP not working?**

- OTP expires in 10 minutes
- Only the latest OTP is valid
- OTP can only be used once

**Database errors?**

- Restart server to create the new table
- Check database connection

## What You Get

✅ 3-step password reset flow
✅ Email-based OTP (6 digits)
✅ 10-minute OTP expiration
✅ Beautiful HTML email templates
✅ Security features built-in
✅ Production-ready code

## API Endpoints

- `POST /users/forgot-password` - Request OTP
- `POST /users/verify-otp` - Verify OTP
- `POST /users/reset-password` - Reset password

See `PASSWORD_RESET_GUIDE.md` for full documentation.
