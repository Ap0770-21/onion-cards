import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from supabase_client import supabase
from routers.auth import require_user
from datetime import datetime, timezone

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
    result = (
        supabase.table("subscriptions")
        .select("status, current_period_end")
        .eq("user_id", user.id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=402, detail="Subscription required")

    sub = result.data[0]
    if sub["status"] == "active":
        return user
    if sub["status"] == "trial" and sub["current_period_end"]:
        end = datetime.fromisoformat(sub["current_period_end"].replace("Z", "+00:00"))
        if end > datetime.now(timezone.utc):
            return user

    raise HTTPException(status_code=402, detail="Subscription required — trial ended or inactive")


@router.get("/status")
def get_subscription_status(user=Depends(require_user)):
    result = supabase.table("subscriptions").select("status, current_period_end").eq("user_id", user.id).execute()
    if not result.data:
        return {"status": "inactive", "has_access": False}
    sub = result.data[0]
    has_access = sub["status"] == "active"
    if sub["status"] == "trial" and sub["current_period_end"]:
        end = datetime.fromisoformat(sub["current_period_end"].replace("Z", "+00:00"))
        has_access = end > datetime.now(timezone.utc)
    return {**sub, "has_access": has_access}
