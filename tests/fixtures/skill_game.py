"""Small game used to verify the skill's documented MCP workflow."""

import random

import pyxel

MODULE_RANDOM = random.randint(0, 1000000)


class App:
    def __init__(self):
        pyxel.init(32, 24)
        self.x = 0
        self.presses = 0
        self.module_random = MODULE_RANDOM
        self.pyxel_random = pyxel.rndi(0, 1000000)
        pyxel.sounds[0].set("C2D2E2R", "tp", "17", "nhq", 10)
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += 1
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.presses += 1

    def draw(self):
        pyxel.cls(1)
        pyxel.rect(self.x, 8, 4, 4, 10)


App()
