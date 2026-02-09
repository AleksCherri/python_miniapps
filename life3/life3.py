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

MIN_CELLS = 10
GENOME_MAX_LEN = 100

CELL_MIN_ENERGY = 12
CELL_ENERGY_CONSUMPTION = {'sprout':3,'stem':1,'leaf':1,'root':1,'seed':2}
CELL_ENERGY_GEN = {'leaf':7, 'root':10}
CELL_COLORS = {'sprout':(200,200,200), 'stem':(100,100,100), 'leaf':(100,200,100), 'root':(200,100,100), 'seed':(200,200,100)}

class Game(arcade.View):
    def __init__(self):
        super().__init__()

        self.organic_map = [[0.0] * MAP_HEIGHT for _ in range(MAP_WIDTH)]
        self.map = [[None] * MAP_HEIGHT for _ in range(MAP_WIDTH)]
        self.sprite_list = arcade.SpriteList()
        self.cell_queue = []

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

    def on_draw(self):
        self.camera.use()
        self.clear()
        self.sprite_list.draw()

    def on_update(self, delta_time: float):
        if len(self.cell_queue) < MIN_CELLS:
            self.add_cell(Sprout(
                (randint(0,MAP_WIDTH-1),randint(0,MAP_HEIGHT-1)),
                None, None, 100, None, 1
                ))

        dx,dy = 0,0
        for key in self.pressed_keys:
            vx, vy = self.move_binds[key]
            dx += vx
            dy += vy
        if dx != 0 or dy != 0:
            self.cam_x += dx*self.cam_speed*delta_time/self.camera.zoom
            self.cam_y += dy*self.cam_speed*delta_time/self.camera.zoom
            self.camera.position = self.cam_x, self.cam_y

        for pos in self.cell_queue:
            x,y = pos
            self.map[x][y].act()

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
        x,y = cell.pos
        if self.map[x][y] is not None:
            return None
        self.map[x][y] = cell
        self.cell_queue.append((x,y))
        sprite = arcade.Sprite('sprite.bmp', scale=0.95)
        sprite.color = CELL_COLORS[cell.type]
        sprite.position = x, y
        self.sprite_list.append(sprite)
        cell.sprite = sprite

    def remove_cell(self, cell):
        x,y = cell.pos
        if (x,y) not in self.cell_queue:
            return None
        self.map[x][y] = cell.energy
        self.cell_queue.remove((x,y))
        self.sprite_list.remove(cell.sprite)

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

class Seed(Cell):
    def __init__(self, pos, sprite, genome, start_energy, parent, direction):
        super().__init__('seed', pos, sprite, genome, start_energy, parent)

    def act(self):
        pass

class Root(Cell):
    def __init__(self, pos, sprite, genome, start_energy, parent, direction):
        super().__init__('root', pos, sprite, genome, start_energy, parent)
        self.direction = direction

    def act(self):
        pass

class Stem(Cell):
    def __init__(self, pos, sprite, genome, start_energy, parent, directions):
        super().__init__('stem', pos, sprite, genome, start_energy, parent)
        self.directions = directions

    def act(self):
        pass

class Leaf(Cell):
    def __init__(self, pos, sprite, genome, start_energy, parent, direction):
        super().__init__('leaf', pos, sprite, genome, start_energy, parent)
        self.direction = calc_dir(direction+2)

    def act(self):
        pass

class Sprout(Cell):
    def __init__(self, pos, sprite, genome, start_energy, parent, direction):
        super().__init__('sprout', pos, sprite, genome, start_energy, parent)
        self.direction = direction
        self.step = 0

    def act(self):
        gene = self.genome[self.step % len(self.genome)]
        self.step += 1
        gene_activation = True
        for i in gene[4:6]:
            pass
        if gene_activation:
            for i in range(-1,3):
                child = cell_types[round(gene[i+1]/100*len(cell_types))-1]
                if self.energy < CELL_MIN_ENERGY or child is None:
                    break
                else:
                    x,y = self.pos
                    direction = calc_dir(self.direction + i)
                    game.add_cell(child(
                        ((x+1,y),(x,y+1),(x-1,y),(x,y-1))[direction],
                        None, self.genome, CELL_MIN_ENERGY, self, direction
                        ))
                    self.energy -= CELL_MIN_ENERGY

        self.energy -= CELL_ENERGY_CONSUMPTION[self.type]
        if self.energy <= 0:
            game.remove_cell(self)

def calc_dir(direction):
    return (direction+4)%4


cell_types = (None,Sprout,Leaf,Root,Seed)
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
