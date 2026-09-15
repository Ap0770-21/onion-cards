def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Naive word-based chunking with overlap. Good enough for v1 — swap for a
    sentence-aware splitter later if retrieval quality needs it."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start = end - overlap
    return chunks


def extract_pdf_text(file_bytes: bytes) -> str:
    from pypdf import PdfReader
    from io import BytesIO

    reader = PdfReader(BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)
