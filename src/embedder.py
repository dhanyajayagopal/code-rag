from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
from .models import CodeChunk

class CodeEmbedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the embedding model"""
        self.model = SentenceTransformer(model_name)
    
    def create_searchable_text(self, chunk: CodeChunk) -> str:
        """Create text optimized for semantic search"""
        searchable_parts = [
            f"This is a {chunk.chunk_type.split(':')[0]}",
            f"from file {chunk.file_path}",
            chunk.content
        ]
        
        if ':' in chunk.chunk_type:
            name = chunk.chunk_type.split(':')[1]
            searchable_parts.insert(1, f"named {name}")
        
        return " ".join(searchable_parts)
    
    def embed_chunks(self, chunks: List[CodeChunk]) -> np.ndarray:
        """Generate embeddings for a list of code chunks"""
        searchable_texts = [self.create_searchable_text(chunk) for chunk in chunks]
        embeddings = self.model.encode(searchable_texts)
        return embeddings
    
    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a search query"""
        return self.model.encode([query])[0]