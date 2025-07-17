"""
Handles subscription management, including Stripe checkout, webhook processing, and subscription status queries.
"""
from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from sqlalchemy.orm import Session
from .. import models, schemas, deps, stripe_utils
from ..database import SessionLocal
from ..config import settings

router = APIRouter(tags=["subscription"])

class SubscriptionRequest(schemas.BaseModel):
    access_token: str

@router.post("/subscribe/pro", response_model=schemas.APIResponse)
async def subscribe_pro(req: SubscriptionRequest, db: Session = Depends(deps.get_db)):
    """
    Initiate a Stripe checkout session for upgrading the current user to 'pro' tier.
    """
    # Get current user from access token
    current_user = await deps.get_current_user_from_schema(req, db)
    session = stripe_utils.create_checkout_session(current_user.id)
    return schemas.APIResponse(status="success", message="Stripe checkout session created", data={"checkout_url": session.url})

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(deps.get_db)):
    """
    Handle Stripe webhook events, updating subscription status on successful payment.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    event = stripe_utils.verify_webhook_signature(payload, sig_header)
    if not event:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    # Handle checkout session completion
    if event["type"] == "checkout.session.completed":
        user_id = int(event["data"]["object"]["metadata"]["user_id"])
        sub = db.query(models.Subscription).filter(models.Subscription.user_id == user_id).first()
        if not sub:
            sub = models.Subscription(user_id=user_id, tier="pro", status="active")
            db.add(sub)
        else:
            sub.tier = "pro"
            sub.status = "active"
        db.commit()
    return {"status": "success"}

@router.get("/subscription/status", response_model=schemas.SubscriptionOut)
async def subscription_status(access_token: str = Query(...), db: Session = Depends(deps.get_db)):
    """
    Get the current subscription status for the authenticated user.
    """
    # Get current user from access token
    current_user = await deps.get_current_user_from_query(access_token, db)
    sub = db.query(models.Subscription).filter(models.Subscription.user_id == current_user.id).first()
    if not sub:
        return schemas.SubscriptionOut(tier="basic", status="inactive", started_at=None, ends_at=None)
    return sub 