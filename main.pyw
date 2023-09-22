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
pg.display.set_caption('@ Silly Kirill')
draw.def_surface = screen

halfx = windowx//2
halfy = windowy//2

# app variables


# app functions

def get_distance(p1, p2):
    return ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5


# app classes

class Skin:
    def __init__(self, image, x_dimension, speed=5, sprint=3):
        self.image = 'skins/'+image+'.jpg'
        self.x_dimension = x_dimension
        self.size = [75*self.x_dimension, 75]
        self.speed = speed
        self.sprint = sprint
        

class Prop:
    def __init__(self, pos):
        self.pos = pos
        self.behind = False
        self.deletable = False

    def draw(self, pos):
        pg.draw.circle(screen, self.color, pos, self.radius)

    def update(self):
        pass

    def collect(self):
        pass


class Tree(Prop):
    def __init__(self, pos):
        super().__init__(pos)
        self.rect = pg.Rect(pos[0]-100, pos[1]-100, 200,200)
        self.color = (15,40,15)
        self.radius = 100

        self.cut_down = False
        self.cut_down_key = 0.0
        self.cd_anim_key = 0.0
        self.blink_anim = -100

    def draw(self, pos):
        if not self.cut_down:
            pg.draw.circle(screen, self.color, pos, self.radius)
        elif (self.blink_anim < 0) or (int(self.blink_anim/3)%2==0):
            pg.draw.line(screen, (50,40,15), (pos[0], pos[1]), (pos[0]-200*self.cd_anim_key, pos[1]), int(40-(40*(self.cd_anim_key/3))))
            pg.draw.circle(screen, (50,40,15), (pos[0], pos[1]+1), round((40-(40*(self.cd_anim_key/3)))/2))
            pg.draw.circle(screen, self.color, (pos[0]-200*self.cd_anim_key, pos[1]), self.radius-(self.radius*(self.cd_anim_key/4)))

    def update(self):
        if self.cut_down:
            if self.cut_down_key < 1.0:
                self.cut_down_key += 0.01
                self.cd_anim_key = easing.QuarticEaseIn(0,1,1).ease(self.cut_down_key)
            else:
                if not self.behind:
                    global app
                    app.sticks += random.randint(2,3)
                self.blink_anim += 1
                self.behind = True
                if self.blink_anim > 35:
                    self.deletable = True

    def collect(self):
        if not self.cut_down:
            self.cut_down = True
            return True
        return False


class Coal(Prop):
    def __init__(self, pos):
        super().__init__(pos)
        self.pos = pos
        self.behind = True
        self.deletable = False
        self.rect = pg.Rect(pos[0]-15, pos[1]-15, 30,30)
        self.color = (15,15,15)
        self.radius = 15

    def collect(self):
        global app
        app.coal += 1
        self.deletable = True
        return True
    

class Game:
    def __init__(self, skin=Skin('normal', 0.8)):
        self.player_pos = [5000,5000]
        self.it_pos = [5000,50]
        self.cam_pos = [5000,5000]
        self.skin = skin
        self.speed = self.skin.speed

        self.temperature = 0.7
        self.stamina = 500
        self.stamina_restore = 0
        self.fuel = 140
        self.coal = 0
        self.sticks = 3
        self.matches = 2

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
        screen.fill((10,30,10))

        # props behind player
        for i in self.props:
            if i.behind:
                i.draw(self.world_to_screen(i.pos))

        # player
        draw.image(self.skin.image, player, self.skin.size, h='m', v='m')

        draw.text(f'{self.player_pos[0]}, {self.player_pos[1]}', (player[0]+30, player[1]-10), size=14, v='m')
        draw.text(f'{round(self.player_dst, 1)} pixels away', (player[0]+30, player[1]+10), size=14, v='m')
        draw.text(f'temp {round(self.temperature, 3)}', (player[0]+30, player[1]+30), size=14, v='m')
        draw.text(f'fuel {round(self.fuel, 1)}', (player[0]+30, player[1]+50), size=14, v='m')
        draw.text(f'stamina {self.stamina}', (player[0]+30, player[1]+70), size=14, v='m')
        draw.text(f'props {(len(self.props))}', (player[0]+30, player[1]+90), size=14, v='m')
        
        # campfire
        pg.draw.circle(screen, (255,255,255), center, 15)
        pg.draw.circle(screen, (255,255,0), center, self.safe_zone, 1)

        # props
        for i in self.props:
            if not i.behind:
                i.draw(self.world_to_screen(i.pos))

        # gui
        draw.text(f'matches', (30, windowy-120), size=14, v='m')
        draw.text(f'sticks', (30, windowy-80), size=14, v='m')
        draw.text(f'coal', (30, windowy-40), size=14, v='m')

        draw.text(str(self.matches), (135, windowy-120), size=21, v='m')
        draw.text(str(self.sticks), (110, windowy-80), size=21, v='m')
        draw.text(str(self.coal), (90, windowy-40), size=21, v='m')


    def update(self):
        # sprint
        moving = [i for i in [keys[pg.K_w], keys[pg.K_a], keys[pg.K_s], keys[pg.K_d]] if i]
        self.speed = self.skin.speed+int(keys[pg.K_LSHIFT] and self.stamina > 0)*self.skin.sprint
        if len(moving) == 2:
            self.speed *= 0.725

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

            self.player_pos[0] = round(max(0, min(10000, self.player_pos[0])))
            self.player_pos[1] = round(max(0, min(10000, self.player_pos[1]))) 

        # cam movement
        self.cam_pos[0] += (self.player_pos[0]-self.cam_pos[0])/7
        self.cam_pos[1] += (self.player_pos[1]-self.cam_pos[1])/7
        self.cam_pos = [
            max(halfx, min(10000-halfx, self.cam_pos[0])),
            max(halfy, min(10000-halfy, self.cam_pos[1]))
        ]

        # props
        not_collected = True
        for i in self.props:
            i.update()
            if pg.K_e in just_pressed and not_collected\
                and get_distance(i.pos, self.player_pos) < i.radius+25:
                    a = i.collect()
                    if a:
                        not_collected = False
        self.props = [i for i in self.props if not i.deletable]

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
    just_pressed = []

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

        if event.type == pg.KEYDOWN:
            just_pressed.append(event.key)

    # updating
    app.update()
    app.draw()

    surface = pg.transform.smoothscale(screen, (screenx, screeny))
    window.blit(surface, (0,0))
    pg.display.flip()
    clock.tick(fps)
    dfps = round(clock.get_fps(), 1)