# HELLO TEST
# HELLO STICKY RICKY BACK
import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# IMAGES HERE
bgimg = pygame.image.load("img/pixelsky.jpg").convert()
bgimg = pygame.transform.scale(bgimg, (800, 600))

logo = pygame.image.load("img/logo.png").convert_alpha()
logo = pygame.transform.scale(logo, (400, 400))

forest = pygame.image.load("img/forest.jpg").convert()
forest = pygame.transform.scale(forest, (800, 600))

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
    pygame.Rect(300,400,500,50),
    pygame.Rect(0,510,800,90),
    pygame.Rect(50, 200, 300, 50),
    pygame.Rect(0, 0, 50, 500)
]


def checkplatform():
    global vy, inair, y,onground, vx,x

    ball_circle = pygame.Rect(x - 13, y - 13, 26, 26)


    for platform in platforms:
        if ball_circle.colliderect(platform) and vy <= 0 and abs(y-(platform.y+platform.height)) <= 15:
            print("collide")
            y = platform.y+platform.height+13
            vy *= -0.5
        elif x < platform.left and ball_circle.colliderect(platform) and vx > 0:
            x = platform.left - 13
            vx = -vx * 0.5
        elif x > platform.right and vx < 0 and ball_circle.colliderect(platform):
            x = platform.right + 13
            vx = -vx * 0.5
        elif ball_circle.colliderect(platform) and vy > 0:
            onground = True
            y = platform.y - 10
            vy *= -0.75
            vx *= 0.6
            if abs(vy) < 0.1 or abs(vx) < 0.1:
                print ("in air is now false")
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
    screen.fill((0, 0, 0))
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == "game" and event.button == 1 and inair == False:
                firing = True
                onground = True
                inair = False

        if event.type == pygame.MOUSEBUTTONUP:
            if state == "game" and event.button == 1:
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

        # Background image yay
        screen.blit(bgimg, (0, 0))

        # Draw main platforms, DRAW OTHER PLATFORMS HERE LATER
        pygame.draw.rect(screen, (0, 255, 0), (0, 510, 800, 90))

        # here's the actual ball
        pygame.draw.circle(screen, (100, 100, 100), (x, y), 13)
        pygame.draw.circle(screen, (255, 255, 255), (x, y), 10)
        for platform in platforms:
            pygame.draw.rect(screen,(0,255,0),platform, border_radius = 5)
            pygame.draw.rect(screen, (0, 150, 0), (platform.x-2, platform.y, platform.width+4, 10),  border_radius = 10)
            
        if firing:
            viy = -15
            vy = viy
            if mx - x == 0:
                theta = math.atan2(my - y, mx - x)
            else:
                theta = 1
            dy = my - y
            if dy == 0:
                a = 0
            else:
                a = -(vy) ** 2 / (2 * dy)
            t = 2 * dy / vy
            if t != 0:
                vx = (mx - x) / t

            # now here's the trajectory of the ball
            # we need x and y in terms of t
            t_temp = 0
            new_dx = x
            new_dy = y

            while abs(new_dx - 400) < 400 and a != 0 and mx - x != 0 and t != 0:
                new_dx = x + vx * t_temp
                new_dy = y + viy * t_temp - 0.5 * a * t_temp ** 2
                pygame.draw.circle(screen, (255, 0, 0), (new_dx, new_dy), 5)
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
