import arcade
from ai_module import *
from random import randint, random
from json import load as jsload
with open('config.json') as file:
    config = jsload(file)

MAP_WIDTH = config['MAP_WIDTH']
MAP_HEIGHT = config['MAP_HEIGHT']

CELL_INIT_ENERGY = config['CELL_INIT_ENERGY']
LEAF_ENERGY_GEN = config['LEAF_ENERGY_GEN']
ROOT_ENERGY_GEN = config['ROOT_ENERGY_GEN']
CELL_MUTATE_CHANCE = config['CELL_MUTATE_CHANCE']
CELL_MUTATE_INIT = config['CELL_MUTATE_INIT']
CELL_MUTATE_MULT = config['CELL_MUTATE_MULT']

dir_offsets = {
    0: (1, 0),
    1: (0, 1),
    2: (-1, 0),
    3: (0, -1),
}

cell_props = (
    (
        arcade.load_texture('leaf_sprite.png'),
        config['LEAF_MAX_AGE'],
        config['LEAF_ENERGY_CONSUMPTION'],
        tuple(config['LEAF_COLOR']),
    ),
    (
        arcade.load_texture('root_sprite.png'),
        config['ROOT_MAX_AGE'],
        config['ROOT_ENERGY_CONSUMPTION'],
        tuple(config['ROOT_COLOR']),
    ),
    (
        arcade.load_texture('stem_sprite.png'),
        config['STEM_MAX_AGE'],
        config['STEM_ENERGY_CONSUMPTION'],
        tuple(config['STEM_COLOR']),
    ),
    (
        arcade.load_texture('seed_sprite.png'),
        config['SEED_MAX_AGE'],
        config['SEED_ENERGY_CONSUMPTION'],
        tuple(config['SEED_COLOR']),
    ),
    (
        arcade.load_texture('spore_sprite.png'),
        config['SPORE_MAX_AGE'],
        config['SPORE_ENERGY_CONSUMPTION'],
        tuple(config['SPORE_COLOR']),
    ),
    (
        arcade.load_texture('sprout_sprite.png'),
        config['SPROUT_MAX_AGE'],
        config['SPROUT_ENERGY_CONSUMPTION'],
        tuple(config['SPROUT_COLOR']),
    ),
)

ai_layers = (
    lua.table_from([10,16,2]), #Seed
    lua.table_from([7,14,2]), #Spore
    lua.table_from([10,16,16,4]), #Sprout
)

class Cell(arcade.Sprite):
    def __init__(self, x, y, direction, energy, team, cid):
        props = cell_props[cid]
        super().__init__(props[0], 0.11, x%MAP_WIDTH, y%MAP_HEIGHT, cdir(direction))

        self.direction = direction
        self.energy = energy
        self.id = cid+1
        self.timer = props[1]
        self.en_con = props[2]
        self.color = props[3]
        self.team = team if team else random()
        self.state = 0 # 0: alive, 1: need update, 2: dead

    def mainact(self):
        self.energy -= self.en_con
        self.timer -= 1
        if self.energy <= 0 or self.timer <= 0:
        #if self.timer <= 0:
            self.state = 2
        if self.state == 2:
            return self.die()
        self.act()

    def die(self):
        game.remove_cell(self)
        self.state = 2

class Leaf(Cell):
    def __init__(self, target, x, y, direction=0, energy=CELL_INIT_ENERGY, team=None):
        direction = (direction + 2) % 4
        super().__init__(x, y, direction, energy, team, 0)
        self.en_gen = LEAF_ENERGY_GEN * self.center_y/MAP_HEIGHT
        self.target = target

    def act(self):
        cell = self.target
        if cell.state == 2:
            self.state = 2
        elif cell.state == 1:
            self.target = cell = game.map[cell.center_x][cell.center_y]
        else:
            cell.energy += self.en_gen * game.sun_factor

class Root(Cell):
    def __init__(self, target, x, y, direction=0, energy=CELL_INIT_ENERGY, team=None):
        direction = (direction + 2) % 4
        super().__init__(x, y, direction, energy, team, 1)
        self.en_gen = ROOT_ENERGY_GEN
        self.target = target

    def act(self):
        cell = self.target
        if cell.state == 2:
            self.state = 2
        elif cell.state == 1:
            self.target = cell = game.map[cell.center_x][cell.center_y]
        else:
            x, y = (self.center_x + randint(-1, 1)) % MAP_WIDTH, (self.center_y + randint(-1, 1)) % MAP_HEIGHT
            prey = game.map[x][y]
            if prey:
                extr_en = min(prey.energy, self.en_gen)
                prey.energy -= extr_en
            else:
                extr_en = min(game.organic[x][y], self.en_gen)
                game.organic[x][y] -= extr_en
            cell.energy += extr_en

class Stem(Cell):
    def __init__(self, targets, x, y, direction, energy=CELL_INIT_ENERGY, team=None):
        super().__init__(x, y, direction, energy, team, 2)
        self.targets = targets

    def act(self):
        n = 1
        for target in self.targets[:]:
            if target.state:
                self.targets.remove(target)
                if target.state == 1:
                    target = game.map[target.center_x][target.center_y]
                    if target:
                        self.targets.append(target)
                        n += 1
            else:
                n += 1

        if n == 1:
            self.state = 2
        else:
            self.energy = se = self.energy / n
            for target in self.targets:
                target.energy += se

class Seed(Cell):
    def __init__(self, x, y, direction=0, energy=CELL_INIT_ENERGY, team=None, genome=None, message=0.0):
        if not genome:
            genome = gen_genome()
        elif random() < CELL_MUTATE_CHANCE:
            team = random()
            genome = [ai_mutate(weights, CELL_MUTATE_MULT) for weights in genome]

        super().__init__(x, y, direction, energy, team, 3)
        self.message = message
        self.genome = genome
        self.weights = genome[0]
        self.ai = AI(ai_layers[0], weights=self.weights, mult_init=CELL_MUTATE_INIT)
        self.surrs = tuple([( (x+dx)%MAP_WIDTH, (y+dy)%MAP_HEIGHT ) for dx, dy in dir_offsets.values()])

    def act(self):
        ids = []
        for x, y in self.surrs:
            cell = game.map[x][y]
            if cell:
                ids.append(cell.id if cell.team == self.team else -cell.id)
            else:
                ids.append(0)

        sx, sy = self.center_x, self.center_y
        spawning, message = self.ai.act(ids + [self.timer, self.direction, self.energy, game.sun_factor, self.message, game.organic[sx][sy]], True)

        if spawning > 0:
            self.state = 1
            cell = Sprout(sx, sy, self.direction, self.energy, self.team, self.genome, message)
            game.cell_list.remove(self)
            game.cell_list.append(cell)
            game.map[sx][sy] = cell

class Spore(Cell):
    def __init__(self, x, y, direction=0, energy=CELL_INIT_ENERGY, team=None, genome=None, message=0.0):
        if not genome:
            genome = gen_genome()
        elif random() < CELL_MUTATE_CHANCE:
            team = random()
            genome = [ai_mutate(weights, CELL_MUTATE_MULT) for weights in genome]

        super().__init__(x, y, direction, energy, team, 4)
        self.message = message
        self.genome = genome
        self.weights = genome[1]
        self.ai = AI(ai_layers[1], weights=self.weights, mult_init=CELL_MUTATE_INIT)

    def act(self):
        sd = self.direction
        dx, dy = dir_offsets[sd]
        sx, sy = self.center_x, self.center_y
        nx, ny = (sx+dx)%MAP_WIDTH, (sy+dy)%MAP_HEIGHT
        cell = game.map[nx][ny]
        if cell:
            cid = cell.id if cell.team == self.team else -cell.id
        else:
            cid = 0

        action, message = self.ai.act([cid, self.timer, sd, self.energy, game.sun_factor, self.message, game.organic[sx][sy]], True)
        action = int(action) % 5
        match action:
            case 1:
                self.direction = sd = (sd+1) % 4
                self.angle = cdir(sd)
            case 2:
                self.direction = sd = (sd-1) % 4
                self.angle = cdir(sd)
            case 3:
                if not cell:
                    self.state = 1
                    self.center_x, self.center_y = nx, ny
                    game.map[nx][ny], game.map[sx][sy] = self, None
            case 4:
                self.state = 1
                cell = Seed(sx, sy, sd, self.energy, self.team, self.genome, message)
                game.cell_list.remove(self)
                game.cell_list.append(cell)
                game.map[sx][sy] = cell

class Sprout(Cell):
    def __init__(self, x, y, direction=0, energy=CELL_INIT_ENERGY, team=None, genome=None, message=0.0):
        if not genome:
            genome = gen_genome()
        elif random() < CELL_MUTATE_CHANCE:
            team = random()
            genome = [ai_mutate(weights, CELL_MUTATE_MULT) for weights in genome]

        super().__init__(x, y, direction, energy, team, 5)
        self.message = message
        self.genome = genome
        self.weights = genome[2]
        self.ai = AI(ai_layers[2], weights=self.weights, mult_init=CELL_MUTATE_INIT)
        self.surrs = tuple([( (x+dx)%MAP_WIDTH, (y+dy)%MAP_HEIGHT ) for dx, dy in dir_offsets.values()])

    def act(self):
        ids = []
        for x, y in self.surrs:
            cell = game.map[x][y]
            if cell:
                ids.append(cell.id if cell.team == self.team else -cell.id)
            else:
                ids.append(0)

        sx, sy, sd, team = self.center_x, self.center_y, self.direction, self.team
        data = self.ai.act(ids + [self.timer, sd, self.energy, game.sun_factor, self.message, game.organic[sx][sy]], True)

        message = data[3]
        genome = [copy_weights(weights) for weights in self.genome]
        targets, feed_targets = [], []
        for d, cid in enumerate(data[:3]):
            cid = int(cid) % sc_len
            if cid:
                direction = (sd + d-1) % 4
                x, y = self.surrs[direction]
                if cid <= 2:
                    cell = spawnable_cells[cid](self, x, y, direction=direction, team=team)
                    if game.add_cell(cell):
                        targets.append(cell)
                else:
                    cell = spawnable_cells[cid](x, y, direction=direction, team=self.team, genome=genome, message=message)
                    if game.add_cell(cell):
                        targets.append(cell)
                        feed_targets.append(cell)

        if targets:
            energy = self.energy / len(targets)+1
            for target in targets:
                target.energy = energy

            cell = Stem(feed_targets, sx, sy, direction=sd, energy=energy, team=team)
            self.state = 1
            game.cell_list.remove(self)
            game.cell_list.append(cell)
            game.map[sx][sy] = cell

copy_weights = lua.eval('''
function(weights)
    local t = {}
    for i, val in pairs(weights) do
        t[i] = val
    end
    return t
end
''')

def gen_genome():
    return [ai_gen_weights(layers, CELL_MUTATE_INIT) for layers in ai_layers]

def cdir(direction):
    return (1-direction)*90

def gameset(g):
    global game
    game = g
game = None

spawnable_cells = {
    1: Leaf,
    2: Root,
    3: Seed,
    4: Spore,
    5: Sprout
}

sc_len = len(spawnable_cells)+1
