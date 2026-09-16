import os
import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from routers.billing import require_active_subscription
from supabase_client import supabase
from services.embeddings import embed_text

router = APIRouter()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class ChatRequest(BaseModel):
    batch_id: str
    message: str


async def _ensure_deck_embedded(batch_id: str, user_id: str):
    existing = supabase.table("card_chunks").select("id").eq("batch_id", batch_id).execute()
    if existing.data:
        return
    cards = supabase.table("cards").select("question, answer").eq("batch_id", batch_id).execute()
    rows = []
    for c in cards.data:
        text = f"Q: {c['question']} A: {c['answer']}"
        embedding = await embed_text(text)
        rows.append({"user_id": user_id, "batch_id": batch_id, "content": text, "embedding": embedding})
    if rows:
        supabase.table("card_chunks").insert(rows).execute()


@router.post("")
async def chat_with_deck(req: ChatRequest, user=Depends(require_active_subscription)):
    await _ensure_deck_embedded(req.batch_id, user.id)

    query_embedding = await embed_text(req.message)
    result = supabase.rpc(
        "match_card_chunks",
        {"query_embedding": query_embedding, "match_batch_id": req.batch_id, "match_count": 5},
    ).execute()
    context = "\n".join(r["content"] for r in result.data)

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "Answer using only the flashcard context provided. If the context doesn't cover the question, say so."},
                    {"role": "user", "content": f"Flashcard context:\n{context}\n\nQuestion: {req.message}"},
                ],
            },
        )
    return {"answer": resp.json()["choices"][0]["message"]["content"]}
