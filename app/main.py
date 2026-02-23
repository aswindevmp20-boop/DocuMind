from fastapi import FastAPI
from app.database import Base, engine

from app.models.document import Document
from app.models.chunk import Chunk
from app.models.query import Query
from app.routers import documents, query

app = FastAPI(title="DocuMind - Enterprise RAG")

Base.metadata.create_all(bind=engine)

app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(query.router, prefix="/query", tags=["Query"])

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}