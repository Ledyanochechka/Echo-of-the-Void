import arcade
from core import BaseOverlayView


class WinWindow(BaseOverlayView):
    TEXT = "Ты победил!!!!\nQ — выход"
    COLOR = arcade.color.GREEN


class LoseWindow(BaseOverlayView):
    TEXT = "Ты проиграл, анлак\nQ — выход"
    COLOR = arcade.color.RED


class PauseWindow(BaseOverlayView):
    TEXT = "ПАУЗА\nESC — продолжить\nQ — выход"
    FONT_SIZE = 28

    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

    def on_draw(self):
        self.game_view.on_draw()
        super().on_draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view)
        elif key == arcade.key.Q:
            arcade.close_window()


class StartView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.txt = None

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.txt = arcade.Text(
            "Нажмите ENTER для начала игры",
            self.window.width // 2,
            self.window.height // 2,
            arcade.color.YELLOW_ORANGE,
            25,
            anchor_x="center",
            anchor_y="center",
        )

    def on_draw(self):
        self.clear()
        self.txt.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            self.game_view.setup()
            self.window.show_view(self.game_view)
