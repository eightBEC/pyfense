"""
 pyfense_entities.py
contains the layer on which all enemies and towers are placed (layer)
"""
import pyglet
from pyglet.window import key
from pyglet import clock

import cocos
from cocos.director import director

# import pyfense_tower
import pyfense_enemy
import pyfense_projectile
# import pyfense_hud
from pyfense_pause import PyFensePause
import pyfense_resources
import pyfense_particles
import pyfense_highscore
import math


class PyFenseEntities(cocos.layer.Layer, pyglet.event.EventDispatcher):
    is_event_handler = True

    def __init__(self, path, startTile):
        super().__init__()
        self.enemies = []
        self.spawnedEnemies = 0
        self.diedEnemies = 0
        self.towers = []
        self.projectiles = []
        self.schedule(self.update)
        self.path = path
        self.startTile = startTile
        self.wavequantity = len(pyfense_resources.waves)
        self.enemieslength = 0
        self.polynomial2 = 0  # quadratic
        self.polynomial1 = 2  # linear
        self.polynomial0 = -(self.polynomial1 - 1)  # offset
        self.enemyHealthFactor = 1

        # update runs every tick
    def update(self, dt):
        self.hasEnemyReachedEnd()

    def nextWave(self, waveNumber):
        self.modulo_wavenumber = (waveNumber-1) % self.wavequantity+1
        self.enemy_list = pyfense_resources.waves[self.modulo_wavenumber]
        self.spawnedEnemies = 0
        self.diedEnemies = 0
        self.enemyHealthFactor = math.floor((waveNumber - 1) /
                                            self.wavequantity) + 1
        self.multiplier = ((self.polynomial2 * (self.enemyHealthFactor**2)) +
                           (self.polynomial1 * self.enemyHealthFactor) +
                           self.polynomial0)
        if self.wavequantity-self.modulo_wavenumber == 1:
            self.showWarning()
        self.enemieslength = len(self.enemy_list)
        self.schedule_interval(self.addEnemy, 0.1, self.startTile, self.path,
                               self.enemy_list, self.multiplier)

    def showWarning(self):
        self.warningLabel = cocos.text.Label(
            'Enemies will get stronger in 2 Waves!!!',
            font_name='Times New Roman', font_size=32,
            anchor_x='center', anchor_y='center', color=(255, 0, 0, 255))
        w, h = cocos.director.director.get_window_size()
        self.warningLabel.position = w / 2, h - 100
        self.add(self.warningLabel)
        blinkaction = cocos.actions.Blink(4, 8)
        self.warningLabel.do(blinkaction)
        clock.schedule_once(lambda dt: self.remove(self.warningLabel), 15)

    def buildTower(self, tower):
        tower.push_handlers(self)
        self.towers.append(tower)
        self.add(tower, z=2)
        return tower.attributes["cost"]

    def getTowerAt(self, position):
        for tower in self.towers:
            if tower.position == position:
                return tower

    def removeTower(self, position):
        tower = self.getTowerAt(position)
        self.remove(tower)
        self.towers.remove(tower)
        return tower.attributes["cost"]

    def on_projectile_fired(self, tower, target, projectileimage, towerNumber,
                            rotation, projectileVelocity, damage):
        projectile = pyfense_projectile.PyFenseProjectile(tower, target,
                                                          projectileimage,
                                                          towerNumber,
                                                          rotation,
                                                          projectileVelocity,
                                                          damage)
        self.projectiles.append(projectile)
        projectile.push_handlers(self)
        self.add(projectile, z=1)
        duration = 80 / projectileVelocity
        clock.schedule_once(lambda dt: self.changeZ(projectile, 1, 4), duration)

    def changeZ(self, cocosnode, z_before, z_after):
        if (z_before, cocosnode) in self.children:
            self.remove(cocosnode)
            self.add(cocosnode, z_after)

    def on_enemy_hit(self, projectile, target, towerNumber):
        explosion = eval('pyfense_particles.Explosion' +
                         str(towerNumber) + '()')
        explosion.position = target.position
        self.add(explosion, z=5)
        pyglet.clock.schedule_once(lambda dt, x: self.remove(x), 0.5,
                                   explosion)
        target.healthPoints -= projectile.damage
        self.remove(projectile)
        self.projectiles.remove(projectile)
        target.updateHealthBar()
        if target in self.enemies and target.healthPoints <= 0:
            self.remove(target.healthBarBackground)
            self.remove(target.healthBar)
            self.remove(target)
            self.enemies.remove(target)
            deathAnimation = pyfense_particles.Death()
            deathAnimation.position = target.position
            self.add(deathAnimation, z=5)
            pyglet.clock.schedule_once(lambda dt, x: self.remove(x), 0.5,
                                       deathAnimation)
            self.diedEnemies += 1
            self.dispatch_event('on_enemy_death', target)
            self.isWaveFinished()

    def isWaveFinished(self):
        if self.spawnedEnemies == self.enemieslength:
            # self.unschedule(self.addEnemy)
            if self.diedEnemies == self.spawnedEnemies:
                self.dispatch_event('on_next_wave')

    def addEnemy(self, dt, startTile, path, enemylist, multiplier):
        self.unschedule(self.addEnemy)
        position = startTile
        enemy = pyfense_enemy.PyFenseEnemy(position,
                                           enemylist[self.spawnedEnemies][0],
                                           enemylist[self.spawnedEnemies][1],
                                           1, path, multiplier)
        self.enemies.append(enemy)
        self.spawnedEnemies += 1
        self.add(enemy, z=3)
        self.add(enemy.healthBarBackground, z=6)
        self.add(enemy.healthBar, z=7)
        if self.spawnedEnemies != self.enemieslength:
            self.schedule_interval(self.addEnemy,
                                   self.enemy_list[self.spawnedEnemies-1][2],
                                   self.startTile, self.path,
                                   self.enemy_list, self.multiplier)
        self.isWaveFinished()

    # Removes enemy from entity when no action is running,
    # ie the enemy has reached
    def hasEnemyReachedEnd(self):
        if self.enemies and not self.enemies[0].actions:
            self.dispatch_event('on_enemy_reached_goal')
            self.remove(self.enemies[0])
            self.remove(self.enemies[0].healthBar)
            self.remove(self.enemies[0].healthBarBackground)
            self.enemies.remove(self.enemies[0])
            self.diedEnemies += 1
            self.isWaveFinished()

    # Overrides the Esc key and quits the game on "Q"
    def on_key_press(self, k, m):
        if k == key.ESCAPE:
            director.push(PyFensePause())
            return True
        if k == key.Q:
            director.replace(pyfense_highscore.PyFenseLost())

PyFenseEntities.register_event_type('on_next_wave')
PyFenseEntities.register_event_type('on_enemy_death')
PyFenseEntities.register_event_type('on_enemy_reached_goal')
