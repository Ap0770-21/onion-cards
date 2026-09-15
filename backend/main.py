import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import auth, generate, upload, cards, billing

load_dotenv()

app = FastAPI(title="onion.cards API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_URL", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(generate.router, prefix="/generate", tags=["generate"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(cards.router, prefix="/cards", tags=["cards"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])


@app.get("/health")
def health():
    return {"status": "ok"}
