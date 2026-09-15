# onion.cards — Day 1 Setup

## What's here
Full repo skeleton matching the spec: FastAPI backend (auth, generate, upload/RAG,
cards, billing) + React/Vite/Tailwind PWA frontend. All code is yours — no
platform lock-in, just push this to your own GitHub repo.

## 1. Supabase project
1. Create a project at supabase.com (free tier is fine to start).
2. In the SQL editor, run `backend/schema.sql` — this enables pgvector and
   creates all tables (generation_batches, cards, document_chunks, subscriptions)
   with row-level security so users can only see their own data.
3. Copy your Project URL and keys:
   - `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` → `backend/.env`
   - `VITE_SUPABASE_URL` + the **anon/public** key (not service role!) → `frontend/.env`

## 2. Groq (flashcard generation)
Get a free API key at console.groq.com → `GROQ_API_KEY` in `backend/.env`.

## 3. Embeddings (needed for upload/RAG — can wait until Day 5-6)
Pick a provider (Cohere free tier or Gemini embeddings both work) and fill in
`services/embeddings.py`. The `vector(768)` dimension in `schema.sql` assumes
a 768-dim model — adjust both to match if your provider differs.

## 4. Paystack
Get your secret key from the Paystack dashboard → `PAYSTACK_SECRET_KEY` in
`backend/.env`. The checkout amount in `routers/billing.py` is a placeholder —
set your real price there.

## 5. Running locally in Termux
```bash
# Backend
cd backend
pip install -r requirements.txt --break-system-packages
cp .env.example .env   # then fill in your keys
uvicorn main:app --reload

# Frontend (separate Termux session or tmux pane)
cd frontend
npm install
cp .env.example .env   # then fill in your keys
npm run dev
```

## 6. Git
```bash
git init
git add .
git commit -m "Day 1: repo scaffold, Supabase schema, Paystack subscription gate"
# create an empty repo on GitHub first, then:
git remote add origin <your-repo-url>
git push -u origin main
```

## What's stubbed vs. real
- `/generate` (free path) — fully wired, works once Groq + Supabase keys are set.
- `/upload/document`, `/upload/generate-from-doc` — wired end-to-end, but
  `services/embeddings.py` needs your chosen provider's API call filled in
  before it'll run (Day 5-6 per the spec).
- `/billing/checkout`, `/billing/webhook` — wired to Paystack's real API;
  webhook signature verification is noted but not yet implemented — add before
  going live (don't trust unverified webhook payloads in production).
- Icons (`icon-192.png`, `icon-512.png`) — placeholders needed in
  `frontend/public/` before the PWA manifest is fully valid (Day 7, logo day).

## Deploy (Day 8)
- Backend → Render (start on free tier, flip to Starter $7/mo before sharing the link)
- Frontend → Vercel or Netlify (free)
- Point onion.cards DNS at your frontend host; set `VITE_API_BASE` to your
  deployed backend URL.
