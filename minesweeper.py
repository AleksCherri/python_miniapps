from tkinter import *
from random import *

WIDTH = 20
HEIGHT = 20
GRID = 24
MINE_SPAWN_CHANCE = 0.25

DEBUG = False

colors = ['#7F00FF', '#0000FF', '#007FFF', '#00FF00', '#7FFF00', '#FFDD00', '#FF7F00', '#FF0000']

class Game:
    def __init__(self):

        self.root = Tk()
        self.root.title('Minesweeper')
        self.root.geometry(f'{WIDTH*GRID}x{HEIGHT*GRID}')

        self.root.bind('<Button>', self.click)

        self.canv = Canvas(bg = '#FFFFFF', width = WIDTH*GRID, height = HEIGHT*GRID)
        self.canv.pack(anchor = NW, expand = 1)

        self.gen_map()

        self.root.mainloop()

    def gen_map(self):
        self.map = [[(None if random() > MINE_SPAWN_CHANCE else 'bomb') for i in range(HEIGHT)] for i in range(WIDTH)]
        self.flags = []
        self.bombs = sum(y == 'bomb' for x in self.map for y in x)
        self.gameover = False
        self.on_draw()

    def on_draw(self):
        self.canv.delete('all')
        for x in range(WIDTH):
            for y in range(HEIGHT):
                cell = self.map[x][y]
                if cell is None or cell == 'bomb':
                    self.canv.create_rectangle(x*GRID, y*GRID, (x+1)*GRID, (y+1)*GRID, fill='#AC2007' if cell == 'bomb' and DEBUG else '#ACACAC', outline='#000000')
                elif cell in range(1,9):
                    self.canv.create_text((x+0.5)*GRID, (y+0.5)*GRID, fill=colors[cell], text=cell, font=f'Arial {round(GRID*0.75)} bold')
        for x, y in self.flags:
            self.canv.create_polygon((x+0.15)*GRID, (y+0.4)*GRID, (x+0.85)*GRID, (y+0.15)*GRID, (x+0.85)*GRID, (y+0.65)*GRID, fill='#FF0000', outline='#FFFF00')
            self.canv.create_line((x+0.85)*GRID, y*GRID, (x+0.85)*GRID, (y+1)*GRID, fill='#000000')

    def find_neighbors(self, x, y):
        neighbors = []
        for dx in [-1,0,1]:
            nx = x+dx
            for dy in [-1,0,1]:
                ny = y+dy
                if 0 <= nx <= WIDTH-1 and 0 <= ny <= HEIGHT-1 and not(nx == x and ny == y):
                    neighbors.append((nx,ny))
        return neighbors

    def action(self, x, y):
        neighbors = self.find_neighbors(x,y)
        bombs = sum(1 for x, y in neighbors if self.map[x][y] == 'bomb')
        self.map[x][y] = bombs
        if bombs == 0:
            for x, y in neighbors:
                self.action(x,y) if self.map[x][y] != 0 else None

    def death(self):
        self.canv.delete('all')
        self.canv.create_rectangle(0, 0, WIDTH*GRID, HEIGHT*GRID, fill='#000000')
        percent = round((HEIGHT*WIDTH-self.bombs - sum(y is None for x in self.map for y in x))/(WIDTH*HEIGHT-self.bombs)*100, 2)
        victory = percent >= 100
        self.canv.create_text(WIDTH/2*GRID, HEIGHT/3*GRID, fill='#00FF00' if victory else '#FF0000', font=f'Arial {round(GRID*min(WIDTH, HEIGHT)*0.075)} bold', text="Nice work, you won." if victory else "You're dead\ndon't be surprised.")
        self.canv.create_text(WIDTH/2*GRID, HEIGHT/2*GRID, fill='#00FF00' if victory else '#FF0000', font=f'Arial {round(GRID*min(WIDTH, HEIGHT)*0.045)}', text=f"You've cleared {percent}% of the map.")

        self.gameover = True

    def click(self, event):
        if self.gameover:
            self.gen_map()
            return None
        x, y = (event.x//GRID, event.y//GRID)
        if event.num == 1 and (x,y) not in self.flags:
            cell = self.map[x][y] if 0 <= x <= WIDTH-1 and 0 <= y <= HEIGHT-1 else -1
            if cell == 'bomb':
                self.death()
                return None
            elif cell is None:
                self.action(x,y)
        elif event.num == 3:
            self.flags.append((x,y)) if (x,y) not in self.flags else self.flags.remove((x,y))
        else:
            return None
        self.on_draw()

game = Game()
