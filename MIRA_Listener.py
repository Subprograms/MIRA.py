import socket
import os

HOST = "127.0.0.1"
PORT = 4444
BASE_DIR = r"C:\Users\<User>\Downloads"

def start_listener():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(5)
        while True:
            client, addr = server.accept()
            handle_client(client)

def handle_client(client):
    data = b""
    while True:
        chunk = client.recv(4096)
        if not chunk:
            break
        data += chunk
    process_data(data)
    client.close()

def process_data(data):
    lines = data.split(b"\n", 1)
    if len(lines) < 2:
        return
    header = lines[0].strip()
    payload = lines[1]
    if header.startswith(b"[filename]"):
        fname = header.split(b"]")[1].strip().decode()
        store_file(fname, payload)

def store_file(fname, payload):
    os.makedirs(BASE_DIR, exist_ok=True)
    path = os.path.join(BASE_DIR, fname)
    with open(path, "wb") as f:
        f.write(payload)

if __name__ == "__main__":
    start_listener()
