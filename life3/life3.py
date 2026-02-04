import arcade
from math import *
from random import *

MAP_WIDTH = 20
MAP_HEIGHT = 20
GRID_SIZE = 50

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_RISIZABLE = True
SCREEN_FULLSCREEN = False

TPS = 60
FPS = 60

class Game(arcade.View):
    def __init__(self):
        super().__init__()

        self.map = [[0] * MAP_HEIGHT for _ in range(MAP_WIDTH)]
        self.sprite_list = arcade.SpriteList()
        self.camera = arcade.camera.Camera2D()

    def on_draw(self):
        self.camera.use()
        self.clear()
        self.sprite_list.draw()

    def on_update(self, delta_time: float):
        self.add_cell((randint(0,255),randint(0,255),randint(0,255)),(randint(0,MAP_WIDTH-1),randint(0,MAP_HEIGHT-1)))

    def add_cell(self, color, pos):
        x, y = pos
        if type(self.map[x][y]) == Cell:
            return None
        self.map[x][y] = Cell()
        sprite = arcade.Sprite('sprite.bmp', scale=GRID_SIZE)
        sprite.color = color
        sprite.position = x*GRID_SIZE, y*GRID_SIZE
        self.sprite_list.append(sprite)

class Cell:
    def __init__(self):
        self.mass = 100

window = arcade.Window(
    title='Life3',
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
