import os
import httpx

EMBEDDING_API_KEY = os.environ.get("EMBEDDING_API_KEY")

# NOTE: fill this in once you've picked an embedding provider (Cohere / Gemini
# embeddings / similar). Must match the `vector(N)` dimension in schema.sql.


async def embed_text(text: str) -> list[float]:
    """Returns an embedding vector for a single string. Replace the body below
    with the real provider call once EMBEDDING_API_KEY is set."""
    raise NotImplementedError("Wire up your chosen embedding provider here")


async def embed_batch(texts: list[str]) -> list[list[float]]:
    return [await embed_text(t) for t in texts]
