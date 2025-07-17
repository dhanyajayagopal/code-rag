from pathlib import Path
from src.simple_parser import SimpleCodeParser

def test_parsing():
    """Test parsing the example Python file"""
    
    parser = SimpleCodeParser()
    test_file = Path("test_code/example.py")
    
    chunks = parser.parse_file(test_file)
    
    print(f"Found {len(chunks)} code chunks:")
    print()
    
    for chunk in chunks:
        print(f"Type: {chunk.chunk_type}")
        print(f"Lines: {chunk.start_line}-{chunk.end_line}")
        print(f"ID: {chunk.id}")
        print("Content:")
        print(chunk.content)
        print("-" * 50)

if __name__ == "__main__":
    test_parsing()