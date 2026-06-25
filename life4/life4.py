import arcade
from cell_module import *
from math import sin, pi
from json import load as jsload
with open('config.json') as file:
    config = jsload(file)

SCREEN_WIDTH = config['SCREEN_WIDTH']
SCREEN_HEIGHT = config['SCREEN_HEIGHT']
TPS = 1 / config['INIT_TPS_LIMIT']
FPS = 1 / config['INIT_FPS_LIMIT']

MAP_HEIGHT = config['MAP_HEIGHT']
MAP_WIDTH = config['MAP_WIDTH']

DAY_DURATION = config['DAY_DURATION']

pi2 = pi*2

class Game(arcade.View):
    def __init__(self):
        super().__init__()

    def setup(self):
        self.map = [[None]*MAP_HEIGHT for _ in range(MAP_WIDTH)]
        self.organic = [[0.0]*MAP_HEIGHT for _ in range(MAP_WIDTH)]
        self.sprite_list = arcade.SpriteList()
        self.cell_list = arcade.SpriteList()

        self.camera = arcade.camera.Camera2D()
        self.camera.position = MAP_WIDTH/2, MAP_HEIGHT/2
        self.camera.zoom = 1.0

        self.pause = True
        self.step = 0
        self.update_rate = TPS
        self.color_mode = 0
        self.sun_factor = 0.5

        self.background = arcade.SpriteSolidColor(
                MAP_WIDTH, MAP_HEIGHT,
                MAP_WIDTH/2 - 0.5, MAP_HEIGHT/2 - 0.5,
            )
        self.sprite_list.append(self.background)

    def on_draw(self):
        self.camera.use()
        self.clear()
        self.background.color = tuple([int(255 * self.sun_factor) for _ in range(3)])
        self.sprite_list.draw()
        self.cell_list.draw()

    def on_update(self, delta_time):
        if not self.pause:
            #if random() < 0.1:
            if not self.cell_list:
                self.add_cell(Sprout(
                    randint(0, MAP_WIDTH-1), randint(0, MAP_HEIGHT-1)
                ))
            self.sun_factor = (sin(pi2 * self.step/DAY_DURATION)+1)/2
            self.step += 1
            for cell in self.cell_list[:]:
                cell.mainact()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.camera.drag_by((dx, dy))

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        zoom = self.camera.zoom * 1.1**scroll_y
        self.camera.zoom = clamp(zoom, 1, 100)

    def on_mouse_press(self, x, y, button, modifiers):
        cx, cy = self.camera.position
        zoom = self.camera.zoom
        x = round(cx + (x - SCREEN_WIDTH/2)/zoom)
        y = round(cy + (y - SCREEN_HEIGHT/2)/zoom)
        try: cell = game.map[x][y]
        except: return
        if not cell:
            print(x,y)
        else:
            match button:
                case 1:
                    print(type(cell), cell.team, cell.energy, x, y)
                case 4:
                    cell.state = 2

    def on_key_press(self, symbol, modifiers):
        #print(symbol)
        match symbol:
            case 32:
                self.pause = not self.pause
            case 65362:
                self.update_rate /= 2
                window.set_update_rate(self.update_rate)
            case 65364:
                self.update_rate *= 2
                window.set_update_rate(self.update_rate)

    def add_cell(self, cell):
        x, y = cell.center_x, cell.center_y
        if self.map[x][y]:
            return False
        self.map[x][y] = cell
        self.cell_list.append(cell)
        return True

    def remove_cell(self, cell):
        x, y = cell.center_x, cell.center_y
        if self.map[x][y]:
            self.map[x][y] = None
            self.cell_list.remove(cell)
            self.organic[x][y] += cell.energy
            return True
        else:
            return False

def clamp(x, mi, ma):
    return max(min(x, ma), mi)

if __name__ == '__main__':
    window = arcade.Window(
        title='Life 4',
        width=SCREEN_WIDTH,
        height=SCREEN_HEIGHT,
        update_rate=TPS,
        draw_rate=FPS,
        )
    game = Game()
    gameset(game)
    game.setup()
    window.show_view(game)
    arcade.run()
