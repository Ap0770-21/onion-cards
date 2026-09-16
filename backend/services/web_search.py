import os
import httpx

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")


async def web_search(query: str, max_results: int = 5) -> list[str]:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            "https://api.tavily.com/search",
            json={"api_key": TAVILY_API_KEY, "query": query, "max_results": max_results},
        )
    data = resp.json()
    return [r["content"] for r in data.get("results", [])]
