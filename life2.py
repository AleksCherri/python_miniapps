from tkinter import *
from random import *
from time import sleep, time

FULLSCREEN = 1
FPS = 60
DRAW_ENERGY = False
DRAW_CELLS = True
PAUSE = False

WIDTH = 10
HEIGHT = 10
GRID = 16

SPAWN_CELLS_LIMIT = 256
GLOBAL_CELLS_LIMIT = 512

ENERGY_TO_GROW = 10
ENERGY_TO_POP = 100
AGE_TO_DIE = 100
S_GEN_LEN = [4, 20]
MUTATE_CHANCE = 0.05

SPAWN_CHANCE = 0.1

typs_energy = [10, -1, -3, -2] #leaf, seed, sprout, sten
# move, spawn, delete
if FULLSCREEN:
    WIDTH = 1920 // GRID
    HEIGHT = 1080 // GRID

cells = [None]*WIDTH*HEIGHT

class Cell:
    def __init__(self, typ, genome, energy, age, color):
        self.typ = typ
        self.genome = genome
        self.energy = energy
        self.age = age
        self.color = color
        self.step = 0

    def applyenergy(self):
        if self.energy <= 255:
            self.energy += typs_energy[self.typ - 1]
        else:
            self.energy = 255

    def shareenergy(self):
        neighbors = []
        pos = cells.index(self)
        x = pos % WIDTH
        y = pos // WIDTH
        ourenergy = self.energy

        target = cells[pos - WIDTH]
        if target is not None and target.genome == self.genome:
            neighbors.append(target)
            ourenergy += target.energy

        target = cells[y*WIDTH + ((x+1) % WIDTH)]
        if target is not None and target.genome == self.genome:
            neighbors.append(target)
            ourenergy += target.energy

        target = cells[(pos + WIDTH) % (HEIGHT*WIDTH)]
        if target is not None and target.genome == self.genome:
            neighbors.append(target)
            ourenergy += target.energy

        target = cells[y*WIDTH + ((WIDTH + x - 1) % WIDTH)]
        if target is not None and target.genome == self.genome:
            neighbors.append(target)
            ourenergy += target.energy

        for cell in neighbors:
            cell.energy = ourenergy / (len(neighbors)+1)
        self.energy = ourenergy / (len(neighbors)+1)

    def dowork(self):
        self.age += 1
        if self.age >= AGE_TO_DIE:
            cells[cells.index(self)] = None
        
        elif self.typ == 1:
            pass

        elif self.typ == 2:
            if self.energy >= ENERGY_TO_POP:
                self.typ = 3
                self.age = 0
                if MUTATE_CHANCE > random():
                    self.mutate()

        elif self.typ == 3:
            if self.energy >= ENERGY_TO_GROW:
                act = self.genome[self.step % len(self.genome)]
                self.step += 1
                action(self, act)
                #if MUTATE_CHANCE > random():
                #    self.mutate()

        else:
            self.shareenergy()

    def mutate(self):
        for i in range(randint(1, 3)):
            ran = randint(1,3)
            if ran <= 2:
                act = randint(1, 3)
                di = randint(1, 4)
                if act == 2:
                    child = randint(1, 4)
                else:
                    child = None
                if ran == 1:
                    self.genome.append([act, di, child])
                else:
                    self.genome[randint(0, len(self.genome)-1)] = [act, di, child]
            elif len(self.genome) > 1:
                self.genome.remove(choice(self.genome))
        self.color = randcolor()

def count_cells():
    k = 0
    for cell in cells:
        if cell is not None:
            k += 1
    return k

def print_data(key):
    print(f'Всего клеток: {count_cells()}')

def toggle_pause(key):
    global PAUSE
    if PAUSE:
        PAUSE = False
    else:
        PAUSE = True

def toggle_drawing(key):
    global DRAW_CELLS
    if DRAW_CELLS:
        DRAW_CELLS = False
    else:
        DRAW_CELLS = True

def toggle_energy(key):
    global DRAW_ENERGY
    if DRAW_ENERGY:
        DRAW_ENERGY = False
    else:
        DRAW_ENERGY = True

def energycolor(energy):
    c = max(min(round(energy), 255), 0)
    return f'#{c:02x}{c:02x}00'

def randcolor():
    return f'#{randint(0, 16777215):06x}'

def action(cell, act):
    pos = cells.index(cell)
    x = pos % WIDTH
    y = pos // WIDTH

    if act[1] == 1:
        target_pos = pos - WIDTH
    elif act[1] == 2:
        target_pos = y*WIDTH + ((x+1) % WIDTH)
    elif act[1] == 3:
        target_pos = (pos + WIDTH) % (HEIGHT*WIDTH)
    else:
        target_pos = y*WIDTH + ((WIDTH + x - 1) % WIDTH)

    if act[0] == 1 and cells[target_pos] is None and count_cells() < GLOBAL_CELLS_LIMIT:
        cell.energy /= 2
        cells[target_pos] = cell
        cells[pos] = Cell(4, cell.genome, cell.energy, 0, cell.color)

    elif act[0] == 2 and cells[target_pos] is None and count_cells() < GLOBAL_CELLS_LIMIT:
        cell.energy /= 2
        cells[target_pos] = Cell(act[2], cell.genome, cell.energy, 0, cell.color)

    elif act[0] == 3 and cells[target_pos] is not None:
        cell.energy += cells[target_pos].energy
        cells[target_pos] = None

def gen_genome():
    genome = []
    for i in range(randint(S_GEN_LEN[0], S_GEN_LEN[1])):
        act = randint(1, 3)
        di = randint(1, 4)
        if act == 2:
            child = choice([1, 2, 4])
        else:
            child = None
        genome.append([act, di, child])
    return genome

def draw_cells():
    canv.delete('all')
    for i in range(len(cells)):
        if cells[i] is not None:
            cell = cells[i]
            if DRAW_ENERGY:
                color = energycolor(cell.energy)
            else:
                color = cell.color
            x = i % WIDTH
            y = i // WIDTH
            
            if cell.typ == 1:
                canv.create_polygon(x*GRID, y*GRID, (x+1)*GRID, y*GRID, (x+0.5)*GRID, (y+1)*GRID, fill = color, outline = '#FFFFFF')
            elif cell.typ == 2:
                canv.create_oval(x*GRID, y*GRID, (x+1)*GRID, (y+1)*GRID, fill = color, outline = '#FFFFFF')
            elif cell.typ == 3:
                canv.create_polygon((x+0.5)*GRID, y*GRID, (x+1)*GRID, (y+0.5)*GRID, (x+0.5)*GRID, (y+1)*GRID, x*GRID, (y+0.5)*GRID, fill = color, outline = '#FFFFFF')
            else:
                canv.create_rectangle(x*GRID, y*GRID, (x+1)*GRID, (y+1)*GRID, fill = color, outline = '#FFFFFF')
    
    canv.update()

def cycle():
    while True:
        #time1 = time()
        if not PAUSE:
            for i in range(len(cells)):
                cell = cells[i]
                if cell is not None:
                    cell.dowork()
                    cell.applyenergy()

                    if cell.energy <= 0:
                        cells[i] = None

            if SPAWN_CHANCE > random():
                if count_cells() < SPAWN_CELLS_LIMIT:
                    spawncell()

        if DRAW_CELLS:
            draw_cells()
        else:
            canv.delete('all')
            canv.update()

        #sleep(max(1/FPS - time() + time1, 0))

def spawncell():
    if cells[randint(0, len(cells)-1)] is None:
        cells[randint(0, len(cells)-1)] = Cell(3, gen_genome(), 255, 0, randcolor())

root = Tk()
root.title('Generation')
root.geometry(f'{WIDTH*GRID+50}x{HEIGHT*GRID+50}')

root.bind('<space>', toggle_energy)
root.bind('<Return>', toggle_drawing)
root.bind('<p>', toggle_pause)
root.bind('<i>', print_data)

canv = Canvas(bg = "black", width = WIDTH*GRID, height = HEIGHT*GRID)
canv.pack(anchor = CENTER, expand = 1)

cycle()
