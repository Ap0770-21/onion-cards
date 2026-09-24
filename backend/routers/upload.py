import os
import json
import httpx
from fastapi import APIRouter, Depends, UploadFile, File, Form
from routers.billing import require_active_subscription
from services.chunking import chunk_text, extract_pdf_text
from services.embeddings import embed_batch
from services.retrieval import retrieve_relevant_chunks
from supabase_client import supabase

router = APIRouter()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

RAG_SYSTEM_PROMPT = """You generate study flashcards STRICTLY grounded in the provided
source passages. Return STRICT JSON only:
{"overview": "...", "cards": [{"question": "...", "answer": "..."}, ...]}
Only use facts present in the passages. Generate 20 cards."""


@router.post("/document")
async def upload_document(file: UploadFile = File(...), user=Depends(require_active_subscription)):
    raw_bytes = await file.read()
    text = extract_pdf_text(raw_bytes) if file.filename.endswith(".pdf") else raw_bytes.decode("utf-8", errors="ignore")

    chunks = chunk_text(text)
    embeddings = await embed_batch(chunks)
    if not chunks:
        raise HTTPException(status_code=422, detail="No readable text found in this document. Scanned/image-based PDFs aren't supported yet — try a text-based PDF or a .txt file.")

    rows = [
        {"user_id": user.id, "document_name": file.filename, "content": c, "embedding": e}
        for c, e in zip(chunks, embeddings)
    ]
    supabase.table("document_chunks").insert(rows).execute()

    return {"document_name": file.filename, "chunks_stored": len(chunks)}


@router.post("/generate-from-doc")
async def generate_from_doc(topic: str = Form(...), user=Depends(require_active_subscription)):
    matches = await retrieve_relevant_chunks(user.id, topic)
    context = "\n\n---\n\n".join(m["content"] for m in matches)

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "openai/gpt-oss-20b",
                "messages": [
                    {"role": "system", "content": RAG_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Topic: {topic}\n\nSource passages:\n{context}"},
                ],
                "response_format": {"type": "json_object"},
            },
        )
    parsed = json.loads(resp.json()["choices"][0]["message"]["content"])

    batch = (
        supabase.table("generation_batches")
        .insert(
            {
                "user_id": user.id,
                "topic": topic,
                "overview": parsed["overview"],
                "source_type": "upload",
                "chunk_ids": [m["id"] for m in matches],
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

    # Batch-level source reference — not per-card attribution (see project notes)
    source_docs = list({m["document_name"] for m in matches})
    return {
        "batch_id": batch_id,
        "overview": parsed["overview"],
        "cards": parsed["cards"],
        "source": {"documents": source_docs, "passages": [m["content"] for m in matches]},
    }
