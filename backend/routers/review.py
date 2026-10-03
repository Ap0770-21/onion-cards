from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from routers.auth import require_user
from supabase_client import supabase

router = APIRouter()
LAGOS = ZoneInfo("Africa/Lagos")


def today_lagos() -> str:
    return datetime.now(LAGOS).date().isoformat()


@router.get("/queue")
def get_queue(limit: int = 40, user=Depends(require_user)):
    now = datetime.now(timezone.utc).isoformat()
    result = (
        supabase.table("card_reviews")
        .select("card_id, due_at, ease, cards(question, answer, batch_id)")
        .eq("user_id", user.id)
        .lte("due_at", now)
        .order("due_at")
        .order("ease")
        .limit(limit)
        .execute()
    )
    return result.data


class AnswerRequest(BaseModel):
    card_id: str
    result: str  # "got_it" or "missed"


@router.post("/answer")
def answer_card(req: AnswerRequest, user=Depends(require_user)):
    if req.result not in ("got_it", "missed"):
        raise HTTPException(status_code=400, detail="result must be 'got_it' or 'missed'")

    existing = (
        supabase.table("card_reviews")
        .select("*")
        .eq("user_id", user.id)
        .eq("card_id", req.card_id)
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Review record not found")
    row = existing.data[0]

    if req.result == "missed":
        new_interval = 1
        new_reps = 0
        new_ease = max(1.3, row["ease"] - 0.2)
    else:
        old_reps = row["reps"]
        new_reps = old_reps + 1
        new_ease = row["ease"]
        if old_reps == 0:
            new_interval = 3
        elif old_reps == 1:
            new_interval = 7
        else:
            new_interval = max(1, round(row["interval_days"] * row["ease"]))

    due_at = (datetime.now(timezone.utc) + timedelta(days=new_interval)).isoformat()

    supabase.table("card_reviews").update({
        "interval_days": new_interval,
        "reps": new_reps,
        "ease": new_ease,
        "due_at": due_at,
        "last_reviewed_at": datetime.now(timezone.utc).isoformat(),
    }).eq("user_id", user.id).eq("card_id", req.card_id).execute()

    day = today_lagos()
    today_row = supabase.table("review_days").select("count").eq("user_id", user.id).eq("day", day).execute()
    if today_row.data:
        supabase.table("review_days").update({"count": today_row.data[0]["count"] + 1}).eq("user_id", user.id).eq("day", day).execute()
    else:
        supabase.table("review_days").insert({"user_id": user.id, "day": day, "count": 1}).execute()

    return {"interval_days": new_interval, "ease": new_ease, "due_at": due_at}


@router.get("/summary")
def get_summary(user=Depends(require_user)):
    now = datetime.now(timezone.utc).isoformat()
    due = (
        supabase.table("card_reviews")
        .select("card_id, cards(batch_id)")
        .eq("user_id", user.id)
        .lte("due_at", now)
        .execute()
    )
    total_due = len(due.data)

    per_deck = {}
    for row in due.data:
        batch_id = row["cards"]["batch_id"] if row.get("cards") else None
        if batch_id:
            per_deck[batch_id] = per_deck.get(batch_id, 0) + 1

    streak = 0
    day = datetime.now(LAGOS).date()
    while True:
        r = supabase.table("review_days").select("count").eq("user_id", user.id).eq("day", day.isoformat()).execute()
        if r.data and r.data[0]["count"] > 0:
            streak += 1
            day -= timedelta(days=1)
        else:
            break

    return {"total_due": total_due, "per_deck_due": per_deck, "streak": streak}
