from pathlib import Path
from typing import List, Dict, Any
import json

class CodeRAGConfig:
    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path(".coderag.json")
        self.default_config = {
            "index_directory": "./chroma_db",
            "file_patterns": ["*.py", "*.js", "*.jsx", "*.ts", "*.tsx"],
            "ignore_patterns": [
                "node_modules/**",
                ".git/**", 
                "__pycache__/**",
                "*.pyc",
                ".venv/**",
                "venv/**",
                "build/**",
                "dist/**"
            ],
            "max_file_size": 1048576,
            "embedding_model": "all-MiniLM-L6-v2"
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                config = self.default_config.copy()
                config.update(user_config)
                return config
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.default_config
        return self.default_config
    
    def save_config(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default=None):
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        self.config[key] = value