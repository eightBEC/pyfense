# pyfense_game.py
# contains PyFenseGame class (scene)
import os
import cocos
from cocos.director import director
from cocos.scene import Scene
from cocos import actions
from pyfense import resources
from pyfense import map
from mapbuilderhud import PyFenseMapBuilderHud
import pickle

root = os.path.dirname(os.path.abspath(__file__))
pathjoin = lambda x: os.path.join(root, x)


class PyFenseMapBuilder(Scene):
    is_event_handler = True

    def __init__(self):
        super().__init__()
        # initialise game grid to store where enemies can walk,
        # towers can be build and where towers are already built
        # one grid cell is 60x60px large (full hd resolution scale)
        # gameGrid can be called by using gameGrid[y][x]
        # key:
        # 0 := no tower can be build, no enemy can walk
        # 1 := no tower can be build, enemy can walk
        # 3 := tower can be build, no enemy can walk
        # 4 := tower has been built, no enemy can walk,
        #      no tower can be build (can upgrade (?))
        self.gameGrid = [[0 for x in range(32)] for x in range(18)]
        self.startTile = [8, 2]
        self.endTile = [9, 29]
        self.movePath = actions.MoveBy((0, 0))
        # self.loadPath()
        # self.levelMapName = "lvl" + str(levelNumber)
        # self.loadMap()
        self._display_hud()
        self._load_backgorund()
        self.on_build_path(210, 510)
        self.on_build_path(1710, 570)

    def on_save(self):
        # Save Path in file and "restart" director to update the Menu
        output = open(pathjoin("data/path.cfg"), "wb")
        pickle.dump(self.gameGrid, output)
        output.close()
        print("save")
        director.pop()

#        scene = Scene()
#        logo = cocos.sprite.Sprite(resources.logo)
#        scene.add(logo, z=2)
#        scene.add(MultiplexLayer(
#            pyfense.MainMenu(),
#            pyfense.LevelSelectMenu(),
#            pyfense.OptionsMenu(),
#            pyfense.ScoresLayer(),
#            pyfense.AboutLayer()),
#            z=1)
#
#        director.director.replace(scene)
    def _load_backgorund(self):
        self.add(map.PyFenseMap("background"), z=0)

    def _display_hud(self):
        self.hud = PyFenseMapBuilderHud()
        self.hud.push_handlers(self)
        self.add(self.hud, z=2)

    def _set_grid_pix(self, x, y, kind):
        if (kind < 0 or kind > 4) and kind != 2:
            print("WRONG GRID TYPE, fix ur shit %d" % kind)
            return
        grid_x = int(x / 60)
        grid_y = int(y / 60)
        self._set_grid(grid_x, grid_y, kind)

    def _set_grid(self, grid_x, grid_y, kind):
        if (kind < 0 or kind > 4) and kind != 2:
            print("WRONG GRID TYPE, fix ur shit")
            return
        self.gameGrid[grid_y][grid_x] = kind

    def _get_grid_pix(self, x, y):
        grid_x = int(x / 60)
        grid_y = int(y / 60)
        # gracefully fail for resolution edge cases
        if grid_x > 31:
            grid_x = 31
        if grid_y > 17:
            grid_y = 17
        return self.gameGrid[grid_y][grid_x]

    def on_build_path(self, x, y):
        if(self._get_grid_pix(x, y) == 0):
            path = cocos.sprite.Sprite(resources.path,
                                       position=(x, y))
            self.add(path)
            self._set_grid_pix(x, y, 2)
        elif(self._get_grid_pix(x, y) == 2):
            path = cocos.sprite.Sprite(resources.grass,
                                       position=(x, y))
            self.add(path)
            self._set_grid_pix(x, y, 3)
        elif(self._get_grid_pix(x, y) == 3):
            nopath = cocos.sprite.Sprite(resources.nopath,
                                         position=(x, y))
            self.add(nopath)
            self._set_grid_pix(x, y, 0)

    def on_user_mouse_motion(self, x, y):
        self.hud.currentCellStatus = self._get_grid_pix(x, y)
