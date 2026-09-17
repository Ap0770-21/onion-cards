import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from supabase_client import supabase
from routers.auth import require_user

router = APIRouter()
PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")
PAYSTACK_BASE = "https://api.paystack.co"


@router.post("/checkout")
async def create_checkout(user=Depends(require_user)):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{PAYSTACK_BASE}/transaction/initialize",
            headers={"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"},
            json={
                "email": user.email,
                "amount": 250000,  # ₦2500.00 in kobo
                "metadata": {"user_id": user.id},
            },
        )
    data = resp.json()
    if not data.get("status"):
        raise HTTPException(status_code=502, detail="Could not start checkout")
    return {"authorization_url": data["data"]["authorization_url"]}


@router.post("/webhook")
async def paystack_webhook(request: Request):
    """
    Paystack calls this on payment events. Verify signature in production
    (X-Paystack-Signature header, HMAC-SHA512 with your secret key) before trusting the payload.
    """
    payload = await request.json()
    event = payload.get("event")

    if event == "charge.success":
        user_id = payload["data"]["metadata"]["user_id"]
        supabase.table("subscriptions").upsert(
            {
                "user_id": user_id,
                "status": "active",
                "paystack_customer_code": payload["data"]["customer"]["customer_code"],
            }
        ).execute()

    return {"received": True}


def require_active_subscription(user=Depends(require_user)):
    """Dependency for paid-tier routes (upload, generate-from-doc)."""
    result = (
        supabase.table("subscriptions")
        .select("status")
        .eq("user_id", user.id)
        .eq("status", "active")
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=402, detail="Upload requires an active subscription")
    return user
