# pyfense_map.py
# contains map class for loading maps and paths associated with it

import pyglet
from pyglet.image.codecs.png import PNGImageDecoder
import cocos
import pyfense_resources


class PyFenseMap(cocos.layer.Layer):
    def __init__(self, levelMap):
        super().__init__()
        self.levelMap = levelMap
        self.loadBackgroundImage()
        self.drawBackgroundImage()

    def loadBackgroundImage(self):
        # TODO: error handling for no image available case!
        # use python's PNGImageDecoder due
        # to segfault causing bug in gdk_pixbuf2
        if(self.levelMap == "lvlcustom"): #if custom image, load new
            backgroundImage = pyfense_resources.loadImage("assets/lvlcustom.png")
        else:
        	backgroundImage = pyfense_resources.background[str(self.levelMap)]
        self.backgroundSprite = cocos.sprite.Sprite(backgroundImage)

    def drawBackgroundImage(self):
        w, h = cocos.director.director.get_window_size()
        self.backgroundSprite.position = w/2, h/2
        self.add(self.backgroundSprite, z=0)
        self.scaleBackgroundToWindow()

    def scaleBackgroundToWindow(self):
        # TODO: keep screen filled with bg image, no matter resize
        # TODO: to eventually allow scrolling, apply "too large" scaling factor
        img_w = self.backgroundSprite.width
        img_h = self.backgroundSprite.height
        imgRatio = img_w / img_h
        screen_w, screen_h = cocos.director.director.get_window_size()
        screenRatio = screen_w / screen_h
        if imgRatio < screenRatio:
            self.scaleRatio = screen_h / img_h
        else:
            self.scaleRatio = screen_w / img_w
        self.backgroundSprite.scale = self.scaleRatio

    def on_draw(self):
        self.scaleBackgroundToWindow()
