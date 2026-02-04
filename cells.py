import arcade
from math import *
from random import *

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_RISIZABLE = True
SCREEN_FULLSCREEN = False

GREENS_MIN_QUANTITY = 1
REDS_MIN_QUANTITY = 10

FOOD_SPAWN_CHANCE = 1.1
FOOD_LIMIT = 500

MUTATION_MULT = 100

TPS = 600
FPS = 60

class Game(arcade.View):
    def __init__(self):
        super().__init__()
        self.greens = []
        self.reds = []
        self.food = []

    def on_draw(self):
        self.clear((255,255,255))
        for cell in self.greens:
            arcade.draw_circle_filled(cell.pos[0], cell.pos[1], cell.radius, (100,255,100))
        for cell in self.reds:
            arcade.draw_circle_filled(cell.pos[0], cell.pos[1], cell.radius, (255,100,100))
        for ball in self.food:
            arcade.draw_circle_filled(ball.pos[0], ball.pos[1], ball.radius, ball.color)

    def on_update(self, delta_time: float):
        if len(self.greens) < GREENS_MIN_QUANTITY:
            self.greens.append(Cell(
                [random()*SCREEN_WIDTH, random()*SCREEN_HEIGHT],
                randint(10, 1000),
                randint(10,100),
                randint(10,1000),
                'green'
                ))
        if len(self.reds) < REDS_MIN_QUANTITY:
            self.reds.append(Cell(
                [random()*SCREEN_WIDTH, random()*SCREEN_HEIGHT],
                randint(10, 1000),
                randint(10,100),
                randint(10,100),
                'red'
                ))
        if random() < FOOD_SPAWN_CHANCE and len(self.food) < FOOD_LIMIT:
            self.food.append(Food((random()*SCREEN_WIDTH,random()*SCREEN_HEIGHT),random()*250))
        for cell in self.greens+self.reds:
            cell.act()

class Food:
    def __init__(self, pos, mass):
        self.pos = pos
        self.mass = mass
        self.radius = sqrt(mass/pi)
        #self.color = (randint(0,255),randint(0,255),randint(0,255))
        self.color = (0,0,0)

class Cell:
    def __init__(self, pos, mass, strenght, sight, typ):
        self.pos = pos
        self.mass = mass
        self.strenght = strenght
        self.speed = strenght/mass*5
        self.sight = sight
        self.typ = typ
        self.radius = sqrt(mass/pi)
        self.max_hunger = mass
        self.hunger = self.max_hunger/2
        self.hunger_per_tick = mass*(strenght+sight)*0.00001
        self.target = None
        self.lst = None

    def act(self):
        if self.lst is None:
            self.lst = game.greens if self.typ == 'green' else game.reds
        lst = game.food if self.typ == 'green' else game.greens
        if self.target is None:
            dists = []
            for target in lst:
                dists.append(((self.pos[0]-target.pos[0])**2 + (self.pos[1]-target.pos[1])**2,target)) if target.mass <= self.mass else None
            dists.sort()
            self.target = dists[0][1] if len(dists) > 0 and dists[0][0] <= self.sight**2 else None

        if self.target is not None:
                self.pos[0] += (sqrt(self.speed) if self.target.pos[0] > self.pos[0] else -sqrt(self.speed))
                self.pos[1] += (sqrt(self.speed) if self.target.pos[1] > self.pos[1] else -sqrt(self.speed))
                if (self.pos[0]-self.target.pos[0])**2 + (self.pos[1]-self.target.pos[1])**2 < self.radius**2:
                    if self.target in lst:
                        lst.remove(self.target)
                        self.hunger += self.target.mass
                        if self.hunger > self.max_hunger:
                            self.lst.append(Cell(
                                [self.pos[0]+self.radius*2, self.pos[1]],
                                max(self.mass+(random()-0.5)*2*MUTATION_MULT,1),
                                max(self.strenght+(random()-0.5)*2*MUTATION_MULT,0),
                                max(self.sight+(random()-0.5)*2*MUTATION_MULT,0),
                                self.typ
                                ))
                            self.hunger /= 2
                    self.target = None
        else:
            self.pos[0] += (random()-0.5)*2*self.speed
            self.pos[1] += (random()-0.5)*2*self.speed
        self.hunger -= self.hunger_per_tick
        if self.hunger <= 0:
            self.lst.remove(self)
            return None


window = arcade.Window(
    title='Cells',
    width=SCREEN_WIDTH,
    height=SCREEN_HEIGHT,
    fullscreen=SCREEN_FULLSCREEN,
    resizable=SCREEN_RISIZABLE,
    update_rate=1/TPS,
    draw_rate=1/FPS,
    )
game = Game()
window.show_view(game)
arcade.run()
