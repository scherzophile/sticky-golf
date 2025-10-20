import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 6969

clients = []
players_state = {}
ready_states = {}
hole_complete_states = {}
game_started = False
current_level = 0
game_lock = threading.RLock()


def broadcast(message, sender=None):
    for c, _ in clients[:]:
        if c != sender:
            try:
                c.sendall((message + "\n").encode())
            except:
                pass


def reset_game():
    global game_started, ready_states, hole_complete_states, current_level
    with game_lock:
        game_started = False
        current_level = 0
        hole_complete_states.clear()
    broadcast(json.dumps({"type": "game_reset"}))


def checkallfinishhole():
    with game_lock:
        if not game_started or len(clients) == 0:
            return False

        for conn, addr in clients:
            addr_str = str(addr)
            player_finished = False
            for pid, is_complete in hole_complete_states.items():
                player_data = players_state.get(pid)
                if player_data and player_data.get("addr") == addr_str and is_complete:
                    player_finished = True
                    break

            if not player_finished:
                return False

        return True


def gonexthole():
    global current_level, hole_complete_states
    with game_lock:
        current_level += 1

        MAX_HOLES = 2

        if current_level >= MAX_HOLES:
            reset_game()
        else:
            hole_complete_states.clear()
            next_hole_msg = json.dumps({
                "type": "next_hole",
                "level": current_level
            })
            broadcast(next_hole_msg)


def handle_client(conn, addr):
    global game_started
    print(f"[NEW CONNECTION] {addr}")
    conn.settimeout(0.1)

    with game_lock:
        clients.append((conn, addr))
        current_players = list(players_state.values())

    print(players_state)
    for player_data in players_state.values():
        try:
            conn.sendall((json.dumps(player_data) + "\n").encode())
        except:
            pass

    print(f"Just some data: Client size is {len(clients)}, game started is {game_started}")

    try:
        buffer = ""
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break

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

                                if not game_started and len(ready_states) == len(clients):
                                    game_started = True
                                    current_level = 0
                                    hole_complete_states.clear()
                                    print("[AUTO START] Minimum players ready, starting game!")
                                    broadcast(json.dumps({"type": "start_game"}))
                                    ready_states.clear()

                        elif msg_type == "hole_complete":
                            pid = info["id"]
                            with game_lock:
                                hole_complete_states[pid] = True
                                print(f"{pid} finished the hole ({len(hole_complete_states)}/{len(clients)} players)")

                                broadcast(json.dumps({
                                    "type": "hole_complete",
                                    "id": pid
                                }), sender=conn)

                                if checkallfinishhole():
                                    gonexthole()

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
                        print("Somehow socket timeout")
                        continue
                    except json.JSONDecodeError:
                        print("Somehow json decode error")
                        continue
                    except Exception as e:
                        print(f"Unhandled exception 2: {e}")
            except socket.timeout:
                pass
            except Exception as e:
                print(f"unhandled exception: {e}")
                break
    except ConnectionResetError:
        print("Error settings")
    except Exception as e:
        print(f"Outer exception: {e}")
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
                hole_complete_states.pop(pid, None)
                print(f"Removed player {pid} from state")

            for c in clients:
                if c[0] == conn:
                    print(f"We removed something from the client: {c}")
                    clients.remove(c)
                    break

            if len(clients) == 0:
                print("[NO PLAYERS] Resetting game state")
                reset_game()

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