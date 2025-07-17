from dataclasses import dataclass
from typing import List, Optional

@dataclass
class CodeChunk:
    """A piece of code with metadata"""
    file_path: str
    content: str
    start_line: int
    end_line: int
    chunk_type: str
    
    @property
    def id(self) -> str:
        """Unique ID for this chunk"""
        return f"{self.file_path}:{self.start_line}-{self.end_line}"

@dataclass
class SearchResult:
    """Result from vector search"""
    chunk: CodeChunk
    score: float
    context: Optional[str] = None