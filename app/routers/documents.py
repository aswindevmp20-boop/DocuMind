from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.document import Document
from app.models.chunk import Chunk
from app.utils.chunking import chunk_text
from app.services.embedding_service import generate_embeddings
import io
from PyPDF2 import PdfReader

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def extract_text(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid file name")

    content = await file.read()
    filename = file.filename.lower()

    # TXT support
    if filename.endswith(".txt"):
        return content.decode("utf-8")

    # PDF support
    if filename.endswith(".pdf"):
        pdf_reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
        return text

    raise HTTPException(status_code=400, detail="Unsupported file type")


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    text = await extract_text(file)
    print("Filename:", file.filename)
    print("Extracted text type:", type(text))
    print("First 100 chars:", text[:100] if text else "None")

    # Save document metadata
    document = Document(name=file.filename)
    db.add(document)
    db.commit()
    db.refresh(document)

    # Chunk text
    chunks = chunk_text(text)

    # Save chunks
    chunk_ids = []
    for chunk_text_content in chunks:
        chunk = Chunk(  
            document_id=document.id,
            content=chunk_text_content,
        )
        db.add(chunk)
        db.commit()
        db.refresh(chunk)
        chunk_ids.append(chunk.id)

    embeddings = generate_embeddings(chunks)

    for chunk_id, embedding in zip(chunk_ids, embeddings):
        db_chunk = db.query(Chunk).filter(Chunk.id == chunk_id).first()
        db_chunk.embedding = embedding.tolist()

    db.commit()

    return {
        "message": "Document processed",
        "document_id": document.id,
        "chunks_created": len(chunks),
    }