from typing import List


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> List[str]:
    """
    Splits text into overlapping chunks.

    Args:
        text (str): Full document text
        chunk_size (int): Max characters per chunk
        chunk_overlap (int): Overlap between chunks

    Returns:
        List[str]: List of text chunks
    """

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    text = text.strip()
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())

        start += chunk_size - chunk_overlap

    return chunks