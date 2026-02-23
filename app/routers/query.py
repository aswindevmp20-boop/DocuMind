from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.chunk import Chunk
from app.models.document import Document
from app.services.embedding_service import generate_embeddings
from app.services.llm_service import generate_answer

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# @router.post("/")
# def query(question: str, db: Session = Depends(get_db)):

#     embedding = generate_embeddings([question])[0]

#     semantic_results = search(embedding, top_k=10)

#     ranked_results = []

#     for result in semantic_results:
#         chunk = db.query(Chunk).filter(Chunk.id == result["chunk_id"]).first()

#         if not chunk:
#             continue

#         k_score = keyword_score(question, chunk.content)

#         hybrid_score = (
#             0.7 * (1 / (1 + result["semantic_score"])) +   # convert L2 to similarity
#             0.3 * k_score
#         )

#         ranked_results.append({
#             "chunk": chunk,
#             "hybrid_score": hybrid_score
#         })

#     ranked_results.sort(key=lambda x: x["hybrid_score"], reverse=True)

#     top_chunks = ranked_results[:5]

#     chunk_texts = [item["chunk"].content for item in top_chunks]

#     answer = generate_answer(chunk_texts, question)

#     citations = []

#     for item in top_chunks:
#         chunk = item["chunk"]
#         document = db.query(Document).filter(Document.id == chunk.document_id).first()

#         citations.append({
#             "document_name": document.name if document else "Unknown",
#             "chunk_id": chunk.id,
#             "preview": chunk.content[:200]
#         })

#     return {
#         "answer": answer,
#         "citations": citations
#     }

def keyword_score(query: str, text: str) -> float:
    query_terms = query.lower().split()
    text_lower = text.lower()

    matches = sum(1 for term in query_terms if term in text_lower)
    return matches / len(query_terms) if query_terms else 0

from app.models.query import Query
from app.services.query_service import enqueue_query


@router.post("/")
def submit_query(question: str, db: Session = Depends(get_db)):

    query = Query(question=question, status="PENDING")
    db.add(query)
    db.commit()
    db.refresh(query)

    enqueue_query(query.id)

    return {
        "query_id": query.id,
        "status": query.status
    }

@router.get("/{query_id}")
def get_query_status(query_id: int, db: Session = Depends(get_db)):

    query = db.query(Query).filter(Query.id == query_id).first()

    if not query:
        return {"error": "Query not found"}

    return {
        "query_id": query.id,
        "status": query.status,
        "answer": query.answer,
        "latency_ms": query.latency_ms
    }