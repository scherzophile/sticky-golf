import pygame
import socket
import threading
import json
import random


pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

HOST = "142.112.166.131"   # aw man pls dont hack me
PORT = 6767

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

player_id = str(random.randint(1000, 9999))
positions = {}

def receive_data():
    global positions
    buffer = ""
    while True:
        try:
            data = client.recv(1024).decode()
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                info = json.loads(message)
                positions[info["id"]] = (info["x"], info["y"], info["color"])
        except json.JSONDecodeError:
            continue
        except Exception as e:
            break

threading.Thread(target=receive_data, daemon=True).start()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mx, my = pygame.mouse.get_pos()

    packet = json.dumps({"id": player_id, "x": mx, "y": my, "color": (123, 123, 123)}) + "\n"
    client.sendall(packet.encode())
    try:
        client.sendall(packet.encode())
    except:
        pass
    screen.fill((0,0,0))
    pygame.draw.circle(screen, (123,123,123), (mx, my), 10)

    for others, (x, y, color) in positions.items():
        if others != player_id:
            pygame.draw.circle(screen, color, (int(x), int(y)), 10)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()