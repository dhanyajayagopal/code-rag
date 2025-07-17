from pathlib import Path
from typing import List, Iterator
import fnmatch
from .config import CodeRAGConfig

class FileScanner:
    def __init__(self, config: CodeRAGConfig):
        self.config = config
    
    def scan_directory(self, directory: Path) -> List[Path]:
        files = []
        
        for pattern in self.config.get("file_patterns", ["*.py"]):
            files.extend(directory.rglob(pattern))
        
        filtered_files = []
        for file_path in files:
            if self.should_include_file(file_path):
                filtered_files.append(file_path)
        
        return filtered_files
    
    def should_include_file(self, file_path: Path) -> bool:
        file_str = str(file_path)
        
        for pattern in self.config.get("ignore_patterns", []):
            if fnmatch.fnmatch(file_str, pattern):
                return False
        
        try:
            if file_path.stat().st_size > self.config.get("max_file_size", 1048576):
                return False
        except OSError:
            return False
        
        return True
    
    def get_file_stats(self, files: List[Path]) -> dict:
        stats = {
            "total_files": len(files),
            "by_extension": {},
            "total_size": 0
        }
        
        for file_path in files:
            ext = file_path.suffix.lower()
            stats["by_extension"][ext] = stats["by_extension"].get(ext, 0) + 1
            
            try:
                stats["total_size"] += file_path.stat().st_size
            except OSError:
                pass
        
        return stats