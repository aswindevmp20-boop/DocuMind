Overview

DocuMind is a scalable Retrieval-Augmented Generation (RAG) backend system that enables intelligent question answering over uploaded documents.

It combines:

    Semantic Search (pgvector embeddings)

    Keyword-based ranking

    LLM answer generation

    Asynchronous job processing (Redis + worker)

Fully Dockerized architecture

The system retrieves relevant document chunks using hybrid ranking and generates contextual answers using an LLM.

Architecture

    Client
    │
    ▼
    FastAPI (API Layer)
    │
    ├── PostgreSQL (pgvector) → Stores documents, chunks, embeddings
    │
    ├── Redis → Queue for async query processing
    │
    └── Worker Service
            ├── Generate Embeddings
            ├── Hybrid Retrieval (Semantic + Keyword)
            └── LLM Answer Generation
        How It Works
        Document Ingestion

Documents are split into chunks.

Each chunk is embedded using sentence-transformers/all-MiniLM-L6-v2.

Embeddings are stored in PostgreSQL using pgvector.

    Query Submission

User submits a question via API.

Query is stored with PENDING status.

Query ID is pushed to Redis queue.

    Async Processing (Worker)

The worker:

    Generates embedding for the question

    Performs vector similarity search using pgvector

    Computes keyword score

    Combines scores using hybrid ranking

    Selects top chunks

    Generates final answer via LLM

    Updates query status to COMPLETED

        Tech Stack

Backend: FastAPI

Database: PostgreSQL 15 + pgvector

Queue: Redis

Embeddings: SentenceTransformers (MiniLM)

LLM: OpenAI-compatible / local LLM service

ORM: SQLAlchemy

Containerization: Docker & Docker Compose

Project Structure

    app/
    ├── main.py
    ├── database.py
    ├── models/
    │     ├── document.py
    │     ├── chunk.py
    │     └── query.py
    ├── routers/
    │     ├── documents.py
    │     └── query.py
    ├── services/
    │     ├── embedding_service.py
    │     ├── vector_search.py
    │     ├── llm_service.py
    │     └── query_service.py
    └── workers/
        └── query_worker.py

Setup Instructions

    Clone the repository
        git clone https://github.com/yourusername/documind.git
        cd documind
    Create .env file
        DATABASE_URL=postgresql://postgres:postgres@db:5432/documind
        REDIS_URL=redis://redis:6379
        OPENAI_API_KEY=your_key_here
    Run with Docker
        docker compose up --build

Services:

    API → http://localhost:8000

    PostgreSQL (pgvector)

    Redis

    Worker

Example API Usage

    Submit Query
    POST /query

    Request:

        {
        "question": "What is the scope of application?"
        }

    Response:

        {
        "query_id": 1,
        "status": "PENDING"
        }

    Get Query Result

    GET /query/1

    Response:

        {
        "query_id": 1,
        "status": "COMPLETED",
        "answer": "...generated answer...",
        "latency_ms": 41817
        }

Hybrid Ranking Strategy

    Final ranking score:

        Hybrid Score = 0.8 * Semantic Similarity + 0.2 * Keyword Score

        This improves retrieval precision by combining vector similarity and lexical matching.

Performance Features

    Async job processing using Redis

    Latency tracking per query

    Top-K vector similarity search

    Efficient embedding storage with pgvector

Key Engineering Highlights

    Designed full async RAG pipeline

    Implemented pgvector similarity search using raw SQL

    Built hybrid ranking logic

    Solved Docker service orchestration issues

    Handled DB readiness & extension setup

    Implemented clean separation of services and routers
