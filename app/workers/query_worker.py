import time
from app.database import SessionLocal
from app.models.query import Query
from app.models.chunk import Chunk
from app.models.document import Document
from app.services.query_service import dequeue_query
from app.services.embedding_service import generate_embeddings
from app.services.llm_service import generate_answer
from app.routers.query import keyword_score
from app.services.vector_search import search_similar_chunks

def process_query(query_id: int):
    db = SessionLocal()

    try:
        query = db.query(Query).filter(Query.id == query_id).first()
        if not query:
            return

        start_time = time.time()

        # Generate embedding
        embedding = generate_embeddings([query.question])[0]

        # Semantic search
        semantic_results = search_similar_chunks(db, embedding, top_k=10)

        ranked_results = []

        for result in semantic_results:
            chunk = db.query(Chunk).filter(Chunk.id == result["chunk_id"]).first()
            if not chunk:
                continue

            # Keyword score
            k_score = keyword_score(query.question, chunk.content)

            # Convert distance → similarity
            semantic_similarity = 1 / (1 + result["semantic_score"])

            # Hybrid score
            hybrid_score = 0.8 * semantic_similarity + 0.2 * k_score

            ranked_results.append((chunk, hybrid_score))

        # Sort AFTER loop
        ranked_results.sort(key=lambda x: x[1], reverse=True)

        top_chunks = ranked_results[:3]

        chunk_texts = [chunk.content for chunk, _ in top_chunks]

        # Generate answer
        answer = generate_answer(chunk_texts, query.question)

        latency = int((time.time() - start_time) * 1000)

        # Update DB
        query.answer = answer
        query.status = "COMPLETED"
        query.latency_ms = latency

        db.commit()

    except Exception as e:
        query.status = "FAILED"
        db.commit()
        print("Worker error:", e)

    finally:
        db.close()

def start_worker():
    print("Worker starting...")
    time.sleep(5)   # give DB + Redis time to initialize
    print("Worker ready.")

    while True:
        job = dequeue_query()
        if not job:
            time.sleep(1)
            continue

        print("Processing job:", job)
        process_query(job["query_id"])

if __name__ == "__main__":
    start_worker()
