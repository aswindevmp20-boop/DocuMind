from sqlalchemy import text
from app.models.chunk import Chunk


def search_similar_chunks(db, embedding, top_k=5):
    # Convert embedding list to Postgres vector format
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"

    sql = text("""
        SELECT id, document_id, content,
               embedding <-> :embedding AS distance
        FROM chunks
        ORDER BY embedding <-> :embedding
        LIMIT :limit
    """)

    result = db.execute(sql, {
        "embedding": embedding_str,
        "limit": top_k
    })

    rows = result.fetchall()

    return [
        {
            "chunk_id": row[0],
            "document_id": row[1],
            "content": row[2],
            "semantic_score": float(row[3])
        }
        for row in rows
    ]