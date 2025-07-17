import chromadb
from chromadb.config import Settings
import numpy as np
from typing import List, Tuple
from .models import CodeChunk, SearchResult

class VectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB for storing code embeddings"""
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="code_chunks",
            metadata={"description": "Code chunks with embeddings"}
        )
    
    def add_chunks(self, chunks: List[CodeChunk], embeddings: np.ndarray):
        """Add code chunks and their embeddings to the vector store"""
        
        ids = [chunk.id for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = [
            {
                "file_path": chunk.file_path,
                "chunk_type": chunk.chunk_type,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line
            }
            for chunk in chunks
        ]
        
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query_embedding: np.ndarray, n_results: int = 5) -> List[SearchResult]:
        """Search for similar code chunks"""
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results
        )
        
        search_results = []
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            chunk = CodeChunk(
                file_path=metadata['file_path'],
                content=results['documents'][0][i],
                start_line=metadata['start_line'],
                end_line=metadata['end_line'],
                chunk_type=metadata['chunk_type']
            )
            
            search_result = SearchResult(
                chunk=chunk,
                score=results['distances'][0][i]
            )
            search_results.append(search_result)
        
        return search_results
    
    def clear(self):
        """Clear all data from the vector store"""
        self.client.delete_collection("code_chunks")
        self.collection = self.client.get_or_create_collection(
            name="code_chunks",
            metadata={"description": "Code chunks with embeddings"}
        )