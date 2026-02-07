import arcade
from random import *

MAP_WIDTH = 1920
MAP_HEIGHT = 1080

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_RISIZABLE = False
SCREEN_FULLSCREEN = False

TPS = 60
FPS = 60

GENOME_MAX_LEN = 100

cell_types = ('sprout','stem','leaf','root','seed')
cell_energy_consumption = {'sprout':3,'stem':1,'leaf':1,'root':1,'seed':2}
cell_energy_gen = {'leaf':7, 'root':10}
cell_colors = {'sprout':(200,200,200), 'stem':(100,100,100), 'leaf':(100,200,100), 'root':(200,100,100), 'seed':(200,200,100)}

class Game(arcade.View):
    def __init__(self):
        super().__init__()

        self.map = [[0] * MAP_HEIGHT for _ in range(MAP_WIDTH)]
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
        }
        self.add_cell(Sprout(
            (randint(0,MAP_WIDTH-1),randint(0,MAP_HEIGHT-1)),
            None, None, 100, None, 1
            ))

    def on_draw(self):
        self.camera.use()
        self.clear()
        self.sprite_list.draw()

    def on_update(self, delta_time: float):
        #self.add_cell((randint(0,255),randint(0,255),randint(0,255)),(randint(0,MAP_WIDTH-1),randint(0,MAP_HEIGHT-1)))
        
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

    def add_cell(self, cell):
        x, y = cell.pos
        if type(self.map[x][y]) == Cell:
            return None
        self.map[x][y] = cell
        sprite = arcade.Sprite('sprite.bmp', scale=0.95)
        sprite.color = cell_colors[cell.type]
        sprite.position = x, y
        self.sprite_list.append(sprite)
        cell.sprite = sprite

class Cell:
    def __init__(self, typ, pos, sprite, genome, start_energy, parent):
        self.type = typ
        self.pos = pos
        self.sprite = sprite
        self.genome = genome if genome is not None else self.gen_genome()
        self.energy = start_energy
        self.parent = parent

    def gen_genome(self):
        genome = []
        for i in range(randint(1, GENOME_MAX_LEN)):
            genome.append([randint(1,100) for _ in range(7)])
        return genome

class Sprout(Cell):
    def __init__(self, pos, sprite, genome, start_energy, parent, direction):
        super().__init__('sprout', pos, sprite, genome, start_energy, parent)
        self.direction = direction
        self.step = 0

    def act():
        gene = self.genome[self.step % len(self.genome)]
        self.step += 1
        gene_activation = True
        for i in gene[4:6]:
            pass
        if gene_activation:
            for i in range(0,4):
                child_type = gene[i]/(100/len(cell_types))

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
