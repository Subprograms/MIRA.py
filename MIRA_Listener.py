import socket
import os

HOST = "127.0.0.1"
PORT = 4444
BASE_DIR = r"C:\Users\<User>\Desktop"

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
    process_data(data, client)
    client.close()

def process_data(data, client):
    lines = data.split(b"\n", 1)
    if len(lines) < 2:
        handle_requests(data, client)
        return
    header = lines[0].strip()
    payload = lines[1]
    if header.startswith(b"[upload]"):
        filename = header.split(b"]")[1].strip().decode()
        path = os.path.join(BASE_DIR, filename)
        if b".txt" in header or b".png" in header:
            store_file(path, payload)
    else:
        handle_requests(data, client)

def handle_requests(data, client):
    if data.startswith(b"[request]"):
        filename = data.split(b"]")[1].strip().decode()
        path = os.path.join(BASE_DIR, filename)
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    file_data = f.read()
                client.sendall(file_data)
            except:
                client.sendall(b"[nofile]")
        else:
            client.sendall(b"[nofile]")
    else:
        pass

def store_file(path, payload):
    folder = os.path.dirname(path)
    os.makedirs(folder, exist_ok=True)
    mode = "ab" if os.path.exists(path) else "wb"
    with open(path, mode) as f:
        f.write(payload)

if __name__ == "__main__":
    start_listener()
