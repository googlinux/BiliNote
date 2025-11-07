"""
Payment router for Stripe integration
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from app.db.engine import get_db
from app.db.user_dao import UserDAO
from app.db.subscription_dao import SubscriptionDAO
from app.db.models.user import User
from app.db.models.subscription import PlanType, BillingCycle, SubscriptionStatus
from app.services.stripe_service import StripeService
from app.core.dependencies import get_current_active_user
from app.core.config import settings
from app.utils.response import ResponseWrapper
from app.services.email_service import EmailService
from pydantic import BaseModel

router = APIRouter(prefix="/api/payment", tags=["Payment"])


class CheckoutRequest(BaseModel):
    """Checkout session request"""
    plan_type: PlanType
    billing_cycle: BillingCycle


class CheckoutResponse(BaseModel):
    """Checkout session response"""
    session_id: str
    url: str


class PortalResponse(BaseModel):
    """Customer portal response"""
    url: str


@router.post("/create-checkout-session", response_model=ResponseWrapper[CheckoutResponse])
async def create_checkout_session(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a Stripe Checkout session for subscription

    Returns checkout URL to redirect user to Stripe payment page
    """
    if not settings.STRIPE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Stripe integration not configured"
        )

    # Free plan doesn't need payment
    if request.plan_type == PlanType.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Free plan doesn't require payment"
        )

    # Get or create Stripe customer
    subscription = SubscriptionDAO.get_subscription(db, current_user.id)

    if not subscription.stripe_customer_id:
        # Create Stripe customer
        customer_id = StripeService.create_customer(
            email=current_user.email,
            name=current_user.full_name,
            user_id=current_user.id,
        )

        # Update subscription with customer ID
        subscription.stripe_customer_id = customer_id
        db.commit()
    else:
        customer_id = subscription.stripe_customer_id

    # Create checkout session
    success_url = f"{settings.FRONTEND_URL}/dashboard/settings/billing?success=true"
    cancel_url = f"{settings.FRONTEND_URL}/dashboard/settings/billing?cancelled=true"

    try:
        session_data = StripeService.create_checkout_session(
            customer_id=customer_id,
            plan_type=request.plan_type,
            billing_cycle=request.billing_cycle,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        return ResponseWrapper.success(
            data=CheckoutResponse(**session_data),
            msg="Checkout session created"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events

    This endpoint is called by Stripe when payment events occur
    """
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Webhook secret not configured"
        )

    # Get raw body
    payload = await request.body()

    # Verify webhook signature
    event = StripeService.construct_webhook_event(payload, stripe_signature)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )

    # Handle different event types
    event_type = event["type"]

    if event_type == "checkout.session.completed":
        # Payment successful - activate subscription
        session = event["data"]["object"]
        await handle_checkout_completed(session, db)

    elif event_type == "customer.subscription.updated":
        # Subscription updated (e.g., plan change)
        subscription = event["data"]["object"]
        await handle_subscription_updated(subscription, db)

    elif event_type == "customer.subscription.deleted":
        # Subscription cancelled
        subscription = event["data"]["object"]
        await handle_subscription_deleted(subscription, db)

    elif event_type == "invoice.payment_succeeded":
        # Recurring payment successful
        invoice = event["data"]["object"]
        await handle_invoice_paid(invoice, db)

    elif event_type == "invoice.payment_failed":
        # Payment failed
        invoice = event["data"]["object"]
        await handle_invoice_failed(invoice, db)

    return {"status": "success"}


async def handle_checkout_completed(session: dict, db: Session):
    """Handle successful checkout"""
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    metadata = session.get("metadata", {})

    plan_type = PlanType(metadata.get("plan_type", "basic"))
    billing_cycle = BillingCycle(metadata.get("billing_cycle", "monthly"))

    # Find user by Stripe customer ID
    from app.db.models.subscription import Subscription
    subscription_obj = db.query(Subscription).filter(
        Subscription.stripe_customer_id == customer_id
    ).first()

    if subscription_obj:
        # Update subscription
        subscription_obj.plan_type = plan_type
        subscription_obj.billing_cycle = billing_cycle
        subscription_obj.stripe_subscription_id = subscription_id
        subscription_obj.status = SubscriptionStatus.ACTIVE

        # Set period dates
        subscription_obj.current_period_start = datetime.utcnow()
        if billing_cycle == BillingCycle.MONTHLY:
            subscription_obj.current_period_end = datetime.utcnow() + timedelta(days=30)
        else:
            subscription_obj.current_period_end = datetime.utcnow() + timedelta(days=365)

        # Update quotas
        from app.db.subscription_dao import PLAN_CONFIG
        config = PLAN_CONFIG[plan_type]
        subscription_obj.max_videos_per_month = config["max_videos_per_month"]
        subscription_obj.max_video_duration_minutes = config["max_video_duration_minutes"]

        db.commit()

        # Send payment success email
        try:
            user = UserDAO.get_user_by_id(db, subscription_obj.user_id)
            if user:
                amount = session.get("amount_total", 0) / 100  # Convert cents to dollars
                EmailService.send_payment_success_email(
                    email=user.email,
                    plan_name=plan_type.value.capitalize(),
                    amount=amount,
                    billing_cycle=billing_cycle.value
                )
        except Exception as e:
            print(f"Failed to send payment success email: {e}")


async def handle_subscription_updated(subscription: dict, db: Session):
    """Handle subscription update"""
    subscription_id = subscription.get("id")
    status_str = subscription.get("status")

    # Find subscription by Stripe subscription ID
    from app.db.models.subscription import Subscription
    subscription_obj = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()

    if subscription_obj:
        # Update status
        if status_str == "active":
            subscription_obj.status = SubscriptionStatus.ACTIVE
        elif status_str == "past_due":
            subscription_obj.status = SubscriptionStatus.PAST_DUE
        elif status_str == "canceled":
            subscription_obj.status = SubscriptionStatus.CANCELLED

        db.commit()


async def handle_subscription_deleted(subscription: dict, db: Session):
    """Handle subscription cancellation"""
    subscription_id = subscription.get("id")

    # Find subscription by Stripe subscription ID
    from app.db.models.subscription import Subscription
    subscription_obj = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()

    if subscription_obj:
        # Store old plan name before downgrade
        old_plan_name = subscription_obj.plan_type.value.capitalize()

        # Downgrade to free plan
        subscription_obj.plan_type = PlanType.FREE
        subscription_obj.billing_cycle = None
        subscription_obj.status = SubscriptionStatus.CANCELLED
        subscription_obj.cancelled_at = datetime.utcnow()

        from app.db.subscription_dao import PLAN_CONFIG
        config = PLAN_CONFIG[PlanType.FREE]
        subscription_obj.max_videos_per_month = config["max_videos_per_month"]
        subscription_obj.max_video_duration_minutes = config["max_video_duration_minutes"]

        # Get access end date
        access_until = subscription_obj.current_period_end

        db.commit()

        # Send cancellation email
        try:
            user = UserDAO.get_user_by_id(db, subscription_obj.user_id)
            if user and access_until:
                EmailService.send_subscription_cancelled_email(
                    email=user.email,
                    plan_name=old_plan_name,
                    access_until=access_until.strftime("%B %d, %Y")
                )
        except Exception as e:
            print(f"Failed to send cancellation email: {e}")


async def handle_invoice_paid(invoice: dict, db: Session):
    """Handle successful invoice payment"""
    customer_id = invoice.get("customer")
    amount = invoice.get("amount_paid") / 100  # Convert cents to dollars
    invoice_id = invoice.get("id")

    # Find subscription by customer ID
    from app.db.models.subscription import Subscription, Invoice
    subscription = db.query(Subscription).filter(
        Subscription.stripe_customer_id == customer_id
    ).first()

    if subscription:
        # Create invoice record
        invoice_obj = Invoice(
            user_id=subscription.user_id,
            stripe_invoice_id=invoice_id,
            amount=amount,
            currency="usd",
            status="paid",
            plan_type=subscription.plan_type,
            billing_cycle=subscription.billing_cycle,
            invoice_date=datetime.utcnow(),
            paid_at=datetime.utcnow(),
        )
        db.add(invoice_obj)
        db.commit()


async def handle_invoice_failed(invoice: dict, db: Session):
    """Handle failed invoice payment"""
    customer_id = invoice.get("customer")

    # Find subscription by customer ID
    from app.db.models.subscription import Subscription
    subscription = db.query(Subscription).filter(
        Subscription.stripe_customer_id == customer_id
    ).first()

    if subscription:
        # Mark subscription as past due
        subscription.status = SubscriptionStatus.PAST_DUE
        db.commit()

        # Send payment failed email
        try:
            user = UserDAO.get_user_by_id(db, subscription.user_id)
            if user:
                EmailService.send_payment_failed_email(
                    email=user.email,
                    plan_name=subscription.plan_type.value.capitalize()
                )
        except Exception as e:
            print(f"Failed to send payment failed email: {e}")


@router.get("/customer-portal", response_model=ResponseWrapper[PortalResponse])
async def get_customer_portal(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get Stripe Customer Portal URL for managing subscriptions

    Users can update payment methods, view invoices, and cancel subscriptions
    """
    if not settings.STRIPE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Stripe integration not configured"
        )

    subscription = SubscriptionDAO.get_subscription(db, current_user.id)

    if not subscription.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Stripe customer found"
        )

    return_url = f"{settings.FRONTEND_URL}/dashboard/settings/billing"

    try:
        portal_url = StripeService.get_customer_portal_url(
            customer_id=subscription.stripe_customer_id,
            return_url=return_url,
        )

        return ResponseWrapper.success(
            data=PortalResponse(url=portal_url),
            msg="Customer portal URL generated"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
