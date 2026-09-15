from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from routers.auth import require_user
from supabase_client import supabase

router = APIRouter()


class CardUpdate(BaseModel):
    question: str | None = None
    answer: str | None = None
    favorite: bool | None = None


@router.get("")
def list_cards(user=Depends(require_user)):
    result = supabase.table("cards").select("*").eq("user_id", user.id).order("created_at", desc=True).execute()
    return result.data


@router.patch("/{card_id}")
def update_card(card_id: str, update: CardUpdate, user=Depends(require_user)):
    payload = {k: v for k, v in update.model_dump().items() if v is not None}
    if not payload:
        raise HTTPException(status_code=400, detail="Nothing to update")
    result = (
        supabase.table("cards")
        .update(payload)
        .eq("id", card_id)
        .eq("user_id", user.id)  # ensures users can only edit their own cards
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Card not found")
    return result.data[0]
