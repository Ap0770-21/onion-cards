from fastapi import APIRouter, HTTPException
from supabase_client import supabase

router = APIRouter()


@router.get("/{share_token}")
def get_shared_deck(share_token: str):
    batch = supabase.table("generation_batches").select("*").eq("share_token", share_token).eq("share_enabled", True).execute()
    if not batch.data:
        raise HTTPException(status_code=404, detail="This deck isn't available or sharing was turned off.")

    b = batch.data[0]
    cards = supabase.table("cards").select("question, answer").eq("batch_id", b["id"]).execute()
    return {"topic": b["topic"], "overview": b["overview"], "cards": cards.data}
