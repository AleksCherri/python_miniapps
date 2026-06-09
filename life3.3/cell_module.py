import arcade
from ai_module import AI
from json import load as jsload
from random import randint, random
from copy import deepcopy

from time import time

with open('config.json') as file:
    config = jsload(file)

MAP_WIDTH = config['MAP_WIDTH']
MAP_HEIGHT = config['MAP_HEIGHT']

CELL_MAX_AGE = config['CELL_MAX_AGE']
CELL_INIT_ENERGY = config['CELL_INIT_ENERGY']
LEAF_ENERGY_GEN = config['LEAF_ENERGY_GEN']
CELL_MUTATE_CHANCE = config['CELL_MUTATE_CHANCE']
CELL_MUTATE_INIT = 10.0

stem_texture = arcade.load_texture('stem_sprite.png')
leaf_texture = arcade.load_texture('leaf_sprite.png')
root_texture = arcade.load_texture('root_sprite.png')
seed_texture = arcade.load_texture('seed_sprite.png')
sprout_texture = arcade.load_texture('sprout_sprite.png')
spore_texture = arcade.load_texture('spore_sprite.png')

dir_offsets = {
    0: (1, 0),
    1: (0, 1),
    2: (-1, 0),
    3: (0, -1),
}

class Cell(arcade.Sprite):
    def __init__(self, x, y, direction, energy, genome_hash, texture):
        if not genome_hash:
            genome_hash = random()
        super().__init__(texture, 0.11, x%MAP_WIDTH, y%MAP_HEIGHT, (1-direction)*90)
        self.direction = direction
        self.energy = energy
        self.genome_hash = genome_hash
        self.age = 0

    def mainact(self):
        self.act() if self.age else None

        self.energy -= 1
        self.age += 1
        if self.energy <= 0 or self.age > CELL_MAX_AGE:
            return self.die()

    def die(self):
        game.organic[self.center_x][self.center_y] += self.energy
        self.remove_from_sprite_lists()
        game.map[self.center_x][self.center_y] = None
        del self

class Stem(Cell):
    def __init__(self, x, y, direction=0, energy=CELL_INIT_ENERGY, genome_hash=None, texture=stem_texture):
        super().__init__(x, y, direction, energy, genome_hash, texture)

    def act(self):
        feeding = set()
        ln = 1
        for x, y in self.outpos[:]:
            cell = game.map[x][y]
            if isinstance(cell, (Stem, Sprout, Seed)):
                feeding.add(cell)
                ln += 1
            else:
                self.outpos.remove((x,y))

        if ln > 1:
            self.energy /= ln
            for cell in feeding:
                cell.energy += self.energy
        else:
            self.die()

class Leaf(Cell):
    def __init__(self, x, y, direction=0, energy=CELL_INIT_ENERGY, genome_hash=None, texture=leaf_texture):
        super().__init__(x, y, direction, energy, genome_hash, texture)
        self.en_gen = LEAF_ENERGY_GEN
        dx, dy = dir_offsets[direction]
        self.feed_pos = (x+dx)%MAP_WIDTH, (y+dy)%MAP_HEIGHT

    def act(self):
        self.energy += 1
        x, y = self.feed_pos
        cell = game.map[x][y]
        if cell:
            cell.energy += self.en_gen
        else:
            self.die()

class Root(Cell):
    def __init__(self, x, y, direction=0, energy=CELL_INIT_ENERGY, genome_hash=None, texture=root_texture):
        super().__init__(x, y, direction, energy, genome_hash, texture)
        self.en_gen = ROOT_ENERGY_GEN
        dx, dy = dir_offsets[direction]
        self.feed_pos = (x+dx)%MAP_WIDTH, (y+dy)%MAP_HEIGHT

    def act(self):
        self.energy += 1
        x, y = self.feed_pos
        cell = game.map[x][y]
        if cell:
            dx, dy = self.center_x + randint(-1, 1), self.center_y + randint(-1, 1)
            extr_en = min(game.organic[dx][dy], self.en_gen)
            game.organic[dx][dy] -= extr_en
            cell.energy += extr_en
        else:
            self.die()

class Seed(Cell):
    def __init__(self, x, y, direction=0, energy=CELL_INIT_ENERGY, genome_hash=None, ai=None, texture=seed_texture, message=0):
        super().__init__(x, y, direction, energy, genome_hash, texture)
        self.ai = ai if ai else AI(9, 2, [16])
        self.genome = genome if genome else [
            [node[:] for node in self.ai.nodes],
            [node[:] for node in AI(9, 4, [16]).nodes],
            [node[:] for node in AI(6, 4, [12], mult_init=CELL_MUTATE_INIT).nodes]
            ]
        self.message = message

        self.surpos = tuple([ ((x+dx)%MAP_WIDTH, (y+dy)%MAP_HEIGHT) for dx, dy in dir_offsets.values() ])

    def act(self):
        output_data = self.ai.act(
            [
            self.energy,
            self.age,
            self.direction,
            game.sun_factor,
            self.message,
            ] + gen_ids(self.surpos)
        )
        print(output_data, self)

class Sprout(Cell):
    def __init__(self, x, y, direction=0, energy=CELL_INIT_ENERGY, genome_hash=None, ai=None, genome=None, message=0, texture=sprout_texture):
        super().__init__(x, y, direction, energy, genome_hash, texture)
        self.ai = ai if ai else AI(9, 4, [16], mult_init=CELL_MUTATE_INIT)
        self.genome = genome if genome else [
            [node[:] for node in AI(9, 2, [16], mult_init=CELL_MUTATE_INIT).nodes],
            [node[:] for node in self.ai.nodes],
            [node[:] for node in AI(6, 4, [12], mult_init=CELL_MUTATE_INIT).nodes]
            ]
        self.message = message

        self.surpos = tuple([ ((x+dx)%MAP_WIDTH, (y+dy)%MAP_HEIGHT) for dx, dy in dir_offsets.values() ])

    def act(self):
        input_data = [
            self.energy,
            self.age,
            self.direction,
            game.sun_factor,
            self.message,
            ] + gen_ids(self.surpos)
        print(self.ai.layers, input_data)
        output_data = self.ai.act(
            input_data
        )

        childs = set()
        outpos = []
        for i, cid in enumerate(output_data[:3]):
            cid = int(cid) % sc_len
            direction = (self.direction + i-1)%4
            x, y = self.surpos[direction]
            if cid and game.map[x][y] is None:
                if cid < 3:
                    direction = (direction+2)%4

                if cid > 2:
                    message = output_data[3]
                    inp, outp, midl = cell_ais[cid]
                    ai = AI(inp, outp, [midl], nodes=[node[:] for node in self.genome[cid-3]])
                    if random() < CELL_MUTATE_CHANCE:
                        ai.mutate()
                        genome_hash = random()
                    else:
                        genome_hash = self.genome_hash
                    cell = spawnable_cells[cid](
                            x, y, direction=direction, genome_hash=genome_hash, ai=ai
                        ) 
                    outpos.append((x,y))

                else:
                    cell = spawnable_cells[cid](
                            x, y, direction=direction, genome_hash=self.genome_hash,
                        )

                childs.add(cell)
                game.add_cell(cell)

        if childs:
            self.energy /= len(childs)+1
            for child in childs:
                child.energy = self.energy

            new_self = Stem(self.center_x, self.center_y, self.direction, self.energy, self.genome_hash)
            new_self.outpos = outpos
            self.die()
            game.add_cell(new_self)

class Spore(Cell):
    def __init__(self, x, y, direction=0, energy=CELL_INIT_ENERGY, genome_hash=None, ai=None, texture=spore_texture, message=0):
        super().__init__(x, y, direction, energy, genome_hash, texture)
        self.ai = ai if ai else AI(6, 4, [12])
        self.genome = genome if genome else [
            [node[:] for node in AI(9, 2, [16], mult_init=CELL_MUTATE_INIT).nodes],
            [node[:] for node in AI(9, 4, [16]).nodes],
            [node[:] for node in self.ai.nodes]
            ]
        self.message = message

    def act(self):
        pass

def gen_ids(surpos):
    ids = []
    for x, y in surpos:
        cell = game.map[x][y]
        ids.append(
            (cell_ids[type(cell)] * (1 if cell.genome_hash == self.genome_hash else -1)) if cell else 0
        )
    return ids

game = None
def set_game(g):
    global game
    game = g

cell_ids = {
    Stem: 1,
    Leaf: 2,
    Root: 3,
    Seed: 4,
    Sprout: 5,
    Spore: 6,
}

cell_ais = {
    4: [9, 2, 16],
    5: [9, 4, 16],
    6: [6, 4, 12]
}

spawnable_cells = {
    1: Leaf,
    2: Root,
    3: Seed,
    4: Sprout,
    5: Spore,
}

sc_len = len(spawnable_cells)+1
