"""Small Cube scene to verify input, numeric state paths, and rendered pixels."""

import pyxel
from pyxel.cube import Camera, Mat4, Node, Vec3


class Box(Node):
    def on_update(self):
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.transform = self.transform.translate(Vec3.RIGHT)

    def on_draw(self):
        self.box(Mat4.IDENTITY, Vec3(8, 8, 8), 11)


class App:
    def __init__(self):
        pyxel.init(64, 48)
        self.scene = Node()
        self.scene.camera = Camera()
        self.scene.camera.clear_color = 1
        self.scene.camera.transform = Mat4.look_at(Vec3(0, 18, 36), Vec3.ZERO)
        self.box = Box()
        self.scene.add_child(self.box)
        pyxel.run(self.update, self.draw)

    def update(self):
        self.scene.update()

    def draw(self):
        self.scene.draw(0, 0, pyxel.width, pyxel.height)


App()
