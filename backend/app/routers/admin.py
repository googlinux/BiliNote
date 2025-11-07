"""
Admin router for administrative functions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.db.engine import get_db
from app.db.models.user import User
from app.db.models.subscription import Subscription, Invoice, PlanType, SubscriptionStatus
from app.core.dependencies import get_current_active_user
from app.utils.response import ResponseWrapper
from pydantic import BaseModel
from typing import Dict, List

router = APIRouter(prefix="/api/admin", tags=["Admin"])


class SystemStats(BaseModel):
    """System statistics"""
    total_users: int
    active_users: int
    total_subscriptions: Dict[str, int]
    active_subscriptions: int
    monthly_revenue: float
    total_revenue: float
    new_users_this_month: int
    churn_rate: float


class UserStats(BaseModel):
    """User statistics"""
    id: int
    email: str
    full_name: str | None
    created_at: datetime
    plan_type: str
    status: str
    videos_used: int
    videos_limit: int


def is_admin(current_user: User = Depends(get_current_active_user)):
    """Check if user is admin"""
    # For now, check if email is admin email
    # In production, add an is_admin field to User model
    admin_emails = [
        "admin@bilinote.app",
        "admin@localhost",
        "test@test.com",  # For testing
    ]

    if current_user.email not in admin_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user


@router.get("/stats", response_model=ResponseWrapper[SystemStats])
async def get_system_stats(
    current_user: User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """
    Get system-wide statistics

    Requires admin access
    """
    # Total users
    total_users = db.query(func.count(User.id)).scalar()

    # Active users (users with active subscriptions)
    active_users = db.query(func.count(User.id)).join(Subscription).filter(
        Subscription.status == SubscriptionStatus.ACTIVE
    ).scalar()

    # Subscription breakdown by plan type
    subscription_breakdown = {}
    for plan_type in PlanType:
        count = db.query(func.count(Subscription.id)).filter(
            Subscription.plan_type == plan_type
        ).scalar()
        subscription_breakdown[plan_type.value] = count

    # Active subscriptions (not free, not cancelled)
    active_subscriptions = db.query(func.count(Subscription.id)).filter(
        Subscription.plan_type != PlanType.FREE,
        Subscription.status == SubscriptionStatus.ACTIVE
    ).scalar()

    # Revenue calculation
    # Monthly revenue (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    monthly_revenue = db.query(func.sum(Invoice.amount)).filter(
        Invoice.paid_at >= thirty_days_ago,
        Invoice.status == "paid"
    ).scalar() or 0.0

    # Total revenue (all time)
    total_revenue = db.query(func.sum(Invoice.amount)).filter(
        Invoice.status == "paid"
    ).scalar() or 0.0

    # New users this month
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_users_this_month = db.query(func.count(User.id)).filter(
        User.created_at >= first_day_of_month
    ).scalar()

    # Churn rate (cancelled subscriptions in last 30 days / total paying customers)
    cancelled_last_30_days = db.query(func.count(Subscription.id)).filter(
        Subscription.cancelled_at >= thirty_days_ago,
        Subscription.cancelled_at.isnot(None)
    ).scalar()

    paying_customers = db.query(func.count(Subscription.id)).filter(
        Subscription.plan_type != PlanType.FREE
    ).scalar()

    churn_rate = (cancelled_last_30_days / paying_customers * 100) if paying_customers > 0 else 0.0

    stats = SystemStats(
        total_users=total_users,
        active_users=active_users,
        total_subscriptions=subscription_breakdown,
        active_subscriptions=active_subscriptions,
        monthly_revenue=round(monthly_revenue, 2),
        total_revenue=round(total_revenue, 2),
        new_users_this_month=new_users_this_month,
        churn_rate=round(churn_rate, 2)
    )

    return ResponseWrapper.success(data=stats)


@router.get("/users", response_model=ResponseWrapper[List[UserStats]])
async def get_users(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of users with their subscription info

    Requires admin access
    """
    users = db.query(User).offset(offset).limit(limit).all()

    user_stats = []
    for user in users:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user.id
        ).first()

        if subscription:
            user_stats.append(UserStats(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                created_at=user.created_at,
                plan_type=subscription.plan_type.value,
                status=subscription.status.value,
                videos_used=subscription.videos_used,
                videos_limit=subscription.max_videos_per_month
            ))

    return ResponseWrapper.success(data=user_stats)


@router.get("/revenue", response_model=ResponseWrapper[Dict])
async def get_revenue_breakdown(
    current_user: User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """
    Get revenue breakdown by plan type

    Requires admin access
    """
    revenue_by_plan = {}

    for plan_type in PlanType:
        if plan_type == PlanType.FREE:
            continue

        revenue = db.query(func.sum(Invoice.amount)).filter(
            Invoice.plan_type == plan_type,
            Invoice.status == "paid"
        ).scalar() or 0.0

        revenue_by_plan[plan_type.value] = round(revenue, 2)

    # Monthly breakdown (last 12 months)
    monthly_breakdown = []
    for i in range(12):
        month_start = (datetime.utcnow().replace(day=1) - timedelta(days=i*30))
        month_end = month_start + timedelta(days=30)

        monthly_revenue = db.query(func.sum(Invoice.amount)).filter(
            Invoice.paid_at >= month_start,
            Invoice.paid_at < month_end,
            Invoice.status == "paid"
        ).scalar() or 0.0

        monthly_breakdown.append({
            "month": month_start.strftime("%Y-%m"),
            "revenue": round(monthly_revenue, 2)
        })

    return ResponseWrapper.success(data={
        "by_plan": revenue_by_plan,
        "monthly": list(reversed(monthly_breakdown))  # Most recent first
    })
