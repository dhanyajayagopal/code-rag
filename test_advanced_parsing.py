from src.tree_parser import AdvancedCodeParser
from pathlib import Path

def test_advanced_parsing():
    parser = AdvancedCodeParser()
    
    test_files = [
        Path("test_project/auth.py"),
        Path("test_project/main.py"),
        Path("test_project/utils/helpers.py")
    ]
    
    for file_path in test_files:
        if file_path.exists():
            print(f"\n=== Parsing {file_path} ===")
            chunks = parser.parse_file(file_path)
            
            for chunk in chunks:
                print(f"\nType: {chunk.chunk_type}")
                print(f"Lines: {chunk.start_line}-{chunk.end_line}")
                print("Content preview:")
                print(chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content)
                print("-" * 40)

if __name__ == "__main__":
    test_advanced_parsing()