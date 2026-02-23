from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np 
import threading

_model = None
_model_lock = threading.Lock()

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

def get_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model

def generate_embeddings(texts: List[str]) -> np.ndarray:
    """
    Generate embeddings for a list of texts.
    Returns numpy array of shape (n, 384)
    """
    model = get_model()
    embeddings = model.encode(
        texts,
        convert_to_numpy = True,
        normalize_embeddings = True
    )
    return embeddings
    