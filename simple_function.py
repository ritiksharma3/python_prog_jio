def greet_user(name: str):
    print(f"Hello, {name}! Have a great day!")

if __name__ == "__main__":
    username = input("Please enter your name: ")
    greet_user(username)