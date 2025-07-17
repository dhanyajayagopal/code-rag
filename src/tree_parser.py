from pathlib import Path
from typing import List, Optional
import re
from .models import CodeChunk

class AdvancedCodeParser:
   def __init__(self):
       self.file_extensions = {
           '.py': 'python',
           '.js': 'javascript',
           '.jsx': 'javascript',
           '.ts': 'typescript',
           '.tsx': 'typescript',
       }
   
   def get_language_from_file(self, file_path: Path) -> Optional[str]:
       return self.file_extensions.get(file_path.suffix.lower())
   
   def parse_file(self, file_path: Path) -> List[CodeChunk]:
       language = self.get_language_from_file(file_path)
       if not language:
           return []
       
       try:
           content = file_path.read_text(encoding='utf-8')
           
           if language == 'python':
               return self._parse_python(file_path, content)
           elif language in ['javascript', 'typescript']:
               return self._parse_javascript(file_path, content)
           
       except Exception as e:
           print(f"Error parsing {file_path}: {e}")
           return []
       
       return []
   
   def _parse_python(self, file_path: Path, content: str) -> List[CodeChunk]:
       chunks = []
       lines = content.split('\n')
       
       i = 0
       while i < len(lines):
           line = lines[i].strip()
           
           if not line or line.startswith('#'):
               i += 1
               continue
           
           func_match = re.match(r'def\s+(\w+)\s*\((.*?)\)\s*:', lines[i])
           if func_match:
               func_name, params = func_match.groups()
               start_line = i + 1
               end_line = self._find_python_block_end(lines, i)
               
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
           
           class_match = re.match(r'class\s+(\w+)(?:\((.*?)\))?\s*:', lines[i])
           if class_match:
               class_name, superclasses = class_match.groups()
               start_line = i + 1
               end_line = self._find_python_block_end(lines, i)
               
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
           
           import_match = re.match(r'((?:from\s+\S+\s+)?import\s+.+)', lines[i])
           if import_match:
               import_content = import_match.group(1)
               chunks.append(CodeChunk(
                   file_path=str(file_path),
                   content=import_content,
                   start_line=i + 1,
                   end_line=i + 1,
                   chunk_type='import'
               ))
           
           i += 1
       
       return chunks
   
   def _parse_javascript(self, file_path: Path, content: str) -> List[CodeChunk]:
       chunks = []
       lines = content.split('\n')
       
       i = 0
       while i < len(lines):
           line = lines[i].strip()
           
           if not line or line.startswith('//'):
               i += 1
               continue
           
           func_match = re.match(r'function\s+(\w+)\s*\((.*?)\)\s*{', lines[i])
           if func_match:
               func_name, params = func_match.groups()
               start_line = i + 1
               end_line = self._find_js_block_end(lines, i)
               
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
           
           arrow_match = re.match(r'(?:const|let|var)\s+(\w+)\s*=\s*\((.*?)\)\s*=>\s*{', lines[i])
           if arrow_match:
               func_name, params = arrow_match.groups()
               start_line = i + 1
               end_line = self._find_js_block_end(lines, i)
               
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
           
           class_match = re.match(r'class\s+(\w+)(?:\s+extends\s+\w+)?\s*{', lines[i])
           if class_match:
               class_name = class_match.group(1)
               start_line = i + 1
               end_line = self._find_js_block_end(lines, i)
               
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
   
   def _find_python_block_end(self, lines: List[str], start_idx: int) -> int:
       if start_idx >= len(lines):
           return len(lines)
       
       def_line = lines[start_idx]
       base_indent = len(def_line) - len(def_line.lstrip())
       
       for i in range(start_idx + 1, len(lines)):
           line = lines[i]
           
           if line.strip() == '' or line.strip().startswith('#'):
               continue
           
           current_indent = len(line) - len(line.lstrip())
           
           if current_indent <= base_indent:
               return i
       
       return len(lines)
   
   def _find_js_block_end(self, lines: List[str], start_idx: int) -> int:
       if start_idx >= len(lines):
           return len(lines)
       
       brace_count = 0
       found_opening = False
       
       for i in range(start_idx, len(lines)):
           line = lines[i]
           for char in line:
               if char == '{':
                   brace_count += 1
                   found_opening = True
               elif char == '}':
                   brace_count -= 1
                   if found_opening and brace_count == 0:
                       return i + 1
       
       return len(lines)
   
   def _extract_python_docstring_from_lines(self, lines: List[str], start_idx: int) -> Optional[str]:
       for i in range(start_idx + 1, min(start_idx + 5, len(lines))):
           line = lines[i].strip()
           if line.startswith('"""') or line.startswith("'''"):
               quote_type = '"""' if line.startswith('"""') else "'''"
               if line.endswith(quote_type) and len(line) > 6:
                   return line[3:-3].strip()
               else:
                   docstring_lines = [line[3:]]
                   for j in range(i + 1, len(lines)):
                       if quote_type in lines[j]:
                           docstring_lines.append(lines[j][:lines[j].index(quote_type)])
                           return '\n'.join(docstring_lines).strip()
                       docstring_lines.append(lines[j])
       return None
   
   def _extract_class_methods(self, lines: List[str], start_idx: int, end_idx: int) -> List[str]:
       methods = []
       for i in range(start_idx + 1, end_idx):
           line = lines[i].strip()
           if line.startswith('def '):
               match = re.match(r'def\s+(\w+)', line)
               if match:
                   methods.append(match.group(1))
       return methods