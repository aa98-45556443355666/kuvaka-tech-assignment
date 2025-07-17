"""
Stripe utility functions for creating checkout sessions and verifying webhooks.
"""
import stripe
from .config import settings
import os

stripe.api_key = settings.STRIPE_API_KEY

PRO_PRICE_ID = os.getenv("STRIPE_PRO_PRICE_ID")
BASIC_PRICE_ID = os.getenv("STRIPE_BASIC_PRICE_ID")


def create_checkout_session(user_id: int):
    """
    Create a Stripe checkout session for the given user ID for the 'pro' subscription tier.
    """
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price": PRO_PRICE_ID,
            "quantity": 1,
        }],
        mode="subscription",
        success_url="https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="https://yourdomain.com/cancel",
        metadata={"user_id": user_id},
    )
    return session

def verify_webhook_signature(payload, sig_header):
    """
    Verify the Stripe webhook signature and return the event if valid, else None.
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        return event
    except Exception:
        return None 