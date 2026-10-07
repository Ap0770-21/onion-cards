import os
from datetime import datetime, timezone
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
                "callback_url": "https://onion.cards/subscription/callback",
                "metadata": {"user_id": user.id, "plan": "active"},
            },
        )
    data = resp.json()
    if not data.get("status"):
        raise HTTPException(status_code=502, detail="Could not start checkout")
    return {"authorization_url": data["data"]["authorization_url"]}


@router.post("/checkout-founder")
async def create_founder_checkout(user=Depends(require_user)):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{PAYSTACK_BASE}/transaction/initialize",
            headers={"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"},
            json={
                "email": user.email,
                "amount": 500000,  # ₦5000.00 in kobo
                "callback_url": "https://onion.cards/subscription/callback",
                "metadata": {"user_id": user.id, "plan": "founder"},
            },
        )
    data = resp.json()
    if not data.get("status"):
        raise HTTPException(status_code=502, detail="Could not start checkout")
    return {"authorization_url": data["data"]["authorization_url"]}


def _build_update(user_id: str, plan: str, customer_code: str) -> dict:
    update_payload = {
        "user_id": user_id,
        "status": "founder" if plan == "founder" else "active",
        "paystack_customer_code": customer_code,
    }
    if plan == "founder":
        update_payload["is_founder"] = True
    return update_payload


@router.post("/webhook")
async def paystack_webhook(request: Request):
    payload = await request.json()
    event = payload.get("event")

    if event == "charge.success":
        user_id = payload["data"]["metadata"]["user_id"]
        plan = payload["data"]["metadata"].get("plan", "active")
        customer_code = payload["data"]["customer"]["customer_code"]
        supabase.table("subscriptions").upsert(_build_update(user_id, plan, customer_code)).execute()

    return {"received": True}


@router.get("/verify/{reference}")
async def verify_transaction(reference: str, user=Depends(require_user)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{PAYSTACK_BASE}/transaction/verify/{reference}",
            headers={"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"},
        )
    data = resp.json()
    if data["data"]["status"] == "success":
        plan = data["data"]["metadata"].get("plan", "active")
        customer_code = data["data"]["customer"]["customer_code"]
        update_payload = _build_update(user.id, plan, customer_code)
        supabase.table("subscriptions").upsert(update_payload).execute()
        return {"status": update_payload["status"]}
    return {"status": data["data"]["status"]}


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
    if sub["status"] in ("active", "founder"):
        return user
    if sub["status"] == "trial" and sub["current_period_end"]:
        end = datetime.fromisoformat(sub["current_period_end"].replace("Z", "+00:00"))
        if end > datetime.now(timezone.utc):
            return user

    raise HTTPException(status_code=402, detail="Subscription required — trial ended or inactive")


@router.get("/status")
def get_subscription_status(user=Depends(require_user)):
    result = supabase.table("subscriptions").select("status, current_period_end, is_founder").eq("user_id", user.id).execute()
    if not result.data:
        return {"status": "inactive", "has_access": False}
    sub = result.data[0]
    has_access = sub["status"] in ("active", "founder")
    if sub["status"] == "trial" and sub["current_period_end"]:
        end = datetime.fromisoformat(sub["current_period_end"].replace("Z", "+00:00"))
        has_access = end > datetime.now(timezone.utc)
    return {**sub, "has_access": has_access}
