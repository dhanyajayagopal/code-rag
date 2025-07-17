
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
