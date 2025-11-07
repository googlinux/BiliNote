"""
Data Access Object for User operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime
from app.db.models.user import User
from app.db.models.subscription import Subscription, PlanType, SubscriptionStatus
from app.core.security import get_password_hash, verify_password


class UserDAO:
    """User database operations"""

    @staticmethod
    def create_user(db: Session, email: str, password: str, full_name: Optional[str] = None,
                    username: Optional[str] = None) -> User:
        """
        Create a new user with hashed password and default free subscription

        Args:
            db: Database session
            email: User email
            password: Plain password (will be hashed)
            full_name: User's full name
            username: Username

        Returns:
            Created User object
        """
        hashed_password = get_password_hash(password)

        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            username=username,
            is_active=True,
            is_verified=False,  # Require email verification
        )

        db.add(user)
        db.flush()  # Flush to get user.id

        # Create default free subscription
        subscription = Subscription(
            user_id=user.id,
            plan_type=PlanType.FREE,
            status=SubscriptionStatus.ACTIVE,
            max_videos_per_month=5,
            max_video_duration_minutes=10,
        )

        db.add(subscription)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(func.lower(User.email) == func.lower(email)).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(func.lower(User.username) == func.lower(username)).first()

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password

        Args:
            db: Database session
            email: User email
            password: Plain password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = UserDAO.get_user_by_email(db, email)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        return user

    @staticmethod
    def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
        """
        Update user fields

        Args:
            db: Database session
            user_id: User ID
            **kwargs: Fields to update

        Returns:
            Updated User object
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def update_password(db: Session, user_id: int, new_password: str) -> bool:
        """
        Update user password

        Args:
            db: Database session
            user_id: User ID
            new_password: New plain password

        Returns:
            True if successful
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return False

        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()

        return True

    @staticmethod
    def verify_email(db: Session, email: str) -> bool:
        """
        Mark user email as verified

        Args:
            db: Database session
            email: User email

        Returns:
            True if successful
        """
        user = UserDAO.get_user_by_email(db, email)

        if not user:
            return False

        user.is_verified = True
        user.updated_at = datetime.utcnow()
        db.commit()

        return True

    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> bool:
        """
        Deactivate user account

        Args:
            db: Database session
            user_id: User ID

        Returns:
            True if successful
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return False

        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.commit()

        return True

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        Permanently delete user (cascade deletes subscription, usage, tasks)

        Args:
            db: Database session
            user_id: User ID

        Returns:
            True if successful
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return False

        db.delete(user)
        db.commit()

        return True
