def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100):
    """
    Simple sliding window chunking.
    Good enough for MVP RAG.
    """

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap  # overlap for context continuity

    return chunks