# HELLO TEST
# HELLO STICKY RICKY BACK
import pygame
import sys
import socket
import threading
import json
import random

pygame.init()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# SERVER STUFF

def receive_data():
    global other_players
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
                pid = info["id"]

                if pid == player_id:
                    continue

                if pid not in other_players:
                    other_players[pid] = {
                        "x": info["x"],
                        "y": info["y"],
                        "tx": info["x"],
                        "ty": info["y"],
                        "firing": info.get("firing", False),
                        "inair": info.get("inair", False)
                    }
                else:
                    other_players[pid]["tx"] = info["x"]
                    other_players[pid]["ty"] = info["y"]
                    other_players[pid]["firing"] = info.get("firing", False)
                    other_players[pid]["inair"] = info.get("inair", False)

        except json.JSONDecodeError:
            continue
        except Exception as e:
            print(f"[ERROR receiving data] {e}")
            break


def send_player_data():
    try:
        packet = json.dumps({
            "id": player_id,
            "x": x,
            "y": y,
            "firing": firing,
            "inair": inair
        }) + "\n"
        client.sendall(packet.encode())
    except:
        pass
HOST = "142.112.166.131"
PORT = 6767  # hehehehaw
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(5)

try:
    client.connect((HOST, PORT))
    print("Connected to RICKY server")
    threading.Thread(target=receive_data, daemon=True).start()
except (ConnectionRefusedError, socket.timeout, OSError) as e:
    print("Ricky server not running")
    pygame.quit()
    sys.exit()

player_id = str(random.randint(1000, 9999))
other_players = {}

# IMAGES HERE
bgimg = pygame.image.load("img/pixelsky.jpg").convert()
bgimg = pygame.transform.scale(bgimg, (1200, 800))

logo = pygame.image.load("img/logo.png").convert_alpha()
logo = pygame.transform.scale(logo, (400, 400))

forest = pygame.image.load("img/forest.jpg").convert()
forest = pygame.transform.scale(forest, (1200, 800))

play = pygame.image.load("img/play.png").convert_alpha()
play = pygame.transform.scale(play, (100, 100))

# MUSIC HERE
pygame.mixer.init()
pygame.mixer.music.load("audio/music.mp3")
pygame.mixer.music.play(loops=-1)

running = True
firing = False
inair = False
onground = False
offset_x = 0
offset_y = 0
canfire = False

state = "title"

x = 300
y = 400
a = 0
viy = 0
vy = 0
vx = 0
t = 0
theta = 0
new_dx = 0
new_dy = 0
platforms = [
    pygame.Rect(300, 400, 500, 50),
    pygame.Rect(0, 510, 1200, 90),
    pygame.Rect(50, 200, 300, 50),
    pygame.Rect(0, 0, 50, 530),
    pygame.Rect(500, 200, 100, 50)
]





def checkcanfire():
    global my, offset_y, canfire
    ball_circle = pygame.Rect(x - 13, y - 13, 26, 26)
    if my + offset_y > ball_circle.y + 7.5:
        canfire = True
    else:
        canfire = False
    print(canfire)


def checkplatform():
    global vy, inair, y, onground, vx, x, offset_x, new_dx, new_dy, platforms, offset_y

    ball_circle = pygame.Rect(x - 13, y - 13, 26, 26)

    for platform in platforms:
        if ball_circle.colliderect(platform) and vy <= 0 and abs(y - (platform.y + platform.height)) <= 15:
            print("collide")
            y = platform.y + platform.height + 13
            vy *= -0.5
        elif x < platform.left and ball_circle.colliderect(platform) and vx > 0:
            x = platform.left - 13
            vx = -vx * 0.5
        elif x > platform.right and vx < 0 and ball_circle.colliderect(platform):
            x = platform.right + 13
            vx = -vx * 0.5
        elif ball_circle.colliderect(platform) and vy >= 0:
            onground = True
            y = platform.y - 10
            vy *= -0.75
            vx *= 0.6
            print(vx, vy)
            if abs(vy) <= abs(a):
                print("in air is now false")
                inair = False
                onground = True
                vy = 0
                vx = 0
                break
            else:
                onground = False

    if not onground:
        inair = True


while running:
    screen.fill((93, 226, 231))
    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == "game" and event.button == 1 and inair == False and canfire == True:
                firing = True
                onground = True
                inair = False

        if event.type == pygame.MOUSEBUTTONUP:
            if state == "game" and event.button == 1 and canfire == True:
                firing = False
                inair = True
                onground = False
            # Play button
            if state == "title" and event.button == 1:
                if 350 <= mx and mx <= 450 and 400 <= my and my <= 500:
                    state = "game"
                    firing = False
                    inair = True
                    a = -2

    if state == "title":
        screen.blit(forest, (0, 0))
        screen.blit(logo, (200, 50))
        screen.blit(play, (350, 400))
    if state == "game":
        if inair:
            vy -= a
            x += vx
            y += vy
            onground = False
            firing = False
            checkplatform()
        offset_x = x - WIDTH // 2
        offset_y = y - HEIGHT // 2

        checkcanfire()

        send_player_data()

        # Background image yay
        # screen.blit(bgimg, (0, 0))

        # Draw main platforms, DRAW OTHER PLATFORMS HERE LATER
        pygame.draw.rect(screen, (0, 255, 0), (0, 510, 1200, 90))

        for platform in platforms:
            pygame.draw.rect(screen, (67, 33, 9),
                             (platform.x - offset_x, platform.y - offset_y, platform.width, platform.height),
                             border_radius=5)
            pygame.draw.rect(screen, (0, 150, 0),
                             (platform.x - 2 - offset_x, platform.y - offset_y, platform.width + 4, 10),
                             border_radius=10)

        # Local player
        pygame.draw.circle(screen, (100, 100, 100), (x - offset_x, y - offset_y), 13)
        pygame.draw.circle(screen, (255, 255, 255), (x - offset_x, y - offset_y), 10)

        # Other players
        for pid, pdata in other_players.items():
            smoothing = 0.2
            pdata["x"] += (pdata["tx"] - pdata["x"]) * smoothing
            pdata["y"] += (pdata["ty"] - pdata["y"]) * smoothing

            other_x = pdata["x"] - offset_x
            other_y = pdata["y"] - offset_y

            pygame.draw.circle(screen, (200, 100, 100), (int(other_x), int(other_y)), 13)
            pygame.draw.circle(screen, (255, 100, 100), (int(other_x), int(other_y)), 10)

        if firing:
            viy = -15
            vy = viy

            actual_mx = mx + offset_x
            actual_my = my + offset_y

            dx = actual_mx - x
            dy = actual_my - y

            if dy == 0:
                a = 0
            else:
                a = -(vy ** 2) / (2 * dy)

            t = 2 * dy / vy if vy != 0 else 0
            if t != 0:
                vx = dx / t

            # trajectory stuff
            t_temp = 0
            new_dx = x
            new_dy = y
            while abs(new_dx - x) < 800 and abs(new_dy - y) < 800 and a != 0 and dx != 0 and t != 0 and canfire == True:
                new_dx = x + vx * t_temp
                new_dy = y + viy * t_temp - 0.5 * a * (t_temp ** 2)
                pygame.draw.circle(screen, (255, 0, 0), (new_dx - offset_x, new_dy - offset_y), 5)
                t_temp += 2

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

"""

TO DO LIST:
- bouncing in intro
- changing backgrounds
- max power limit (so then user can just max send it)
"""
