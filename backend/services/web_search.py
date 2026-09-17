import os
import httpx

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")


async def web_search(query: str, max_results: int = 5) -> list[str]:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            "https://serpapi.com/search",
            params={"q": query, "api_key": SERPAPI_KEY, "engine": "google", "num": max_results},
        )
    data = resp.json()
    organic = data.get("organic_results", [])
    return [r.get("snippet", "") for r in organic if r.get("snippet")]
