"""
pyfense_enemy.py
contains PyFenseEnemy class
"""

import cocos
import pyglet
from cocos import sprite
from cocos import actions
import pyfense_resources


class PyFenseEnemy(sprite.Sprite):
    def __init__(self, enemyname, lvl, wave, path):
        # TODO: Different assets and values for stronger enemies
        # to be loaded from textfile
        self.attributes = pyfense_resources.enemy[enemyname]
        self.currentPos = (150, 525)
        texture = self.attributes["image"]
        super(PyFenseEnemy, self).__init__(texture,
                                           position=self.currentPos,
                                           scale=1)
        self.path = path
        self.healthPoints = self.attributes["maxhealth"]
        self.healthBar = self.drawHealthBar()
        self.move(lvl)

    def move(self, lvl):
        self.do(self.path)
        self.healthBar.do(self.path)

    def drawHealthBar(self):
        self.healthBarWidth = 50
        self.bar_x = self.x - self.healthBarWidth / 2
        self.bar_y = self.y + self.height / 2 + 20
        self.healthBar = cocos.draw.Line((self.bar_x, self.bar_y),
                                         (self.bar_x + self.healthBarWidth,
                                          self.bar_y),
                                         (0, 237, 55, 0), 3)
        # self.healthBar.set_endcap('BUTT_CAP') -> cam be changed by altering
        # the ending sprite which cocos.draw loads
        return self.healthBar

    def updateHealthBar(self):
        self.healthBar.color = (0, 237, 55, 255)
        self.healthBar.end = (self.bar_x + self.healthBarWidth *
                              (self.healthPoints/self.attributes["maxhealth"]),
                              self.bar_y)
