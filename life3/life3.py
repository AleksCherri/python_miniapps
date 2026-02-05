import arcade
from random import *

MAP_WIDTH = 1920
MAP_HEIGHT = 1080

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
        self.cell_queue = set()
        self.sprite_list = arcade.SpriteList()

        self.camera = arcade.camera.Camera2D()
        self.cam_x, self.cam_y = SCREEN_WIDTH/2, SCREEN_HEIGHT/2
        self.camera.position = self.cam_x, self.cam_y
        self.cam_speed = 500
        self.pressed_keys = set()
        self.move_binds = {
            arcade.key.W: (0, 1),
            arcade.key.S: (0, -1),
            arcade.key.A: (-1, 0),
            arcade.key.D: (1, 0),

            arcade.key.UP: (0, 1),
            arcade.key.DOWN: (0, -1),
            arcade.key.LEFT: (-1, 0),
            arcade.key.RIGHT: (1, 0),
        }

    def on_draw(self):
        self.camera.use()
        self.clear()
        self.sprite_list.draw()

    def on_update(self, delta_time: float):
        self.add_cell((randint(0,255),randint(0,255),randint(0,255)),(randint(0,MAP_WIDTH-1),randint(0,MAP_HEIGHT-1)))
        
        dx,dy = 0,0
        for key in self.pressed_keys:
            vx, vy = self.move_binds[key]
            dx += vx
            dy += vy
        if dx != 0 or dy != 0:
            self.cam_x += dx*self.cam_speed*delta_time/self.camera.zoom
            self.cam_y += dy*self.cam_speed*delta_time/self.camera.zoom
            self.camera.position = self.cam_x, self.cam_y

    def on_key_press(self, symbol, modifiers):
        if symbol in self.move_binds:
            self.pressed_keys.add(symbol)

    def on_key_release(self, symbol, modifiers):
        self.pressed_keys.discard(symbol)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if scroll_y > 0 and self.camera.zoom < 100:
            self.camera.zoom *= 1.1
        elif scroll_y < 0 and self.camera.zoom > 0.1:
            self.camera.zoom /= 1.1

    def add_cell(self, color, pos):
        x, y = pos
        if type(self.map[x][y]) == Cell:
            return None
        self.map[x][y] = Cell()
        self.cell_queue.add((x,y))
        sprite = arcade.Sprite('sprite.bmp')
        sprite.color = color
        sprite.position = x, y
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
