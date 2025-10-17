import socket
import threading

HOST = "0.0.0.0"
PORT = 6767

clients = []
lock = threading.Lock()

def broadcast(data, sender=None):
    with lock:
        for c in clients:
            if c != sender:
                try:
                    c.sendall(data.encode())
                except:
                    pass

def handle_client(conn, addr):
    with lock:
        clients.append(conn)

    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            broadcast(data, sender=conn)
    except:
        pass
    with lock:
        clients.remove(conn)
    conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
