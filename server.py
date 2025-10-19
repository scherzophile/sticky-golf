import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 6969

clients = []
players_state = {}
ready_states = {}
game_started = False
game_lock = threading.Lock()


def broadcast(message, sender=None):
    for c, _ in clients[:]:
        if c != sender:
            try:
                c.sendall((message + "\n").encode())
            except:
                pass


def reset_game():
    global game_started, ready_states
    with game_lock:
        game_started = False
    broadcast(json.dumps({"type": "game_reset"}))

def handle_client(conn, addr):
    global game_started
    print(f"[NEW CONNECTION] {addr}")
    conn.settimeout(1)

    with game_lock:
        clients.append((conn, addr))

    for player_data in players_state.values():
        try:
            conn.sendall((json.dumps(player_data) + "\n").encode())
        except:
            pass

    try:
        buffer = ""
        while True:
            try:
                data = conn.recv(1024).decode()

                buffer += data
                while "\n" in buffer:
                    idx = buffer.index("\n")
                    message = buffer[:idx]
                    buffer = buffer[idx + 1:]
                    if not message.strip():
                        continue

                    try:
                        info = json.loads(message)
                        info["addr"] = str(addr)
                        msg_type = info.get("type")

                        if msg_type == "ready":
                            pid = info["id"]
                            with game_lock:
                                ready_states[pid] = True
                                print(f"{pid} is ready ({len(ready_states)}/{len(clients)} players)")
                                print(game_started)

                                if not game_started and len(ready_states) == len(clients):
                                    game_started = True
                                    print("[AUTO START] Minimum players ready, starting game!")
                                    broadcast(json.dumps({"type": "start_game"}))
                                    ready_states.clear()

                        elif msg_type == "game_finished":
                            pid = info["id"]
                            print(f"{pid} finished their game")
                            reset_game()
                            game_started = False

                        elif msg_type == "reset":
                            reset_game()
                            broadcast(json.dumps({"type": "game_reset"}))

                        else:
                            players_state[info["id"]] = info
                            broadcast(json.dumps(info), sender=conn)
                    except socket.timeout:
                        continue
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print("Unhandled exception 2")
            except socket.timeout:
                pass
            except Exception as e:
                print("unhandled exception")
                break
    except ConnectionResetError:
        print("Error settings")
    except Exception as e:
        print("OUter exception")
    finally:
        print(f"[DISCONNECTED] {addr}")

        disconnected_ids = [
            pid for pid, pdata in players_state.items()
            if pdata.get("addr") == str(addr)
        ]

        with game_lock:
            for pid in disconnected_ids:
                players_state.pop(pid, None)
                ready_states.pop(pid, None)
                print(f"Removed player {pid} from state")

            for c in clients[:]:
                if c[0] == conn:
                    print(f"We removed something from the client: {c}")
                    clients.remove(c)
                    break

            if len(clients) == 0:
                print("[NO PLAYERS] Resetting game state")
                reset_game()
            # elif game_started and len(ready_states) < 3:
            #     print("[NOT ENOUGH PLAYERS] Resetting game state")
            #     reset_game()

        conn.close()

        print(f"Clients size is now {len(clients)}")

        disconnect_msg = json.dumps({"type": "disconnect", "addr": str(addr)})
        broadcast(disconnect_msg)


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"[LISTENING] Server running on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()