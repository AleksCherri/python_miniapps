import arcade
import random

MAP_WIDTH = 1000
MAP_HEIGHT = 1000

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_RISIZABLE = True
SCREEN_FULLSCREEN = False

TPS = 60000
FPS = 60

CELL_COLORS = {
    'sprout':(255,200,0),
    'stem':(150,150,150),
    'leaf':(0,200,0),
    'seed':(200,255,0),
    'root':(200,0,0),
}

class Game(arcade.View):
    def __init__(self):
        super().__init__()
        self.cells = [[None] * MAP_HEIGHT for _ in range(MAP_WIDTH)]
        self.sprite_list = arcade.SpriteList()
        self.cell_texture = arcade.make_soft_square_texture(2, arcade.color.WHITE, outer_alpha=255)
        self.pause = False
        self.start_cell = None
        self.cell_counter = 0

        #Camera settings
        self.camera = arcade.camera.Camera2D()
        self.cam_x, self.cam_y = MAP_WIDTH/2, MAP_HEIGHT/2
        self.cam_speed = 500
        self.camera.position = self.cam_x, self.cam_y
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
        arcade.draw_lbwh_rectangle_filled(-0.5, -0.5, MAP_WIDTH, MAP_HEIGHT, (100,100,100))
        self.sprite_list.draw()

    def on_update(self, delta_time: float):
        #Camera control
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
            if self.start_cell is None:
                cell = Cell('sprout', (random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1)), 255, None, None, None)
                self.start_cell = cell.pos
                self.add_cell(cell)
            pos = self.start_cell
            while pos is not None:
                x,y = pos
                pos = self.cells[x][y].act()

        print(self.cell_counter) if delta_time > 0.003 else None

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

    def add_cell(self, cell):
        x,y = cell.pos
        if self.cells[x][y] is not None:
            return False
        self.cells[x][y] = cell
        sprite = arcade.Sprite(self.cell_texture, scale=0.475)
        sprite.color = CELL_COLORS[cell.type]
        sprite.position = x,y
        self.sprite_list.append(sprite)
        cell.sprite = sprite
        self.cell_counter += 1
        return True

    def remove_cell(self, cell):
        x,y = cell.pos
        if cell.pos == self.start_cell:
            self.start_cell = cell.child
        self.cells[x][y] = None

        if cell.child is not None:
            x,y = cell.child
            self.cells[x][y].parent = cell.parent
        if cell.parent is not None:
            x,y = cell.parent
            self.cells[x][y].child = cell.child

        try:
            self.sprite_list.remove(cell.sprite)
            self.cell_counter -= 1
        except:
            print(cell.pos, cell.type, cell.sprite)

class Cell:
    def __init__(self, typ, pos, energy, parent, child, sprite):
        self.type = typ
        self.pos = pos
        self.energy = energy
        self.parent = parent
        self.child = child
        self.sprite = sprite

    def act(self):
        if self.child is None:
            self.energy /= 2
            child_pos = pos_normalised((self.pos[0]+1, self.pos[1]+random.choice((-1,1))))
            child = Cell('sprout', child_pos, self.energy, self.pos, None, None)
            if game.add_cell(child):
                self.child = child_pos
        else:
            return self.child

def pos_normalised(pos):
    return ((pos[0]+MAP_WIDTH)%MAP_WIDTH, (pos[1]+MAP_HEIGHT)%MAP_HEIGHT)

window = arcade.Window(
    title='Life3.1',
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
