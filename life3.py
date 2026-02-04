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

TPS = 600
FPS = 60

class Game(arcade.View):
    def __init__(self):
        super().__init__()
        self.map = [[0]*MAP_HEIGHT]*MAP_WIDTH
        self.batch = arcade.shape_list.ShapeElementList()

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def on_update(self, delta_time: float):
        self.batch.append(arcade.shape_list.create_rectangle_filled(
            randint(0, MAP_WIDTH)*GRID_SIZE, randint(0, MAP_HEIGHT)*GRID_SIZE,
            GRID_SIZE, GRID_SIZE, (255,0,0)
            ))
        print(type(self.batch))

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
