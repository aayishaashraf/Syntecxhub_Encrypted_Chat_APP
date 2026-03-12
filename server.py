import socket
import threading
from datetime import datetime

# Server Config
HOST = '127.0.0.1'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []

def log_to_file(data, address):
    """Logs the raw encrypted data to a text file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] From {address}: {data.hex()}\n"
    
    with open("server_chat_log.txt", "a") as f:
        f.write(log_entry)
    print(f"Logged encrypted packet from {address}")

def broadcast(message, _client):
    for client in clients:
        if client != _client:
            client.send(message)

def handle_client(client, address):
    while True:
        try:
            # Receive the encrypted blob
            message = client.recv(1024)
            if not message:
                break
                
            # LOG the encrypted data (Hex format for readability)
            log_to_file(message, address)
            
            # Pass the encrypted data to others
            broadcast(message, client)
        except:
            if client in clients:
                clients.remove(client)
            client.close()
            break

print(f"Server is listening on {HOST}:{PORT}...")

while True:
    client, address = server.accept()
    print(f"New connection: {str(address)}")
    clients.append(client)
    
    # Pass both client and address to the handler for logging
    thread = threading.Thread(target=handle_client, args=(client, address))
    thread.start()