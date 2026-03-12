import socket
import threading
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# --- 1. Security Setup (Key Derivation) ---
def derive_key(password: str):
    # We use a static salt for this project so users with the same password get the same key
    salt = b'secure_static_salt' 
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    # Turn the password into a URL-safe base64 key for Fernet
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# --- 2. Identity & Authentication ---
username = input("Enter your username: ")
room_password = input("Enter the secret Room Password: ")

key = derive_key(room_password)
cipher = Fernet(key)

# --- 3. Connection Setup ---
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect(('127.0.0.1', 5555))
except ConnectionRefusedError:
    print("Error: Could not connect to server. Is server.py running?")
    exit()

def receive():
    while True:
        try:
            encrypted_message = client.recv(1024)
            if not encrypted_message:
                break
            
            # Attempt to decrypt
            decrypted_message = cipher.decrypt(encrypted_message).decode('utf-8')
            print(f"\n{decrypted_message}")
        except Exception:
            # This triggers if the Third Person has the wrong Room Password
            print("\n[!] Received an encrypted message, but your Room Password is incorrect. Decryption failed.")
            # We don't break here so the user can try to stay in the session
            pass

def send():
    while True:
        try:
            message = input(f"{username} > ")
            if message.lower() == 'quit':
                client.close()
                break
            
            full_message = f"{username}: {message}"
            # Encrypt the username + message together
            encrypted_msg = cipher.encrypt(full_message.encode('utf-8'))
            client.send(encrypted_msg)
        except Exception as e:
            print(f"Error sending message: {e}")
            break

# --- 4. Start Threads ---
receive_thread = threading.Thread(target=receive, daemon=True)
receive_thread.start()

# The main thread will handle the sending
send()