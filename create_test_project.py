from pathlib import Path

def create_test_project():
    """Create a small test project with multiple files"""
    
    project_dir = Path("./test_project")
    project_dir.mkdir(exist_ok=True)
    
    (project_dir / "main.py").write_text('''
def main():
    """Main entry point"""
    auth = Authentication()
    if auth.login("user", "pass"):
        print("Login successful")
    else:
        print("Login failed")

if __name__ == "__main__":
    main()
''')
    
    (project_dir / "auth.py").write_text('''
class Authentication:
    def __init__(self):
        self.users = {"user": "pass", "admin": "secret"}
    
    def login(self, username, password):
        """Authenticate a user"""
        return self.users.get(username) == password
    
    def logout(self):
        """Log out the current user"""
        print("User logged out")

def hash_password(password):
    """Hash a password for storage"""
    return f"hashed_{password}"
''')
    
    utils_dir = project_dir / "utils"
    utils_dir.mkdir(exist_ok=True)
    
    (utils_dir / "__init__.py").write_text("")
    (utils_dir / "helpers.py").write_text('''
def format_username(username):
    """Format username for display"""
    return username.title()

class Logger:
    def log(self, message):
        """Log a message"""
        print(f"LOG: {message}")
''')
    
    print(f"Created test project in {project_dir}")
    print("Files created:")
    for file in project_dir.rglob("*.py"):
        print(f"  {file}")

if __name__ == "__main__":
    create_test_project()