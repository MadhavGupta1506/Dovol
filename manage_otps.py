"""
OTP Management Utility for Dovol

This script helps administrators manage OTPs in the database.
Run this to view, clear, or debug OTP records.
"""

import asyncio
from app.database import AsyncSessionLocal
from app.models.password_reset import PasswordResetOTP
from sqlalchemy.future import select
from datetime import datetime, timezone

async def list_all_otps():
    """List all OTPs in the database"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(PasswordResetOTP).order_by(PasswordResetOTP.created_at.desc())
        )
        otps = result.scalars().all()
        
        if not otps:
            print("No OTPs found in database")
            return
        
        print("\n" + "="*80)
        print(f"{'Email':<30} {'OTP':<8} {'Verified':<10} {'Used':<6} {'Expired':<8} {'Created'}")
        print("="*80)
        
        for otp in otps:
            is_expired = datetime.now(timezone.utc) > otp.expires_at
            print(f"{otp.email:<30} {otp.otp_code:<8} {str(otp.is_verified):<10} "
                  f"{str(otp.is_used):<6} {str(is_expired):<8} {otp.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("="*80)
        print(f"Total OTPs: {len(otps)}\n")

async def list_active_otps():
    """List only active (unused, not expired) OTPs"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(PasswordResetOTP)
            .where(PasswordResetOTP.is_used == False)
            .order_by(PasswordResetOTP.created_at.desc())
        )
        otps = result.scalars().all()
        
        active_otps = [otp for otp in otps if datetime.now(timezone.utc) <= otp.expires_at]
        
        if not active_otps:
            print("No active OTPs found")
            return
        
        print("\n" + "="*80)
        print("ACTIVE OTPs (Unused and Not Expired)")
        print("="*80)
        print(f"{'Email':<30} {'OTP':<8} {'Verified':<10} {'Expires At'}")
        print("="*80)
        
        for otp in active_otps:
            print(f"{otp.email:<30} {otp.otp_code:<8} {str(otp.is_verified):<10} "
                  f"{otp.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("="*80)
        print(f"Total Active OTPs: {len(active_otps)}\n")

async def clear_expired_otps():
    """Delete all expired OTPs"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PasswordResetOTP))
        otps = result.scalars().all()
        
        expired_otps = [otp for otp in otps if datetime.now(timezone.utc) > otp.expires_at]
        
        if not expired_otps:
            print("No expired OTPs to clear")
            return
        
        count = 0
        for otp in expired_otps:
            await db.delete(otp)
            count += 1
        
        await db.commit()
        print(f"✅ Deleted {count} expired OTP(s)")

async def clear_all_otps():
    """Delete ALL OTPs (use with caution!)"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PasswordResetOTP))
        otps = result.scalars().all()
        
        if not otps:
            print("No OTPs to clear")
            return
        
        count = len(otps)
        for otp in otps:
            await db.delete(otp)
        
        await db.commit()
        print(f"✅ Deleted {count} OTP(s)")

async def find_otp_by_email(email):
    """Find OTPs for a specific email"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(PasswordResetOTP)
            .where(PasswordResetOTP.email == email)
            .order_by(PasswordResetOTP.created_at.desc())
        )
        otps = result.scalars().all()
        
        if not otps:
            print(f"No OTPs found for {email}")
            return
        
        print("\n" + "="*80)
        print(f"OTPs for: {email}")
        print("="*80)
        print(f"{'OTP':<8} {'Verified':<10} {'Used':<6} {'Expired':<8} {'Created':<20} {'Expires'}")
        print("="*80)
        
        for otp in otps:
            is_expired = datetime.now(timezone.utc) > otp.expires_at
            print(f"{otp.otp_code:<8} {str(otp.is_verified):<10} {str(otp.is_used):<6} "
                  f"{str(is_expired):<8} {otp.created_at.strftime('%Y-%m-%d %H:%M'):<20} "
                  f"{otp.expires_at.strftime('%Y-%m-%d %H:%M')}")
        
        print("="*80)
        print(f"Total: {len(otps)}\n")

async def get_stats():
    """Get OTP statistics"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PasswordResetOTP))
        otps = result.scalars().all()
        
        total = len(otps)
        used = sum(1 for otp in otps if otp.is_used)
        unused = total - used
        verified = sum(1 for otp in otps if otp.is_verified)
        expired = sum(1 for otp in otps if datetime.now(timezone.utc) > otp.expires_at)
        active = sum(1 for otp in otps if not otp.is_used and datetime.now(timezone.utc) <= otp.expires_at)
        
        print("\n" + "="*50)
        print("OTP STATISTICS")
        print("="*50)
        print(f"Total OTPs:        {total}")
        print(f"Used:              {used}")
        print(f"Unused:            {unused}")
        print(f"Verified:          {verified}")
        print(f"Expired:           {expired}")
        print(f"Active (valid):    {active}")
        print("="*50 + "\n")

def main():
    print("="*60)
    print("DOVOL OTP MANAGEMENT UTILITY")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("  1. List all OTPs")
        print("  2. List active OTPs only")
        print("  3. Find OTPs by email")
        print("  4. View statistics")
        print("  5. Clear expired OTPs")
        print("  6. Clear ALL OTPs (careful!)")
        print("  0. Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            asyncio.run(list_all_otps())
        elif choice == "2":
            asyncio.run(list_active_otps())
        elif choice == "3":
            email = input("Enter email: ").strip()
            if email:
                asyncio.run(find_otp_by_email(email))
        elif choice == "4":
            asyncio.run(get_stats())
        elif choice == "5":
            confirm = input("Clear expired OTPs? (y/n): ").strip().lower()
            if confirm == 'y':
                asyncio.run(clear_expired_otps())
        elif choice == "6":
            confirm = input("⚠️  Clear ALL OTPs? This cannot be undone! (yes/no): ").strip().lower()
            if confirm == 'yes':
                asyncio.run(clear_all_otps())
        elif choice == "0":
            print("\nGoodbye!")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
