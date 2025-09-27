"""
Reset the test user password for testing
"""

from database.models import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Create database connection
engine = create_engine(settings.get_database_url())
Session = sessionmaker(bind=engine)
session = Session()

# Find the test user
user = session.query(User).filter_by(email="test@example.com").first()

if user:
    # Update password
    new_password = "TestPassword123!"
    user.hashed_password = get_password_hash(new_password)
    session.commit()
    print(f"Password reset for {user.email}")
    print(f"New password: {new_password}")
else:
    # Create new test user
    from datetime import datetime
    new_user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow()
    )
    session.add(new_user)
    session.commit()
    print("Created new test user")
    print("Email: test@example.com")
    print("Password: TestPassword123!")

session.close()