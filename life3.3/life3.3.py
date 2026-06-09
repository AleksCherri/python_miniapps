import arcade
from cell_module import *
from json import load as jsload

with open('config.json') as file:
    config = jsload(file)

SCREEN_WIDTH = config['SCREEN_WIDTH']
SCREEN_HEIGHT = config['SCREEN_HEIGHT']
TPS = 1 / config['INIT_TPS_LIMIT']
FPS = 1 / config['INIT_FPS_LIMIT']

MAP_HEIGHT = config['MAP_HEIGHT']
MAP_WIDTH = config['MAP_WIDTH']

CELL_COLORS = {
    Stem: tuple(config['STEM_COLOR']),
    Leaf: tuple(config['LEAF_COLOR']),
    Root: tuple(config['ROOT_COLOR']),
    Seed: tuple(config['SEED_COLOR']),
    Sprout: tuple(config['SPROUT_COLOR']),
    Spore: tuple(config['SPORE_COLOR']),
}

class Game(arcade.View):

    def __init__(self):
        super().__init__()

    def setup(self):
        set_game(self)
        self.map = [[None]*MAP_HEIGHT for _ in range(MAP_WIDTH)]
        self.organic=[[0.0]*MAP_HEIGHT for _ in range(MAP_WIDTH)]
        self.sprite_list = arcade.SpriteList()
        self.cell_list = arcade.SpriteList()

        self.camera = arcade.camera.Camera2D()
        self.camera.position = MAP_WIDTH/2, MAP_HEIGHT/2
        self.camera.zoom = 1.0

        self.pause = True
        self.update_rate = TPS
        self.sun_factor = 1.0
        self.color_mode = 0

        self.sprite_list.append(arcade.SpriteSolidColor(
                MAP_WIDTH, MAP_HEIGHT,
                MAP_WIDTH/2 - 0.5, MAP_HEIGHT/2 - 0.5,
            ))

        self.update_colors()

    def on_draw(self):
        self.camera.use()
        self.clear()
        self.sprite_list.draw()
        self.cell_list.draw()

    def on_update(self, delta_time: float):
        if not self.pause:
            if not self.cell_list:
                self.add_cell(Sprout(
                    randint(0, MAP_WIDTH-1), randint(0, MAP_HEIGHT-1)
                ))

            for cell in self.cell_list[:]:
                cell.mainact()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.camera.drag_by((dx, dy))

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        zoom = self.camera.zoom * 1.1**scroll_y
        self.camera.zoom = clamp(zoom, 1, 100)

    def on_key_press(self, symbol, modifiers):
        match symbol:
            case arcade.key.SPACE:
                self.pause = not self.pause
            case arcade.key.UP:
                self.update_rate /= 2
                window.set_update_rate(self.update_rate)
            case arcade.key.DOWN:
                self.update_rate *= 2
                window.set_update_rate(self.update_rate)

    def add_cell(self, cell):
        x, y = cell.center_x % MAP_WIDTH, cell.center_y % MAP_HEIGHT
        if game.map[x][y] is not None:
            return False

        match self.color_mode:
            case 0:
                cell.color = CELL_COLORS[type(cell)]

        game.map[x][y] = cell
        self.cell_list.append(cell)
        return True

    def update_colors(self):
        match self.color_mode:
            case 0:
                for cell in self.cell_list:
                    cell.color = CELL_COLORS[type(cell)]

def clamp(x, mi, ma):
    return max(min(x, ma), mi)

if __name__ == '__main__':
    window = arcade.Window(
        title='Life 3.3',
        width=SCREEN_WIDTH,
        height=SCREEN_HEIGHT,
        update_rate=TPS,
        draw_rate=FPS,
        )
    game = Game()
    game.setup()
    window.show_view(game)
    arcade.run()
