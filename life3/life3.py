import arcade
from random import *

MAP_WIDTH = 1000
MAP_HEIGHT = 1000

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_RISIZABLE = True
SCREEN_FULLSCREEN = False

TPS = 600
FPS = 60

MIN_CELLS = 25
GENOME_MAX_LEN = 100

CELL_MIN_ENERGY = 12
CELL_ENERGY_CONSUMPTION = {'sprout':3,'stem':1,'leaf':1,'root':1,'seed':0}
CELL_ENERGY_GEN = {'leaf':7, 'root':10}
CELL_COLORS = {'sprout':(200,200,200), 'stem':(100,100,100), 'leaf':(100,200,100), 'root':(200,100,100), 'seed':(200,200,100)}
CELL_MUTATE_CHANCE = 0.1

class Game(arcade.View):
    def __init__(self):
        super().__init__()

        self.organic_map = [[0.0] * MAP_HEIGHT for _ in range(MAP_WIDTH)]
        self.map = [[None] * MAP_HEIGHT for _ in range(MAP_WIDTH)]
        self.sprite_list = arcade.SpriteList()
        self.cell_queue = []

        self.camera = arcade.camera.Camera2D()
        self.cam_x, self.cam_y = MAP_WIDTH/2, MAP_HEIGHT/2
        self.camera.position = self.cam_x, self.cam_y
        self.cam_speed = 500
        self.pause = False
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

        dx,dy = 0,0
        for key in self.pressed_keys:
            vx, vy = self.move_binds[key]
            dx += vx
            dy += vy
        if dx != 0 or dy != 0:
            self.cam_x += dx*self.cam_speed*delta_time/self.camera.zoom
            self.cam_y += dy*self.cam_speed*delta_time/self.camera.zoom
            self.camera.position = self.cam_x, self.cam_y

        if not self.pause:
            if len(self.cell_queue) < MIN_CELLS:
                self.add_cell(Sprout(
                    (randint(0,MAP_WIDTH-1),randint(0,MAP_HEIGHT-1)),
                    None, None, 100, 1
                    ), None)

            for pos in self.cell_queue:
                x,y = pos
                self.map[x][y].act()

    def on_key_press(self, symbol, modifiers):
        if symbol in self.move_binds:
            self.pressed_keys.add(symbol)
        if symbol == arcade.key.SPACE:
            self.pause = False if self.pause else True

    def on_key_release(self, symbol, modifiers):
        self.pressed_keys.discard(symbol)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if scroll_y > 0 and self.camera.zoom < 100:
            self.camera.zoom *= 1.1
        elif scroll_y < 0 and self.camera.zoom > 0.1:
            self.camera.zoom /= 1.1

    def add_cell(self, cell, index):
        x,y = ((cell.pos[0]+MAP_WIDTH)%MAP_WIDTH, (cell.pos[1]+MAP_HEIGHT)%MAP_HEIGHT)
        if self.map[x][y] is not None:
            return None
        self.map[x][y] = cell
        self.cell_queue.insert(index, (x,y)) if index is not None else self.cell_queue.append((x,y))
        sprite = arcade.Sprite('sprite.bmp', scale=0.95)
        sprite.color = CELL_COLORS[cell.type]
        sprite.position = x, y
        self.sprite_list.append(sprite)
        cell.sprite = sprite

    def remove_cell(self, cell):
        x,y = (cell.pos[0]%MAP_WIDTH,cell.pos[1]%MAP_HEIGHT)
        if (x,y) not in self.cell_queue:
            return None
        self.map[x][y] = None
        self.organic_map[x][y] += cell.energy
        self.cell_queue.remove((x,y))
        try:
            self.sprite_list.remove(cell.sprite)
        except:
            print(cell.pos, cell.type, cell.sprite)

class Cell:
    def __init__(self, typ, pos, sprite, genome, start_energy):
        self.type = typ
        self.pos = (pos[0]+MAP_WIDTH)%MAP_WIDTH, (pos[1]+MAP_HEIGHT)%MAP_HEIGHT
        self.sprite = sprite
        self.genome = genome if genome is not None else self.gen_genome()
        self.energy = start_energy

    def mutate(self):
        match randint(0,2):
            case 0:
                self.genome.append([randint(1,100) for _ in range(7)]) if len(self.genome) < GENOME_MAX_LEN else None
            case 1:
                self.genome[randint(0,len(self.genome)-1)][randint(0,6)] = randint(1,100)
            case 2:
                self.genome.pop(randint(0,len(self.genome)-1)) if len(self.genome) > 1 else None

    def gen_genome(self):
        genome = []
        for i in range(randint(1, GENOME_MAX_LEN)):
            genome.append([randint(1,100) for _ in range(7)])
        return genome

    def check_for_death(self):
        self.energy -= CELL_ENERGY_CONSUMPTION[self.type]
        if self.energy <= 0:
            game.remove_cell(self)
        return None

class Seed(Cell):
    def __init__(self, pos, sprite, genome, start_energy, direction):
        super().__init__('seed', pos, sprite, genome, start_energy)
        self.direction = direction
        self.step = 0

    def act(self):
        self.step += 1
        #self.check_for_death()
        if self.step >= 50 or self.energy >= 100:
            index = game.cell_queue.index(self.pos)
            game.remove_cell(self)
            game.add_cell(Sprout(
                self.pos, None, self.genome, self.energy, self.direction
                ), index)

class Root(Cell):
    def __init__(self, pos, sprite, genome, start_energy, direction):
        super().__init__('root', pos, sprite, genome, start_energy)
        self.direction = direction

    def act(self):
        self.check_for_death()

class Stem(Cell):
    def __init__(self, pos, sprite, genome, start_energy, directions):
        super().__init__('stem', pos, sprite, genome, start_energy)
        self.directions = directions

    def act(self):
        self.check_for_death()

        x,y = self.pos
        childs = []
        for direction in self.directions:
            dx,dy = ((x+1,y),(x,y+1),(x-1,y),(x,y-1))[direction]
            child = game.map[(dx+MAP_WIDTH)%MAP_WIDTH][(dy+MAP_HEIGHT)%MAP_HEIGHT]
            childs.append(child) if child is not None else None

        if len(childs) == 0:
            game.remove_cell(self)
            return None

        self.energy /= len(childs)+1
        for child in childs:
            child.energy += self.energy

class Leaf(Cell):
    def __init__(self, pos, sprite, genome, start_energy, direction):
        super().__init__('leaf', pos, sprite, genome, start_energy)
        self.direction = calc_dir(direction+2)
        self.step = 0

    def act(self):
        self.step += 1
        self.energy += CELL_ENERGY_GEN['leaf']/(1+self.step*0.01)
        x,y = self.pos
        self.check_for_death()
        
        dx,dy = ((x+1,y),(x,y+1),(x-1,y),(x,y-1))[self.direction]
        dx,dy = (dx+MAP_WIDTH)%MAP_WIDTH,(dy+MAP_HEIGHT)%MAP_HEIGHT
        if game.map[dx][dy] is None:
            game.remove_cell(self)
            return None

        self.energy /= 2
        game.map[dx][dy].energy += self.energy

class Sprout(Cell):
    def __init__(self, pos, sprite, genome, start_energy, direction):
        super().__init__('sprout', pos, sprite, genome, start_energy)
        self.direction = direction
        self.step = 0
        if random() < CELL_MUTATE_CHANCE:
            self.mutate()

    def act(self):
        gene = self.genome[self.step % len(self.genome)]
        self.step += 1
        gene_activation = True
        for i in gene[4:6]:
            pass
        if gene_activation:
            transform_directs = []
            for i in range(-1,3):
                child = cell_types[round(gene[i+1]/100*len(cell_types))-1]
                if self.energy-CELL_ENERGY_CONSUMPTION[self.type] < CELL_MIN_ENERGY or child is None:
                    break
                else:
                    x,y = self.pos
                    direction = calc_dir(self.direction + i)
                    child = child(
                        ((x+1,y),(x,y+1),(x-1,y),(x,y-1))[direction],
                        None, self.genome, CELL_MIN_ENERGY, direction
                        )
                    if child.type == 'sprout':
                        child.step = self.step
                        transform_directs.append(direction)
                    elif child.type == 'seed':
                        transform_directs.append(direction)
                    index = game.cell_queue.index(self.pos)
                    game.add_cell(child, index)
                    self.energy -= CELL_MIN_ENERGY

            if len(transform_directs) > 0:
                index = game.cell_queue.index(self.pos)
                game.remove_cell(self)
                game.add_cell(Stem(
                    self.pos, None, self.genome, self.energy, transform_directs
                    ), index)

        self.check_for_death()

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
