# HELLO TEST
# HELLO STICKY RICKY BACK
import pygame
import sys
import socket
import threading
import json
import random
import time

pygame.init()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
# Fonts
font = pygame.font.Font(None, 48)
font2 = pygame.font.Font(None, 36)


# ===== SERVER STUFF
def receive_data():
    global other_players, state, all_ready
    buffer = ""
    try:
        while True:
            try:
                data = client.recv(1024).decode()
                if not data:
                    break
                buffer += data
                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)
                    info = json.loads(message)

                    # Late join
                    if info.get("type") == "reject":
                        print(info.get("reason"))
                        pygame.quit()
                        sys.exit()

                    # Game start
                    if info.get("type") == "start_game":
                        print("Game started!")
                        state = "game"
                        all_ready = True
                        continue

                    # Handle player ready status
                    if info.get("type") == "player_ready":
                        ready_pid = info.get("id")
                        if ready_pid in other_players:
                            other_players[ready_pid]["ready"] = True
                        continue

                    if info.get("type") == "hole_complete":
                        complete_pid = info.get("id")
                        if complete_pid in other_players:
                            other_players[complete_pid]["hole_complete"] = True
                        elif complete_pid == player_id:
                            pass
                        continue

                    if info.get("type") == "next_hole":
                        print("Moving to next hole!")
                        level = info.get("level")
                        resetfornexthole()
                        continue
                    if info.get("type") == "game_reset":
                        resetgame()
                        continue

                    # Handle disconnect messages
                    if info.get("type") == "disconnect":
                        disconnect_addr = info.get("addr")
                        for pid in list(other_players.keys()):
                            if other_players[pid].get("addr") == disconnect_addr:
                                del other_players[pid]
                                print(f"Player {pid} disconnected")
                        continue

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
                            "inair": info.get("inair", False),
                            "name": info.get("name", "???"),
                            "addr": info.get("addr", ""),
                            "ready": False,
                            "hole_complete": False
                        }
                    else:
                        other_players[pid]["tx"] = info["x"]
                        other_players[pid]["ty"] = info["y"]
                        other_players[pid]["firing"] = info.get("firing", False)
                        other_players[pid]["inair"] = info.get("inair", False)
                        other_players[pid]["name"] = info.get("name", other_players[pid].get("name", "???"))
                        other_players[pid]["addr"] = info.get("addr", other_players[pid].get("addr", ""))

            except socket.timeout:
                continue
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"[ERROR receiving data] {e}")
    except Exception as e:
        print(f"OOPSIES exception in outer try statement {e} ")
    finally:
        try:
            client.close()
        except:
            pass
        pygame.quit()
        sys.exit()


def send_player_data():
    try:
        packet = json.dumps({
            "id": player_id,
            "x": x,
            "y": y,
            "firing": firing,
            "inair": inair,
            "name": name
        }) + "\n"
        client.sendall(packet.encode())
    except:
        pass

HOST = "142.112.166.131"
#HOST = "127.0.0.1"
PORT = 6969  # hehehehaw
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(1)
try:
    client.connect((HOST, PORT))
    print("Connected to RICKY server")
    threading.Thread(target=receive_data, daemon=True).start()
except (ConnectionRefusedError, socket.timeout, OSError) as e:
    print("Ricky server not running")
    pygame.quit()
    sys.exit()

# ==== GLOBAL VARIABLES
player_id = f"{random.randint(1000, 9999)}-{int(time.time() * 1000) % 100000}"
other_players = {}

title_slideshow = 0
title_slide = 0

running = True
firing = False
inair = False
onground = True
offset_x = 0
offset_y = 0
canfire = False
activateability = False
abilitytype = ""
wasinair = False
abilities = ["sticky", "homerun", "blackvision", "magnet", "swapball", "ghost", "rewind", "explosive", "dizzy", "invincible"]

spectating = False
hole_complete = False
spectate_x = 0;
spectate_y = 0;

state = "title"
ready = False
all_ready = False

# Themes:
"""
Grass, Fire, Ice, Space
"""
theme = "grass"

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
prevx = 0
prevy = 0

money = 0
strokes = 0
name = ""
level = 0

# IMAGES HERE
bgimg = pygame.image.load("img/pixelsky.jpg").convert()
bgimg = pygame.transform.scale(bgimg, (1200, 800))

logo = pygame.image.load("img/logo.png").convert_alpha()
logo = pygame.transform.scale(logo, (400, 400))

forest = pygame.image.load("img/forest.jpg").convert()
forest = pygame.transform.scale(forest, (1200, 800))

tundra = pygame.image.load("img/tundra.jpg").convert()
tundra = pygame.transform.scale(tundra, (1200, 800))

volcano = pygame.image.load("img/volcano.jpg").convert()
volcano = pygame.transform.scale(volcano, (1200, 800))

play = pygame.image.load("img/play.png").convert_alpha()
play = pygame.transform.scale(play, (100, 100))

# MUSIC HERE
pygame.mixer.init()
pygame.mixer.music.load("audio/music.mp3")
pygame.mixer.music.play(loops=-1)

platforms = [
    [
        pygame.Rect(300, 400, 500, 50),
        pygame.Rect(0, 510, 1000, 90),
        pygame.Rect(50, 200, 300, 50),
        pygame.Rect(0, 0, 50, 530),
        pygame.Rect(500, 200, 100, 50),

        # Make sure user can't cheat by going right
        pygame.Rect(1000, -500, 50, 1100),

        # We're going down down down
        pygame.Rect(-200, 0, 50, 800),
        pygame.Rect(-200, 800, 1500, 50)
    ], [
        # Middle block
        pygame.Rect(-100, 50, 200, 200),

        # Bottom left corner of center
        pygame.Rect(-500, 250, 200, 400),
        pygame.Rect(-300, 450, 200, 200),

        # Bottom right corner of center
        pygame.Rect(300, 250, 200, 400),
        pygame.Rect(100, 450, 200, 200),

        # Top right corner of center
        pygame.Rect(300, -350, 200, 400),
        pygame.Rect(100, -350, 200, 200),

        # Top left corner of center
        pygame.Rect(-500, -350, 200, 400),
        pygame.Rect(-300, -350, 200, 200),

        # Bottom platform to prevent user from falling
        pygame.Rect(-300, 850, 600, 200),

        # Top platform for symmetry
        pygame.Rect(-300, -750, 600, 200),

        # Now left and right side symmetry
        pygame.Rect(-1100, -350, 200, 1000),
        pygame.Rect(900, -350, 200, 1000),

        # Top-left corner blocks
        pygame.Rect(-900, -550, 200, 200),
        pygame.Rect(-700, -750, 200, 200),

        # Bottom left corner blocks
        pygame.Rect(-900, 850, 200, 200),
        pygame.Rect(-700, 1050, 200, 200),

        # Top-right corner blocks
        pygame.Rect(700, -550, 200, 200),
        pygame.Rect(500, -750, 200, 200),

        # Bottom right corner blocks
        pygame.Rect(700, 850, 200, 200),
        pygame.Rect(500, 1050, 200, 200),
    ]

]

coins = [
    [
        pygame.Rect(500, 140, 50, 50)
    ],
    [
        pygame.Rect(500, 140, 50, 50)
    ]
]

hole = [
    pygame.Rect(1000, 790, 50, 10),
    pygame.Rect(100, 100, 50, 10)
]

abilityrect = pygame.Rect(700,600,100,100)

def checkcanfire():
    global my, offset_y, canfire
    ball_circle = pygame.Rect(x - 13, y - 13, 26, 26)
    if my + offset_y > ball_circle.y + 7.5:
        canfire = True
    else:
        canfire = False


def respawn():
    global x, y, prevx, prevy, vx, vy, onground, inair
    if y + offset_y > 2000:
        vx = 0
        vy = 0
        onground = True
        inair = False
        x = prevx
        y = prevy

def resetfornexthole():
    global x,y,vx,vy,onground,offset_x, offset_y, prevx, prevy, spectating, hole_complete, inair, level
    level+=1
    x = 0
    y = 0
    vx = 0
    vy = 0
    inair = False
    onground = True
    offset_x = 0
    offset_y = 0
    prevx = 0
    prevy = 0
    spectating = False
    hole_complete = False

    for pid in other_players:
        other_players[pid]["hole_complete"] = False

def resetgame():
    global state, ready, all_ready, level, strokes, money, x, y, vx, vy, onground, inair, spectating, hole_complete
    level = 0
    state = "queue"
    ready = False
    all_ready = False
    strokes = 0
    money = 0
    x = 300
    y = 400
    vx = 0
    vy = 0
    inair = False
    onground = True
    spectating = False
    hole_complete = False

def checkplatform():
    global vy, inair, y, onground, vx, x, offset_x, new_dx, new_dy, platforms, offset_y, activateability, abilityrect, abilitytype, wasinair

    ball_circle = pygame.Rect(x - 13, y - 13, 26, 26)

    for platform in platforms[level]:
        if ball_circle.colliderect(platform) and vy <= 0 and abs(y - (platform.y + platform.height)) <= 15:
            y = platform.y + platform.height + 13
            vy *= -0.5
            if activateability and wasinair and abilitytype == "sticky":
                vy = 0
                vx = 0
                inair = False
                onground = True
                activateability = False
                print("This is true!")
                break
        elif x < platform.left and ball_circle.colliderect(platform) and vx > 0:
            x = platform.left - 13
            vx = -vx * 0.5
            if activateability and wasinair and abilitytype == "sticky":
                vy = 0
                vx = 0
                inair = False
                onground = True
                activateability = False
                print("This is true!")
                break
        elif x > platform.right and vx < 0 and ball_circle.colliderect(platform):
            x = platform.right + 13
            vx = -vx * 0.5
            if activateability and wasinair and abilitytype == "sticky":
                vy = 0
                vx = 0
                inair = False
                onground = True
                activateability = False
                print("This is true!")
                break

        elif ball_circle.colliderect(platform) and vy >= 0:
            onground = True
            y = platform.y - 10

            if activateability and wasinair and abilitytype == "sticky":
                vy = 0
                vx = 0
                inair = False
                onground = True
                activateability = False
                print("This is true!")
                break

            vy *= -0.75
            vx *= 0.6

            if abs(vy) <= abs(a):
                inair = False
                onground = True
                vy = 0
                vx = 0
                break
            else:
                onground = False

    if not onground:
        inair = True
    wasinair = inair

while running:
    if theme == "grass":
        bgc = (93, 226, 231)
    if theme == "fire":
        bgc = (44, 2, 2)
    if theme == "ice":
        bgc = (255, 255, 255)
    if theme == "space":
        bgc = (21, 0, 42)
    screen.fill(bgc)
    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == "game" and event.button == 1 and inair == False and canfire == True and not abilityrect.collidepoint(mx,my):
                firing = True
                onground = True
                inair = False
            if abilityrect.collidepoint(mx,my) and not inair:
                activateability = not activateability
                abilitytype = "sticky"
            if state == "queue" and event.button == 1:
                if not ready:
                    print("Sent ready message")
                    ready = True
                    packet = json.dumps({"type": "ready", "id": player_id}) + "\n"
                    client.sendall(packet.encode())

        if event.type == pygame.MOUSEBUTTONUP:
            if state == "game" and event.button == 1 and canfire == True and inair == False and onground == True and not abilityrect.collidepoint(mx,my):
                firing = False
                inair = True
                onground = False
                strokes += 1


            # Play button
            if state == "title" and event.button == 1:
                if 550 <= mx and mx <= 650 and 500 <= my and my <= 600 and name.strip() != "":
                    state = "queue"
                    firing = False
                    inair = True
                    a = -2

        if event.type == pygame.KEYDOWN:
            if state == "title":
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 20:
                    name += event.unicode
            if state == "game":
                if event.key == pygame.K_1:
                    theme = "grass"
                if event.key == pygame.K_2:
                    theme = "fire"
                if event.key == pygame.K_3:
                    theme = "ice"
                if event.key == pygame.K_4:
                    theme = "space"

    if state == "queue":
        send_player_data()
        if title_slide % 3 == 0:
            screen.blit(forest, (0, 0))
        elif title_slide % 3 == 1:
            screen.blit(tundra, (0, 0))
        else:
            screen.blit(volcano, (0, 0))
        screen.blit(logo, (400, 20))

        total_players = len(other_players) + 1
        ready_count = 0
        if ready:
            ready_count += 1
        for player in other_players.values():
            if player.get("ready"):
                ready_count += 1

        pygame.draw.rect(screen, (50, 50, 50), (495, 440, 210, 80), border_radius=15)
        pygame.draw.rect(screen, (70, 70, 70), (500, 445, 200, 70), border_radius=12)
        count_text = font.render(f"{ready_count}/{total_players}", True, (255, 255, 255))
        count_rect = count_text.get_rect(center=(600, 480))
        screen.blit(count_text, count_rect)

        list_title = font2.render("PLAYERS", True, (0,0,0))
        screen.blit(list_title, (850, 200))

        y_offset = 250
        if ready:
            player_box_color = (0, 200, 0)
        else:
            player_box_color = (100, 100, 100)
        pygame.draw.rect(screen, player_box_color, (820, y_offset, 320, 60), border_radius=10)
        pygame.draw.rect(screen, (50, 50, 50), (825, y_offset + 5, 310, 50), border_radius=8)

        my_name_text = font2.render(name, True, (255, 255, 255))
        screen.blit(my_name_text, (840, y_offset + 17))

        # Ready status
        if ready:
            ready_text = font2.render("READY", True, (0, 255, 0))
        else:
            ready_text = font2.render("NOT READY", True, (255, 100, 100))
        ready_rect = ready_text.get_rect(right=1120, centery=y_offset + 30)
        screen.blit(ready_text, ready_rect)

        y_offset += 70

        # Other players
        for pid, pdata in other_players.items():
            is_ready = pdata.get("ready", False)
            if ready:
                player_box_color = (0, 200, 0)
            else:
                player_box_color = (100, 100, 100)
            pygame.draw.rect(screen, player_box_color, (820, y_offset, 320, 60), border_radius=10)
            pygame.draw.rect(screen, (50, 50, 50), (825, y_offset + 5, 310, 50), border_radius=8)

            player_name_text = font2.render(pdata['name'], True, (255, 255, 255))
            screen.blit(player_name_text, (840, y_offset + 17))

            if is_ready:
                ready_text = font2.render("READY", True, (0, 255, 0))
            else:
                ready_text = font2.render("NOT READY", True, (255, 100, 100))
            ready_rect = ready_text.get_rect(right=1120, centery=y_offset + 30)
            screen.blit(ready_text, ready_rect)

            y_offset += 70

        if not ready:
            button_color = (0, 180, 0)
            button_text = "READY UP"
        else:
            button_color = (180, 180, 0)
            button_text = "WAITING..."

        pygame.draw.rect(screen, button_color, (445, 550, 310, 80), border_radius=15)
        pygame.draw.rect(screen, (60, 60, 60), (450, 555, 300, 70), border_radius=12)
        ready_button_text = font.render(button_text, True, (255, 255, 255))
        ready_button_rect = ready_button_text.get_rect(center=(600, 590))
        screen.blit(ready_button_text, ready_button_rect)

        if all_ready:
            state = "game"


    if state == "title":
        send_player_data()
        if title_slide % 3 == 0:
            screen.blit(forest, (0, 0))
        elif title_slide % 3 == 1:
            screen.blit(tundra, (0, 0))
        else:
            screen.blit(volcano, (0, 0))

        screen.blit(logo, (400, 0))
        screen.blit(play, (550, 500))

        pygame.draw.rect(screen, (0, 0, 0), (395, 355, 410, 90), border_radius=25)
        pygame.draw.rect(screen, (255, 255, 255), (400, 360, 400, 80), border_radius=20)
        inputtext = font.render(name, True, (0, 0, 0))
        screen.blit(inputtext, (425, 385))

    if state == "game":
        send_player_data()
        if not spectating:
            if inair:
                vy -= a
                x += vx
                y += vy
                onground = False
                firing = False
                checkplatform()
            offset_x = x - WIDTH // 2
            offset_y = y - HEIGHT // 2
        else:
            offset_x = spectate_x - WIDTH // 2
            offset_y = spectate_y - HEIGHT // 2

        checkcanfire()
        respawn()

        for platform in platforms[level]:
            if theme == "grass":
                color1 = (67, 33, 9)
                color2 = (0, 150, 0)
            if theme == "fire":
                color2 = (183, 39, 39)
                color1 = (88, 70, 49)
            if theme == "ice":
                color2 = (1, 248, 248)
                color1 = (32, 192, 192)
            if theme == "space":
                color2 = (169, 59, 237)
                color1 = (80, 80, 80)
            pygame.draw.rect(screen, color1,
                             (platform.x - offset_x, platform.y - offset_y, platform.width, platform.height),
                             border_radius=5)
            pygame.draw.rect(screen, color2,
                             (platform.x - 2 - offset_x, platform.y - offset_y, platform.width + 4, 10),
                             border_radius=10)

        for coin in coins[level]:
            pygame.draw.circle(screen, (200, 200, 0), (
                coin.x - offset_x + coin.width / 2,
                coin.y - offset_y + coin.height / 2
            ), coin.width / 2 + 5)
            pygame.draw.circle(screen, (255, 255, 0), (
                coin.x - offset_x + coin.width / 2,
                coin.y - offset_y + coin.height / 2
            ), coin.width / 2)

            if not spectating:
                ball_circle = pygame.Rect(x - 13, y - 13, 26, 26)
                if ball_circle.colliderect(coin):
                    money += 100
                    coin.x = -100000000
                    break

        # Draw hole
        newholerect = pygame.Rect(hole[level].x - offset_x, hole[level].y - offset_y, hole[level].width,
                                  hole[level].height)
        pygame.draw.rect(screen, (0, 0, 0), newholerect)
        if not spectating:
            ball_circle = pygame.Rect(x - 13, y - 13, 26, 26)
            pygame.draw.rect(screen, (0,0,0), (abilityrect.x, abilityrect.y, abilityrect.width, abilityrect.height))

            if ball_circle.colliderect(hole[level]):
                hole_complete = True
                spectating = True
                spectate_x = hole[level].x + hole[level].width // 2
                spectate_y = hole[level].y + hole[level].height // 2
                packet = json.dumps({"type": "hole_complete", "id": player_id}) + "\n"
                try:
                    client.sendall(packet.encode())
                except:
                    print("Problem")
                offset_x = 0
                offset_y = 0
                prevx = 0
                prevy = 0
                respawn()
                if level >= len(platforms) - 1:
                    pass

        # Local player
        if not spectating:
            pygame.draw.circle(screen, (100, 100, 100), (x - offset_x, y - offset_y), 13)
            pygame.draw.circle(screen, (255, 255, 255), (x - offset_x, y - offset_y), 10)

            fontw, fonth = font2.size(name)
            pygame.draw.rect(screen, (0, 0, 0),
                             (x - offset_x - fontw / 2 - 10, y - offset_y - 55 - fonth / 2, fontw + 20, fonth + 10),
                             border_radius=10)
            my_name = font2.render(name, True, (255, 255, 255))
            my_name_rect = my_name.get_rect(center=(x - offset_x, y - offset_y - 50))
            screen.blit(my_name, my_name_rect)
        else:
            pygame.draw.circle(screen, (100, 100, 100), (spectate_x - offset_x, spectate_y - offset_y), 13)
            pygame.draw.circle(screen, (255, 255, 255), (spectate_x - offset_x, spectate_y - offset_y), 10)

            fontw, fonth = font2.size(name)
            pygame.draw.rect(screen, (0, 0, 0),
                             (spectate_x - offset_x - fontw / 2 - 10, spectate_y - offset_y - 55 - fonth / 2,
                              fontw + 20, fonth + 10),
                             border_radius=10)
            my_name = font2.render(name, True, (255, 255, 255))
            my_name_rect = my_name.get_rect(center=(spectate_x - offset_x, spectate_y - offset_y - 50))
            screen.blit(my_name, my_name_rect)

        # Other players
        for pid, pdata in other_players.items():
            smoothing = 0.2
            pdata["x"] += (pdata["tx"] - pdata["x"]) * smoothing
            pdata["y"] += (pdata["ty"] - pdata["y"]) * smoothing

            other_x = pdata["x"] - offset_x
            other_y = pdata["y"] - offset_y

            pygame.draw.circle(screen, (200, 100, 100), (int(other_x), int(other_y)), 13)
            pygame.draw.circle(screen, (255, 100, 100), (int(other_x), int(other_y)), 10)

            fontw, fonth = font2.size(pdata["name"])
            pygame.draw.rect(screen, (100, 100, 100),
                             (other_x - fontw / 2 - 10, other_y - 55 - fonth / 2, fontw + 20, fonth + 10),
                             border_radius=10)
            name_text = font2.render(pdata["name"], True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(other_x, other_y - 50))
            screen.blit(name_text, name_rect)

        if firing and not spectating:
            viy = -15
            vy = viy
            prevx = x
            prevy = y
            actual_mx = mx + offset_x
            actual_my = my + offset_y

            dx = actual_mx - x
            dy = actual_my - y

            max_x = 200

            if abs(dx) > max_x:
                dx = max_x * (dx / abs(dx))

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
            while abs(new_dx - x) < 400 and abs(new_dy - y) < 400 and a != 0 and dx != 0 and t != 0 and canfire == True:
                new_dx = x + vx * t_temp
                new_dy = y + viy * t_temp - 0.5 * a * (t_temp ** 2)
                pygame.draw.circle(screen, (255, 0, 0), (new_dx - offset_x, new_dy - offset_y), 5)
                t_temp += 2

        # DISPLAY the user interfaace (at the very end)

        # Amt of money user has
        pygame.draw.rect(screen, (0, 0, 0), (495, 20, 210, 65), border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), (500, 25, 200, 55), border_radius=10)
        money_text = font.render("$" + str(money), True, (0, 0, 0))
        money_rect = money_text.get_rect(center=(600, 50))
        screen.blit(money_text, money_rect)

        # Number of strokes the user took
        pygame.draw.rect(screen, (0, 0, 0), (510, 90, 180, 50), border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), (515, 95, 170, 40), border_radius=10)
        money_text = font2.render("Strokes: " + str(strokes), True, (0, 0, 0))
        money_rect = money_text.get_rect(center=(600, 115))
        screen.blit(money_text, money_rect)

        if spectating:
            finished_count = 1
            total_players = len(other_players) + 1
            for pdata in other_players.values():
                if pdata.get("hole_complete", False):
                    finished_count += 1

            pygame.draw.rect(screen, (0, 0, 0), (395, 680, 410, 90), border_radius=15)
            pygame.draw.rect(screen, (100, 100, 255), (400, 685, 400, 80), border_radius=12)
            spectate_text = font2.render("WAITING FOR OTHERS", True, (255, 255, 255))
            spectate_rect = spectate_text.get_rect(center=(600, 710))
            screen.blit(spectate_text, spectate_rect)

            count_text = font2.render(f"{finished_count}/{total_players} finished", True, (255, 255, 255))
            count_rect = count_text.get_rect(center=(600, 740))
            screen.blit(count_text, count_rect)

    title_slideshow += 1
    if title_slideshow % 300 == 0:
        title_slide += 1

    pygame.display.flip()
    clock.tick(60)


"""

TO DO LIST:
- bouncing in intro
- changing backgrounds
- max power limit (so then user can just max send it)
"""