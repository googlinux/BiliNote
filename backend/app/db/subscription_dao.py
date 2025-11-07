"""
Data Access Object for Subscription and Usage operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from app.db.models.subscription import (
    Subscription, UsageRecord, Invoice,
    PlanType, BillingCycle, SubscriptionStatus
)


# Plan configuration (quota limits)
PLAN_CONFIG = {
    PlanType.FREE: {
        "max_videos_per_month": 5,
        "max_video_duration_minutes": 10,
        "ai_models": ["gpt-3.5-turbo"],
        "screenshots": False,
        "multi_modal": False,
        "mind_maps": False,
        "api_access": False,
    },
    PlanType.BASIC: {
        "max_videos_per_month": 100,
        "max_video_duration_minutes": 30,
        "ai_models": ["gpt-4", "claude-3-sonnet"],
        "screenshots": True,
        "multi_modal": False,
        "mind_maps": False,
        "api_access": False,
    },
    PlanType.PRO: {
        "max_videos_per_month": 500,
        "max_video_duration_minutes": 120,
        "ai_models": ["gpt-4", "gpt-4o", "claude-3-opus", "claude-3.5-sonnet"],
        "screenshots": True,
        "multi_modal": True,
        "mind_maps": True,
        "api_access": True,
    },
    PlanType.ENTERPRISE: {
        "max_videos_per_month": -1,  # Unlimited
        "max_video_duration_minutes": -1,  # Unlimited
        "ai_models": ["all"],
        "screenshots": True,
        "multi_modal": True,
        "mind_maps": True,
        "api_access": True,
    },
}


class SubscriptionDAO:
    """Subscription database operations"""

    @staticmethod
    def get_subscription(db: Session, user_id: int) -> Optional[Subscription]:
        """Get user's subscription"""
        return db.query(Subscription).filter(Subscription.user_id == user_id).first()

    @staticmethod
    def create_subscription(
        db: Session,
        user_id: int,
        plan_type: PlanType,
        billing_cycle: Optional[BillingCycle] = None,
    ) -> Subscription:
        """Create or update subscription"""
        subscription = SubscriptionDAO.get_subscription(db, user_id)

        plan_config = PLAN_CONFIG[plan_type]

        if subscription:
            # Update existing subscription
            subscription.plan_type = plan_type
            subscription.billing_cycle = billing_cycle
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.max_videos_per_month = plan_config["max_videos_per_month"]
            subscription.max_video_duration_minutes = plan_config["max_video_duration_minutes"]
            subscription.current_period_start = datetime.utcnow()

            # Set period end based on billing cycle
            if billing_cycle == BillingCycle.MONTHLY:
                subscription.current_period_end = datetime.utcnow() + timedelta(days=30)
            elif billing_cycle == BillingCycle.YEARLY:
                subscription.current_period_end = datetime.utcnow() + timedelta(days=365)

            subscription.updated_at = datetime.utcnow()
        else:
            # Create new subscription
            subscription = Subscription(
                user_id=user_id,
                plan_type=plan_type,
                billing_cycle=billing_cycle,
                status=SubscriptionStatus.ACTIVE,
                max_videos_per_month=plan_config["max_videos_per_month"],
                max_video_duration_minutes=plan_config["max_video_duration_minutes"],
            )

            if billing_cycle == BillingCycle.MONTHLY:
                subscription.current_period_end = datetime.utcnow() + timedelta(days=30)
            elif billing_cycle == BillingCycle.YEARLY:
                subscription.current_period_end = datetime.utcnow() + timedelta(days=365)

            db.add(subscription)

        db.commit()
        db.refresh(subscription)

        return subscription

    @staticmethod
    def cancel_subscription(db: Session, user_id: int, immediately: bool = False) -> bool:
        """Cancel subscription (downgrade to free at period end or immediately)"""
        subscription = SubscriptionDAO.get_subscription(db, user_id)

        if not subscription:
            return False

        if immediately:
            # Downgrade to free immediately
            subscription.plan_type = PlanType.FREE
            subscription.billing_cycle = None
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.max_videos_per_month = PLAN_CONFIG[PlanType.FREE]["max_videos_per_month"]
            subscription.max_video_duration_minutes = PLAN_CONFIG[PlanType.FREE]["max_video_duration_minutes"]
            subscription.current_period_end = None
            subscription.auto_renew = False
            subscription.cancelled_at = datetime.utcnow()
        else:
            # Cancel at period end
            subscription.cancel_at = subscription.current_period_end
            subscription.auto_renew = False
            subscription.cancelled_at = datetime.utcnow()

        db.commit()
        return True

    @staticmethod
    def get_usage_stats(db: Session, user_id: int) -> Tuple[int, int]:
        """
        Get current month usage statistics

        Returns:
            Tuple of (videos_used, duration_used_minutes)
        """
        subscription = SubscriptionDAO.get_subscription(db, user_id)

        if not subscription:
            return (0, 0)

        # Get usage for current period
        period_start = subscription.current_period_start
        period_end = subscription.current_period_end or datetime.utcnow()

        usage_records = db.query(UsageRecord).filter(
            UsageRecord.user_id == user_id,
            UsageRecord.created_at >= period_start,
            UsageRecord.created_at <= period_end,
        ).all()

        videos_used = len(usage_records)
        duration_used_seconds = sum(record.video_duration_seconds for record in usage_records)
        duration_used_minutes = duration_used_seconds // 60

        return (videos_used, duration_used_minutes)

    @staticmethod
    def check_quota(db: Session, user_id: int, video_duration_minutes: int) -> Tuple[bool, str]:
        """
        Check if user has quota for a new video

        Returns:
            Tuple of (has_quota, error_message)
        """
        subscription = SubscriptionDAO.get_subscription(db, user_id)

        if not subscription:
            return (False, "No subscription found")

        # Enterprise has unlimited quota
        if subscription.plan_type == PlanType.ENTERPRISE:
            return (True, "")

        videos_used, duration_used_minutes = SubscriptionDAO.get_usage_stats(db, user_id)

        # Check video count quota
        if videos_used >= subscription.max_videos_per_month:
            return (False, f"Monthly video limit reached ({subscription.max_videos_per_month} videos)")

        # Check video duration quota
        if video_duration_minutes > subscription.max_video_duration_minutes:
            return (False, f"Video too long (max {subscription.max_video_duration_minutes} minutes per video)")

        # Check total duration quota (optional, could add this to subscription model)
        # For now, we only check per-video duration

        return (True, "")

    @staticmethod
    def record_usage(
        db: Session,
        user_id: int,
        task_id: str,
        video_duration_seconds: int,
        tokens_used: int = 0,
        screenshots_generated: int = 0,
        platform: Optional[str] = None,
        video_url: Optional[str] = None,
    ) -> UsageRecord:
        """Record video processing usage"""
        usage = UsageRecord(
            user_id=user_id,
            task_id=task_id,
            video_duration_seconds=video_duration_seconds,
            tokens_used=tokens_used,
            screenshots_generated=screenshots_generated,
            platform=platform,
            video_url=video_url,
        )

        db.add(usage)
        db.commit()
        db.refresh(usage)

        return usage

    @staticmethod
    def get_user_invoices(db: Session, user_id: int) -> List[Invoice]:
        """Get all invoices for a user"""
        return db.query(Invoice).filter(Invoice.user_id == user_id).order_by(Invoice.invoice_date.desc()).all()

    @staticmethod
    def create_invoice(
        db: Session,
        user_id: int,
        stripe_invoice_id: str,
        amount: float,
        plan_type: PlanType,
        billing_cycle: BillingCycle,
        **kwargs
    ) -> Invoice:
        """Create invoice record"""
        invoice = Invoice(
            user_id=user_id,
            stripe_invoice_id=stripe_invoice_id,
            amount=amount,
            plan_type=plan_type,
            billing_cycle=billing_cycle,
            **kwargs
        )

        db.add(invoice)
        db.commit()
        db.refresh(invoice)

        return invoice
