import os
from groq import Groq
from typing import List
import os
from dotenv import load_dotenv

GROQ_MODEL = "llama-3.3-70b-versatile"

_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set in enviornment variables.")
        _client = Groq(api_key=api_key)
    return _client

def build_prompt(context_chunks: List[str], question: str) -> str:
    context = "\n\n".join(context_chunks)

    return f"""
    You are an enterprise knowledge assistant.

    Answer the question strictly using the provided context.
    If the answer is not found in the context, say "Information not available in provided documents."

    Context:
    {context}

    Question:
    {question}

    Answer:
    """.strip()

def generate_answer(context_chunks: List[str], question: str) -> str:
    client = get_client()
    prompt = build_prompt(context_chunks, question)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role":"system", "content":" You are a helpful enterprise AI assistant."},
            {"role":"user", "content": prompt}
        ],
        temperature = 0.2,
    )

    return response.choices[0].message.content.strip()