import os
import json
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from routers.auth import get_current_user
from routers.billing import require_active_subscription
from services.web_search import web_search
from supabase_client import supabase

router = APIRouter()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You generate study flashcards. Given a topic (and optional
web search context), return STRICT JSON only, no prose:
{
  "overview": "2-3 sentence summary of the topic",
  "cards": [{"question": "...", "answer": "..."}, ...]
}
Generate 8-12 cards. Questions should be specific and testable, answers concise."""


class GenerateRequest(BaseModel):
    topic: str
    use_web_search: bool = False


@router.post("")
async def generate_cards(req: GenerateRequest, user=Depends(get_current_user)):
    web_context = ""
    if req.use_web_search:
        # Premium-gated: require an active subscription for this path only
        require_active_subscription(user=user)
        results = await web_search(req.topic)
        web_context = "\n\n".join(results)

    user_content = req.topic if not web_context else f"Topic: {req.topic}\n\nWeb search context:\n{web_context}"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "openai/gpt-oss-20b",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                "response_format": {"type": "json_object"},
            },
        )
    groq_response = resp.json()
if "choices" not in groq_response:
    raise HTTPException(status_code=502, detail=f"Groq error: {groq_response}")
raw = groq_response["choices"][0]["message"]["content"]
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
