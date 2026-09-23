import os
import httpx

COHERE_API_KEY = os.environ.get("COHERE_API_KEY")


async def embed_text(text: str, input_type: str = "search_document") -> list[float]:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            "https://api.cohere.com/v1/embed",
            headers={"Authorization": f"Bearer {COHERE_API_KEY}"},
            json={"texts": [text], "model": "embed-english-v3.0", "input_type": input_type},
        )
    data = resp.json()
    if "embeddings" not in data:
        raise RuntimeError(f"Cohere embed error (text): {data}")
    return data["embeddings"][0]


async def embed_batch(texts: list[str], input_type: str = "search_document") -> list[list[float]]:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.cohere.com/v1/embed",
            headers={"Authorization": f"Bearer {COHERE_API_KEY}"},
            json={"texts": texts, "model": "embed-english-v3.0", "input_type": input_type},
        )
    data = resp.json()
    if "embeddings" not in data:
        raise RuntimeError(f"Cohere embed error (batch): {data}")
    return data["embeddings"]
