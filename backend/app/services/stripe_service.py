"""
Stripe payment service for subscription management
"""
import stripe
from typing import Optional, Dict, Any
from app.core.config import settings
from app.db.models.subscription import PlanType, BillingCycle

# Initialize Stripe
if settings.STRIPE_API_KEY:
    stripe.api_key = settings.STRIPE_API_KEY


# Price mapping (configured in Stripe dashboard)
STRIPE_PRICE_MAP = {
    (PlanType.BASIC, BillingCycle.MONTHLY): settings.STRIPE_PRICE_BASIC_MONTHLY,
    (PlanType.BASIC, BillingCycle.YEARLY): settings.STRIPE_PRICE_BASIC_YEARLY,
    (PlanType.PRO, BillingCycle.MONTHLY): settings.STRIPE_PRICE_PRO_MONTHLY,
    (PlanType.PRO, BillingCycle.YEARLY): settings.STRIPE_PRICE_PRO_YEARLY,
    (PlanType.ENTERPRISE, BillingCycle.MONTHLY): settings.STRIPE_PRICE_ENTERPRISE_MONTHLY,
    (PlanType.ENTERPRISE, BillingCycle.YEARLY): settings.STRIPE_PRICE_ENTERPRISE_YEARLY,
}


class StripeService:
    """Stripe payment service"""

    @staticmethod
    def create_customer(email: str, name: Optional[str] = None, user_id: int = None) -> str:
        """
        Create a Stripe customer

        Args:
            email: Customer email
            name: Customer name
            user_id: Internal user ID

        Returns:
            Stripe customer ID
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")

        metadata = {"user_id": str(user_id)} if user_id else {}

        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata=metadata,
        )

        return customer.id

    @staticmethod
    def create_checkout_session(
        customer_id: str,
        plan_type: PlanType,
        billing_cycle: BillingCycle,
        success_url: str,
        cancel_url: str,
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout session

        Args:
            customer_id: Stripe customer ID
            plan_type: Subscription plan type
            billing_cycle: Billing cycle (monthly/yearly)
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment is cancelled

        Returns:
            Checkout session data with session_id and url
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")

        # Get price ID for the plan
        price_id = STRIPE_PRICE_MAP.get((plan_type, billing_cycle))

        if not price_id:
            raise ValueError(f"No price configured for {plan_type} {billing_cycle}")

        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "plan_type": plan_type.value,
                "billing_cycle": billing_cycle.value,
            },
        )

        return {
            "session_id": session.id,
            "url": session.url,
        }

    @staticmethod
    def cancel_subscription(subscription_id: str, immediately: bool = False) -> bool:
        """
        Cancel a Stripe subscription

        Args:
            subscription_id: Stripe subscription ID
            immediately: If True, cancel immediately. If False, cancel at period end.

        Returns:
            Success status
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")

        try:
            if immediately:
                stripe.Subscription.delete(subscription_id)
            else:
                stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True,
                )
            return True
        except stripe.error.StripeError:
            return False

    @staticmethod
    def get_subscription(subscription_id: str) -> Optional[Dict[str, Any]]:
        """
        Get Stripe subscription details

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            Subscription data or None
        """
        if not stripe.api_key:
            return None

        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except stripe.error.StripeError:
            return None

    @staticmethod
    def construct_webhook_event(payload: bytes, signature: str) -> Optional[Any]:
        """
        Construct and verify Stripe webhook event

        Args:
            payload: Request body
            signature: Stripe signature header

        Returns:
            Stripe event or None if invalid
        """
        if not settings.STRIPE_WEBHOOK_SECRET:
            raise ValueError("Stripe webhook secret not configured")

        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except stripe.error.SignatureVerificationError:
            return None

    @staticmethod
    def get_customer_portal_url(customer_id: str, return_url: str) -> str:
        """
        Create a customer portal session for managing subscriptions

        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after managing subscription

        Returns:
            Customer portal URL
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")

        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )

        return session.url
