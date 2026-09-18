from supabase_client import supabase
from services.embeddings import embed_text


async def retrieve_relevant_chunks(user_id: str, query: str, top_k: int = 5):
    """
    Calls the match_document_chunks Postgres function (see schema.sql) which
    does the pgvector cosine-distance search, scoped to this user's documents.
    """
    query_embedding = await embed_text(query, input_type="search_query")
    result = supabase.rpc(
        "match_document_chunks",
        {
            "query_embedding": query_embedding,
            "match_user_id": user_id,
            "match_count": top_k,
        },
    ).execute()
    return result.data  # list of {id, document_name, content, similarity}
