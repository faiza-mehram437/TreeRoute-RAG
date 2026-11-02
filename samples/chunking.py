"""Page-aware text chunking for retrieval (sample from TreeRoute).

Each page is chunked separately so every chunk, and so every citation, maps to one page.
Chunks overlap so a sentence cut at a boundary still appears whole in one chunk.
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source: str
    page: int


def chunk_text(text: str, size: int = 1000, overlap: int = 200) -> list[str]:
    """Split text into ~size-character chunks that overlap by ~overlap characters.

    Chunks end on a word boundary where possible so words are not cut in half.
    """
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            space = text.rfind(" ", start + size // 2, end)
            if space != -1:
                end = space
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        next_start = max(end - overlap, start + 1)
        # Begin the overlap at the next word, not mid-word.
        space = text.find(" ", next_start - 1, end)
        start = space + 1 if space != -1 and text[next_start - 1] != " " else next_start
    return chunks


def chunk_pages(
    pages: list[tuple[int, str]], source: str, size: int = 1000, overlap: int = 200
) -> list[Chunk]:
    """Chunk each page separately so every chunk can be cited by page number."""
    chunks = []
    for page, text in pages:
        for i, piece in enumerate(chunk_text(text, size, overlap)):
            chunks.append(Chunk(id=f"{source}:p{page}:c{i}", text=piece, source=source, page=page))
    return chunks
