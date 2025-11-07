"""
Subscription router for plan management, quota tracking, and billing
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.engine import get_db
from app.db.subscription_dao import SubscriptionDAO, PLAN_CONFIG
from app.db.models.user import User
from app.db.models.subscription import PlanType, BillingCycle
from app.models.subscription_model import (
    PricingPlan, SubscriptionResponse, UsageStats,
    SubscriptionCreate, InvoiceResponse, PlanFeatures
)
from app.core.dependencies import get_current_active_user
from app.utils.response import ResponseWrapper

router = APIRouter(prefix="/api/subscription", tags=["Subscription"])


@router.get("/plans", response_model=ResponseWrapper[List[PricingPlan]])
async def get_pricing_plans():
    """
    Get all available pricing plans

    Public endpoint - no authentication required
    """
    plans = [
        PricingPlan(
            plan_type=PlanType.FREE,
            name="Free",
            description="Perfect for trying out BiliNote",
            price_monthly=0,
            price_yearly=0,
            features=PlanFeatures(
                max_videos_per_month=5,
                max_video_duration_minutes=10,
                ai_models=["GPT-3.5"],
                screenshots=False,
                multi_modal=False,
                mind_maps=False,
                api_access=False,
                priority_support=False,
                custom_ai_keys=False,
            )
        ),
        PricingPlan(
            plan_type=PlanType.BASIC,
            name="Basic",
            description="For regular video learners",
            price_monthly=9.0,
            price_yearly=86.0,  # ~20% discount
            features=PlanFeatures(
                max_videos_per_month=100,
                max_video_duration_minutes=30,
                ai_models=["GPT-4", "Claude 3 Sonnet"],
                screenshots=True,
                multi_modal=False,
                mind_maps=False,
                api_access=False,
                priority_support=False,
                custom_ai_keys=False,
            )
        ),
        PricingPlan(
            plan_type=PlanType.PRO,
            name="Pro",
            description="For power users and professionals",
            price_monthly=29.0,
            price_yearly=278.0,  # ~20% discount
            features=PlanFeatures(
                max_videos_per_month=500,
                max_video_duration_minutes=120,
                ai_models=["GPT-4", "GPT-4o", "Claude 3 Opus", "Claude 3.5 Sonnet"],
                screenshots=True,
                multi_modal=True,
                mind_maps=True,
                api_access=True,
                priority_support=True,
                custom_ai_keys=False,
            )
        ),
        PricingPlan(
            plan_type=PlanType.ENTERPRISE,
            name="Enterprise",
            description="For teams and organizations",
            price_monthly=99.0,
            price_yearly=950.0,
            features=PlanFeatures(
                max_videos_per_month=-1,  # Unlimited
                max_video_duration_minutes=-1,  # Unlimited
                ai_models=["All models available"],
                screenshots=True,
                multi_modal=True,
                mind_maps=True,
                api_access=True,
                priority_support=True,
                custom_ai_keys=True,
            )
        ),
    ]

    return ResponseWrapper.success(
        data=plans,
        msg="Pricing plans retrieved"
    )


@router.get("/current", response_model=ResponseWrapper[SubscriptionResponse])
async def get_current_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's subscription details

    Requires authentication
    """
    subscription = SubscriptionDAO.get_subscription(db, current_user.id)

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )

    return ResponseWrapper.success(
        data=SubscriptionResponse.model_validate(subscription),
        msg="Subscription retrieved"
    )


@router.get("/usage", response_model=ResponseWrapper[UsageStats])
async def get_usage_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get usage statistics for current billing period

    Requires authentication
    """
    subscription = SubscriptionDAO.get_subscription(db, current_user.id)

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )

    videos_used, duration_used_minutes = SubscriptionDAO.get_usage_stats(db, current_user.id)

    stats = UsageStats(
        videos_used=videos_used,
        videos_limit=subscription.max_videos_per_month,
        duration_used_minutes=duration_used_minutes,
        duration_limit_minutes=subscription.max_video_duration_minutes,
        period_start=subscription.current_period_start,
        period_end=subscription.current_period_end,
        is_unlimited=subscription.is_unlimited,
    )

    return ResponseWrapper.success(
        data=stats,
        msg="Usage statistics retrieved"
    )


@router.post("/subscribe", response_model=ResponseWrapper[dict])
async def subscribe_to_plan(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Subscribe to a plan (creates Stripe checkout session)

    NOTE: This is a simplified version. In production, this would:
    1. Create Stripe checkout session
    2. Redirect user to Stripe payment page
    3. Handle webhook to activate subscription after payment

    For now, it directly activates the subscription (FREE for testing)
    """
    # Only allow free plan for direct activation
    if subscription_data.plan_type != PlanType.FREE:
        # In production, create Stripe checkout session here
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Paid subscriptions require Stripe integration (coming soon)"
        )

    # Create/update subscription
    subscription = SubscriptionDAO.create_subscription(
        db=db,
        user_id=current_user.id,
        plan_type=subscription_data.plan_type,
        billing_cycle=subscription_data.billing_cycle,
    )

    return ResponseWrapper.success(
        data={"subscription_id": subscription.id},
        msg=f"Subscribed to {subscription_data.plan_type.value} plan"
    )


@router.post("/cancel", response_model=ResponseWrapper[dict])
async def cancel_subscription(
    immediately: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cancel subscription

    - **immediately**: If True, downgrade to Free immediately. If False, at period end.

    Requires authentication
    """
    success = SubscriptionDAO.cancel_subscription(
        db=db,
        user_id=current_user.id,
        immediately=immediately
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )

    message = "Subscription cancelled immediately" if immediately else "Subscription will be cancelled at period end"

    return ResponseWrapper.success(
        data={},
        msg=message
    )


@router.get("/invoices", response_model=ResponseWrapper[List[InvoiceResponse]])
async def get_invoices(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all invoices for current user

    Requires authentication
    """
    invoices = SubscriptionDAO.get_user_invoices(db, current_user.id)

    return ResponseWrapper.success(
        data=[InvoiceResponse.model_validate(invoice) for invoice in invoices],
        msg="Invoices retrieved"
    )
