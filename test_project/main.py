
def main():
    """Main entry point"""
    auth = Authentication()
    if auth.login("user", "pass"):
        print("Login successful")
    else:
        print("Login failed")

if __name__ == "__main__":
    main()
