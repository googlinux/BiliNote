"""
Initialize authentication database tables

Run this script to create all auth-related tables
"""
from app.db.engine import Base, engine
from app.db.models.user import User
from app.db.models.subscription import Subscription, UsageRecord, Invoice
from app.db.models.video_tasks import VideoTask
from app.db.models.models import Model
from app.db.models.providers import Provider


def init_db():
    """Create all tables"""
    print("Creating database tables...")

    # Import all models to ensure they're registered with Base
    # This is important for SQLAlchemy to know about all tables

    # Create all tables
    Base.metadata.create_all(bind=engine)

    print("✅ Database tables created successfully!")
    print("\nCreated tables:")
    print("- users")
    print("- subscriptions")
    print("- usage_records")
    print("- invoices")
    print("- video_tasks (updated with user_id)")
    print("- models")
    print("- providers")


if __name__ == "__main__":
    init_db()
