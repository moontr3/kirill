############## INITIALIZATION ##############

import pygame as pg
import easing_functions as easing
import random
import draw

pg.init()

# app size
windowx = 1280
windowy = 720
# window size, changes on resize
screenx = 1280
screeny = 720

clock = pg.time.Clock()
fps = 60

window = pg.display.set_mode((screenx,screeny), pg.RESIZABLE)
screen = pg.Surface((windowx, windowy))

running = True
pg.display.set_caption('caption')
draw.def_surface = screen

halfx = windowx//2
halfy = windowy//2

# app variables


# app functions

def get_distance(p1, p2):
    return ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5


# app classes

class Tree:
    def __init__(self, pos):
        self.pos = pos
        self.rect = pg.Rect(pos[0]-100, pos[1]-100, 200,200)

    def draw(self, pos):
        pg.draw.circle(screen, (10,40,10), pos, 100)


class Coal:
    def __init__(self, pos):
        self.pos = pos
        self.rect = pg.Rect(pos[0]-15, pos[1]-15, 30,30)

    def draw(self, pos):
        pg.draw.circle(screen, (5,5,5), pos, 15)


class Game:
    def __init__(self):
        self.player_pos = [5000,5000]
        self.it_pos = [5000,50]
        self.cam_pos = [5000,5000]

        self.speed = 5
        self.temperature = 0.7
        self.stamina = 500
        self.stamina_restore = 0
        self.fuel = 140

        self.props = []
        self.gen_world()

    def gen_world(self, trees=150, coal=30):
        for i in range(coal):
            pos = (random.randint(200,9800), random.randint(200,9800))
            self.props.append(Coal(pos))

        for i in range(trees):
            pos = (random.randint(200,9800), random.randint(200,9800))
            self.props.append(Tree(pos))

        new = []
        for i in self.props:
            if get_distance(i.pos, (5000,5000)) < 500:
                continue
            new.append(i)
        self.props = new

    def world_to_screen(self, point):
        return [point[0]-self.cam_pos[0]+halfx, point[1]-self.cam_pos[1]+halfy]

    def draw(self):
        player = self.world_to_screen(self.player_pos)
        center = self.world_to_screen((5000,5000))

        # BG
        screen.fill((5,15,5))

        # player
        pg.draw.circle(screen, (255,255,255), player, 25)

        draw.text(f'{self.player_pos[0]}, {self.player_pos[1]}', (player[0]+30, player[1]-10), size=14, v='m')
        draw.text(f'{round(self.player_dst, 1)} pixels away', (player[0]+30, player[1]+10), size=14, v='m')
        draw.text(f'temp {round(self.temperature, 3)}', (player[0]+30, player[1]+30), size=14, v='m')
        draw.text(f'fuel {round(self.fuel, 1)}', (player[0]+30, player[1]+50), size=14, v='m')
        draw.text(f'stamina {self.stamina}', (player[0]+30, player[1]+70), size=14, v='m')
        draw.text(f'props {(len(self.props))}', (player[0]+30, player[1]+90), size=14, v='m')
        
        # campfire
        pg.draw.circle(screen, (255,255,255), center, 15)
        pg.draw.circle(screen, (255,255,0), center, self.safe_zone, 1)

        pg.draw.line(screen, (255,0,0), center, player, 1)

        # props
        for i in self.props:
            i.draw(self.world_to_screen(i.pos))

    def update(self):
        # sprint
        moving = keys[pg.K_w] or keys[pg.K_a] or keys[pg.K_s] or keys[pg.K_d]
        self.speed = 5+int(keys[pg.K_LSHIFT] and self.stamina > 0)*3

        if keys[pg.K_LSHIFT] and moving and self.stamina > 0:
            self.stamina -= 1
            self.stamina_restore = 100
        elif self.stamina_restore > 0:
            self.stamina_restore -= 1
        elif self.stamina < 500:
            self.stamina += 2
            
        # player movement
        if moving:
            if keys[pg.K_w]:
                self.player_pos[1] -= self.speed
            if keys[pg.K_s]:
                self.player_pos[1] += self.speed
            if keys[pg.K_a]:
                self.player_pos[0] -= self.speed
            if keys[pg.K_d]:
                self.player_pos[0] += self.speed

            self.player_pos[0] = max(0, min(10000, self.player_pos[0]))
            self.player_pos[1] = max(0, min(10000, self.player_pos[1]))

        # cam movement
        self.cam_pos[0] += (self.player_pos[0]-self.cam_pos[0])/7
        self.cam_pos[1] += (self.player_pos[1]-self.cam_pos[1])/7
        self.cam_pos = [
            max(halfx, min(10000-halfx, self.cam_pos[0])),
            max(halfy, min(10000-halfy, self.cam_pos[1]))
        ]

        # campfire
        self.safe_zone = self.fuel*2+30
        self.it_dst = get_distance(self.it_pos, (5000,5000))
        self.player_dst = get_distance(self.player_pos, (5000,5000))
        if self.fuel > 0.0:
            self.fuel -= 0.02
            if self.fuel < 0.0:
                self.fuel = 0.0

        # temperature
        if self.player_dst < self.safe_zone:
            if self.temperature < 1.0:
                self.temperature += self.fuel*0.00001
                if self.temperature > 1.0:
                    self.temperature = 1.0
        else:
            if self.temperature > 0.0:
                self.temperature -= 0.00025
                if self.temperature < 0.0:
                    self.temperature = 0.0


# preparing

app = Game()


# main loop

while running:
    # input
    events = pg.event.get()
    mouse_pos = pg.mouse.get_pos()
    mouse_press = pg.mouse.get_pressed(5)
    mouse_moved = pg.mouse.get_rel()
    keys = pg.key.get_pressed()

    # events
    for event in events:
        if event.type == pg.QUIT:
            running = False 

        if event.type == pg.VIDEORESIZE:
            screenx = event.w
            screeny = event.h
            if screenx <= 640:
                screenx = 640
            if screeny <= 480:
                screeny = 480
            window = pg.display.set_mode((screenx,screeny), pg.RESIZABLE)

    # updating
    app.update()
    app.draw()

    surface = pg.transform.smoothscale(screen, (screenx, screeny))
    window.blit(surface, (0,0))
    pg.display.flip()
    clock.tick(fps)
    dfps = round(clock.get_fps(), 1)