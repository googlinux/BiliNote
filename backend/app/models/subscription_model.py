"""
Pydantic models for subscription and billing endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.db.models.subscription import PlanType, BillingCycle, SubscriptionStatus


class PlanFeatures(BaseModel):
    """Plan features description"""
    max_videos_per_month: int
    max_video_duration_minutes: int
    ai_models: List[str]
    screenshots: bool
    multi_modal: bool
    mind_maps: bool
    api_access: bool
    priority_support: bool
    custom_ai_keys: bool


class PricingPlan(BaseModel):
    """Pricing plan details"""
    plan_type: PlanType
    name: str
    description: str
    price_monthly: float
    price_yearly: float
    features: PlanFeatures


class SubscriptionResponse(BaseModel):
    """Subscription details response"""
    id: int
    user_id: int
    plan_type: PlanType
    billing_cycle: Optional[BillingCycle]
    status: SubscriptionStatus
    max_videos_per_month: int
    max_video_duration_minutes: int
    current_period_start: datetime
    current_period_end: Optional[datetime]
    trial_end: Optional[datetime]
    cancel_at: Optional[datetime]
    auto_renew: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UsageStats(BaseModel):
    """Usage statistics for current period"""
    videos_used: int
    videos_limit: int
    duration_used_minutes: int
    duration_limit_minutes: int
    period_start: datetime
    period_end: Optional[datetime]
    is_unlimited: bool


class SubscriptionCreate(BaseModel):
    """Create subscription request"""
    plan_type: PlanType
    billing_cycle: BillingCycle


class CheckoutSession(BaseModel):
    """Stripe checkout session response"""
    session_id: str
    url: str


class InvoiceResponse(BaseModel):
    """Invoice details response"""
    id: int
    amount: float
    currency: str
    status: str
    plan_type: PlanType
    billing_cycle: BillingCycle
    invoice_date: datetime
    paid_at: Optional[datetime]
    invoice_pdf_url: Optional[str]

    class Config:
        from_attributes = True
