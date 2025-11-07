"""
Subscription and pricing models for SaaS billing
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.db.engine import Base
import enum


class PlanType(str, enum.Enum):
    """Subscription plan types"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class BillingCycle(str, enum.Enum):
    """Billing cycle types"""
    MONTHLY = "monthly"
    YEARLY = "yearly"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


class Subscription(Base):
    """User subscription model"""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    # Plan details
    plan_type = Column(SQLEnum(PlanType), default=PlanType.FREE, nullable=False)
    billing_cycle = Column(SQLEnum(BillingCycle), default=BillingCycle.MONTHLY, nullable=True)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)

    # Stripe integration
    stripe_customer_id = Column(String(255), unique=True, nullable=True, index=True)
    stripe_subscription_id = Column(String(255), unique=True, nullable=True, index=True)
    stripe_price_id = Column(String(255), nullable=True)

    # Quota limits (based on plan)
    max_videos_per_month = Column(Integer, default=5, nullable=False)  # Free: 5, Basic: 100, Pro: 500, Enterprise: -1 (unlimited)
    max_video_duration_minutes = Column(Integer, default=10, nullable=False)  # Free: 10, Basic: 30, Pro: 120, Enterprise: -1

    # Billing dates
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    current_period_start = Column(DateTime, default=datetime.utcnow, nullable=False)
    current_period_end = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    cancel_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    # Auto renewal
    auto_renew = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="subscription")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan={self.plan_type})>"

    @property
    def is_active(self):
        """Check if subscription is active"""
        return self.status == SubscriptionStatus.ACTIVE and (
            self.current_period_end is None or self.current_period_end > datetime.utcnow()
        )

    @property
    def is_unlimited(self):
        """Check if plan has unlimited quota"""
        return self.plan_type == PlanType.ENTERPRISE


class UsageRecord(Base):
    """Track user usage for quota management"""
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String(255), nullable=False, index=True)

    # Usage metrics
    video_duration_seconds = Column(Integer, default=0, nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)  # AI tokens consumed
    screenshots_generated = Column(Integer, default=0, nullable=False)

    # Video details
    platform = Column(String(50), nullable=True)
    video_url = Column(String(2048), nullable=True)

    # Cost tracking (for analytics)
    estimated_cost_usd = Column(Numeric(10, 4), default=0.0, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="usage_records")

    def __repr__(self):
        return f"<UsageRecord(id={self.id}, user_id={self.user_id}, task_id={self.task_id})>"


class Invoice(Base):
    """Stripe invoices for payment tracking"""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Stripe details
    stripe_invoice_id = Column(String(255), unique=True, nullable=False, index=True)
    stripe_payment_intent_id = Column(String(255), nullable=True)

    # Invoice details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="usd", nullable=False)
    status = Column(String(50), nullable=False)  # paid, open, void, uncollectible

    # Plan details at time of invoice
    plan_type = Column(SQLEnum(PlanType), nullable=False)
    billing_cycle = Column(SQLEnum(BillingCycle), nullable=False)

    # Dates
    invoice_date = Column(DateTime, nullable=False)
    paid_at = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)

    # PDF URL
    invoice_pdf_url = Column(String(2048), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Invoice(id={self.id}, user_id={self.user_id}, amount={self.amount}, status={self.status})>"
