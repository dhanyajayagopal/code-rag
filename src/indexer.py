import hashlib
import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from .models import CodeChunk
from .tree_parser import AdvancedCodeParser
from .embedder import CodeEmbedder
from .vector_store import VectorStore

class IncrementalIndexer:
    def __init__(self, config, console=None):
        self.config = config
        self.console = console
        self.parser = AdvancedCodeParser()
        self.embedder = CodeEmbedder()
        self.vector_store = VectorStore(config.get("index_directory"))
        self.metadata_file = Path(config.get("index_directory")) / "metadata.json"
        self.file_hashes = self.load_metadata()
    
    def load_metadata(self) -> Dict[str, str]:
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_metadata(self):
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.metadata_file, 'w') as f:
            json.dump(self.file_hashes, f, indent=2)
    
    def get_file_hash(self, file_path: Path) -> str:
        try:
            content = file_path.read_bytes()
            return hashlib.md5(content).hexdigest()
        except:
            return ""
    
    def get_changed_files(self, files: List[Path]) -> Dict[str, List[Path]]:
        changed = []
        removed = []
        unchanged = []
        
        current_files = {str(f): f for f in files}
        
        for file_str, file_path in current_files.items():
            current_hash = self.get_file_hash(file_path)
            if file_str not in self.file_hashes or self.file_hashes[file_str] != current_hash:
                changed.append(file_path)
                self.file_hashes[file_str] = current_hash
            else:
                unchanged.append(file_path)
        
        for file_str in list(self.file_hashes.keys()):
            if file_str not in current_files:
                removed.append(file_str)
                del self.file_hashes[file_str]
        
        return {
            'changed': changed,
            'removed': removed,
            'unchanged': unchanged
        }
    
    def remove_chunks_for_files(self, file_paths: List[str]):
        try:
            existing_data = self.vector_store.collection.get()
            ids_to_remove = []
            
            for i, metadata in enumerate(existing_data['metadatas']):
                if metadata.get('file_path') in file_paths:
                    ids_to_remove.append(existing_data['ids'][i])
            
            if ids_to_remove:
                self.vector_store.collection.delete(ids=ids_to_remove)
                if self.console:
                    self.console.print(f"Removed {len(ids_to_remove)} chunks from deleted files")
        except Exception as e:
            if self.console:
                self.console.print(f"Error removing chunks: {e}")
    
    def index_files(self, files: List[Path], force_reindex: bool = False) -> Dict[str, int]:
        if force_reindex:
            changes = {'changed': files, 'removed': [], 'unchanged': []}
            self.vector_store.clear()
        else:
            changes = self.get_changed_files(files)
        
        if self.console:
            self.console.print(f"Files - Changed: {len(changes['changed'])}, "
                             f"Removed: {len(changes['removed'])}, "
                             f"Unchanged: {len(changes['unchanged'])}")
        
        if changes['removed']:
            self.remove_chunks_for_files(changes['removed'])
        
        if not changes['changed']:
            if self.console:
                self.console.print("No files to reindex")
            return {'chunks_added': 0, 'files_processed': 0}
        
        all_chunks = []
        processed_files = 0
        
        for file_path in changes['changed']:
            try:
                chunks = self.parser.parse_file(file_path)
                all_chunks.extend(chunks)
                processed_files += 1
                
                if self.console:
                    self.console.print(f"Parsed {file_path}: {len(chunks)} chunks")
                    
            except Exception as e:
                if self.console:
                    self.console.print(f"Error parsing {file_path}: {e}")
        
        if all_chunks:
            if self.console:
                self.console.print(f"Generating embeddings for {len(all_chunks)} chunks...")
            
            embeddings = self.embedder.embed_chunks(all_chunks)
            self.vector_store.add_chunks(all_chunks, embeddings)
        
        self.save_metadata()
        
        return {
            'chunks_added': len(all_chunks),
            'files_processed': processed_files
        }