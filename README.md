# onion.cards — Day 1 Setup

## What's here
FastAPI backend (auth, generate, upload/RAG, cards, billing) — all code is
yours, no platform lock-in. Frontend is being built separately in Lovable.

## 1. Supabase project
1. Create a project at supabase.com (free tier is fine to start).
2. In the SQL editor, run `backend/schema.sql` — enables pgvector and
   creates all tables (generation_batches, cards, document_chunks, subscriptions)
   with row-level security so users only see their own data.
3. Copy your Project URL and keys into `backend/.env`:
   `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY`.

## 2. Groq (flashcard generation)
Free API key at console.groq.com → `GROQ_API_KEY` in `backend/.env`.

## 3. Embeddings (needed for upload/RAG)
Pick a provider (Cohere free tier or Gemini embeddings) and fill in
`services/embeddings.py`. The `vector(768)` dimension in `schema.sql` assumes
a 768-dim model — adjust both to match if your provider differs.

## 4. Paystack
Secret key from the Paystack dashboard → `PAYSTACK_SECRET_KEY` in
`backend/.env`. Checkout amount in `routers/billing.py` is a placeholder.

## 5. Running locally in Termux
cd backend
pip install -r requirements.txt --break-system-packages
cp .env.example .env
uvicorn main:app --reload

## What's stubbed vs. real
- /generate — fully wired, works once Groq + Supabase keys are set.
- /upload/document, /upload/generate-from-doc — wired end-to-end, but
  services/embeddings.py needs your provider's API call filled in first.
- /billing/checkout, /billing/webhook — wired to Paystack's real API;
  webhook signature verification still needs implementing before going live.

## Deploy
- Backend → Render (free tier while testing, Starter $7/mo before sharing the link)
- Frontend → wherever Lovable deploys to
- Point onion.cards DNS at the frontend host; set the API base URL to the
  deployed backend.
