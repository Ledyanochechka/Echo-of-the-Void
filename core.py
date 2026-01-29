import arcade
from pyglet.graphics import Batch


class BaseOverlayView(arcade.View):
    TEXT = ""
    COLOR = arcade.color.WHITE
    FONT_SIZE = 25


    def __init__(self):
        super().__init__()
        self.batch = None
        self.txt = None
        self.ui_camera = None

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

        self.ui_camera = arcade.camera.Camera2D()
        self.batch = Batch()

        self.txt = arcade.Text(
            self.TEXT,
            0, 0,
            self.COLOR,
            self.FONT_SIZE,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=self.window.width,
            align="center",
            batch=self.batch,
        )

    def on_draw(self):
        self.clear()
        self.ui_camera.use()

        self.txt.x = self.window.width // 2
        self.txt.y = self.window.height // 2 + self.txt.content_height // 2

        self.batch.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.Q:
            arcade.close_window()

