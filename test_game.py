# Test for pyfense_tower, to be tested with py.test

import unittest
import cocos
from cocos.director import director
import pyglet

import pyfense_game



settings = {
	"window": {
		"width": 1920,
		"height": 1080,
		"caption": "PyFense",
		"vsync": True,
		"fullscreen": False,
		#ATTENTION: misspelling intentional, pyglet fcked up
		"resizable": True
	}, 
	"world": {
		"gameSpeed": 1.0
	},
	"player": {
		"currency": 200	
	},
	"general": {
		"showFps" : True
	}
}



class TestGame(unittest.TestCase):

	def test_getPositionFromGrid(self):
		director.init(**settings['window'])
		
		
		startTile = [8,2]
		result = pyfense_game.PyFenseGame.getPositionFromGrid(self, startTile)
		actualResult = (150, 510)
		self.assertEqual(result, actualResult)
		
	
if __name__ == '__main__':
	unittest.main()