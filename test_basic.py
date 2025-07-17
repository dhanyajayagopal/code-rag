import os
from pathlib import Path

def test_basic_setup():
    """Test that we can find Python files in a directory"""
    
    test_dir = Path("./test_code")
    test_dir.mkdir(exist_ok=True)
    
    (test_dir / "example.py").write_text("""
def hello_world():
    '''Says hello to the world'''
    return "Hello, World!"

class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
""")
    
    python_files = list(test_dir.glob("*.py"))
    print(f"Found Python files: {python_files}")
    
    for file in python_files:
        content = file.read_text()
        print(f"\nContent of {file}:")
        print(content)

if __name__ == "__main__":
    test_basic_setup()