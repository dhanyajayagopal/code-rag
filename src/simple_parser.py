import re
from typing import List
from pathlib import Path
from .models import CodeChunk

class SimpleCodeParser:
    def parse_file(self, file_path: Path) -> List[CodeChunk]:
        """Parse a Python file into code chunks"""
        content = file_path.read_text()
        lines = content.split('\n')
        chunks = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line or line.startswith('#'):
                i += 1
                continue
            
            func_match = re.match(r'def\s+(\w+)\s*\(', lines[i])
            if func_match:
                func_name = func_match.group(1)
                start_line = i + 1
                end_line = self._find_block_end(lines, i)
                
                func_content = '\n'.join(lines[i:end_line])
                
                chunks.append(CodeChunk(
                    file_path=str(file_path),
                    content=func_content,
                    start_line=start_line,
                    end_line=end_line,
                    chunk_type=f'function:{func_name}'
                ))
                i = end_line
                continue
            
            class_match = re.match(r'class\s+(\w+)', lines[i])
            if class_match:
                class_name = class_match.group(1)
                start_line = i + 1
                end_line = self._find_block_end(lines, i)
                
                class_content = '\n'.join(lines[i:end_line])
                
                chunks.append(CodeChunk(
                    file_path=str(file_path),
                    content=class_content,
                    start_line=start_line,
                    end_line=end_line,
                    chunk_type=f'class:{class_name}'
                ))
                i = end_line
                continue
            
            i += 1
        
        return chunks
    
    def _find_block_end(self, lines: List[str], start_idx: int) -> int:
        """Find where a code block ends based on indentation"""
        if start_idx >= len(lines):
            return len(lines)
        
        def_line = lines[start_idx]
        base_indent = len(def_line) - len(def_line.lstrip())
        
        i = start_idx + 1
        while i < len(lines):
            line = lines[i]
            
            if line.strip() == '':
                i += 1
                continue
            
            current_indent = len(line) - len(line.lstrip())
            
            if current_indent <= base_indent:
                return i
            
            i += 1
        
        return len(lines)