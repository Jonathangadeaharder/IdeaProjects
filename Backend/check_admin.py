#!/usr/bin/env python3
"""
Database verification script to check admin user status
"""
import asyncio
import sys
from pathlib import Path

# Add the Backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.database import AsyncSessionLocal
from core.auth import User
from sqlalchemy import select


async def check_admin_user():
    """Check if admin user exists and display details"""
    print("Checking admin user in database...")

    async with AsyncSessionLocal() as session:
        try:
            # Check for admin user by username
            result = await session.execute(
                select(User).where(User.username == "admin")
            )
            admin_user = result.scalar_one_or_none()

            if admin_user:
                print("FOUND: Admin user found!")
                print(f"  ID: {admin_user.id}")
                print(f"  Email: {admin_user.email}")
                print(f"  Username: {admin_user.username}")
                print(f"  Is Active: {admin_user.is_active}")
                print(f"  Is Superuser: {admin_user.is_superuser}")
                print(f"  Is Verified: {admin_user.is_verified}")
                print(f"  Created: {admin_user.created_at}")
                print(f"  Last Login: {admin_user.last_login}")
                return True
            else:
                print("NOT FOUND: Admin user not found!")

                # Check if any users exist
                result = await session.execute(select(User))
                all_users = result.scalars().all()
                print(f"Total users in database: {len(all_users)}")

                for user in all_users:
                    print(f"  - {user.username} ({user.email})")

                return False

        except Exception as e:
            print(f"Error checking database: {e}")
            return False


async def create_admin_if_missing():
    """Create admin user if it doesn't exist"""
    from core.database import create_default_admin_user

    print("Creating default admin user...")
    try:
        await create_default_admin_user()
        print("SUCCESS: Admin user creation completed")
        return True
    except Exception as e:
        print(f"ERROR: Error creating admin user: {e}")
        return False


async def main():
    """Main function"""
    print("LangPlug Database Admin User Checker")
    print("=" * 40)

    # Check if admin user exists
    admin_exists = await check_admin_user()

    if not admin_exists:
        print("\nAttempting to create admin user...")
        await create_admin_if_missing()

        print("\nRe-checking admin user after creation:")
        await check_admin_user()


if __name__ == "__main__":
    asyncio.run(main())