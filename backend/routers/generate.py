import os
import json
import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from routers.auth import get_current_user
from supabase_client import supabase

router = APIRouter()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You generate study flashcards. Given a topic, return STRICT JSON only, no prose:
{
  "overview": "2-3 sentence summary of the topic",
  "cards": [{"question": "...", "answer": "..."}, ...]
}
Generate 8-12 cards. Questions should be specific and testable, answers concise."""


class GenerateRequest(BaseModel):
    topic: str


@router.post("")
async def generate_cards(req: GenerateRequest, user=Depends(get_current_user)):
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": req.topic},
                ],
                "response_format": {"type": "json_object"},
            },
        )
    raw = resp.json()["choices"][0]["message"]["content"]
    parsed = json.loads(raw)

    batch_id = None
    if user is not None:
        batch = (
            supabase.table("generation_batches")
            .insert(
                {
                    "user_id": user.id,
                    "topic": req.topic,
                    "overview": parsed["overview"],
                    "source_type": "prompt",
                }
            )
            .execute()
        )
        batch_id = batch.data[0]["id"]
        rows = [
            {"user_id": user.id, "batch_id": batch_id, "question": c["question"], "answer": c["answer"]}
            for c in parsed["cards"]
        ]
        supabase.table("cards").insert(rows).execute()

    return {"batch_id": batch_id, "overview": parsed["overview"], "cards": parsed["cards"], "source": None}
